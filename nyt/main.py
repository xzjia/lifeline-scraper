import os
import json
import time
from datetime import timedelta, date
import requests

ARTICLE_SEARCH_EP = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'


class NYT(object):
    def __init__(self, year_start, month_start, day_start, year_end, month_end, day_end, path_prefix):
        self.current_key_index = 0
        self.api_key_pool = os.environ['NYT_API_KEYS'].split('_')
        self.error_count = 0

        self.start_date = date(year_start, month_start, day_start)
        self.end_date = date(year_end, month_end, day_end)

        while self.start_date <= self.end_date:
            self.process_one_day(self.start_date, path_prefix)
            self.start_date = self.start_date + timedelta(days=1)

    def format_date(self, date_object, with_hyphen=False):
        if with_hyphen:
            return date_object.strftime('%Y-%m-%d')
        return date_object.strftime('%Y%m%d')

    def remove_duplicate(self, event_list):
        seen_article = set()
        result = []
        for event in event_list:
            title = event['headline']['print_headline']
            if title in seen_article:
                continue
            else:
                result.append(event)
                seen_article.add(title)
        return result

    def process_one_day(self, date, path_prefix):
        result = self.get_one_day(date)
        result = self.remove_duplicate(result)
        if len(result) > 0:
            with open('{}/{}.json'.format(path_prefix, self.format_date(date, with_hyphen=True)), 'w') as outfile:
                json.dump(result, outfile, indent=2)
        else:
            print('***** No data for {} so skipping... '.format(self.format_date(date)))

    def get_one_day(self, target_date):
        result = []
        one_batch = self.get_one_batch(target_date)
        num_pages = one_batch['response']['meta']['hits'] // 10 + 1
        current_page = 0
        while (current_page < num_pages):
            try:
                print('Processing for {}, progress of pages: {}/{}'.format(
                    self.format_date(target_date), current_page+1, num_pages))
                current_page += 1
                result.extend(one_batch['response']['docs'])
                time.sleep(1)
                one_batch = self.get_one_batch(
                    target_date, page_number=current_page)
            except:
                print(
                    'Something unexpected happened and returning the results up to this point')
                return result
        return result

    def get_one_batch(self, target_date, page_number=0):
        end_date = target_date + timedelta(days=1)
        payload = {
            'api-key': self.api_key_pool[self.current_key_index],
            'begin_date': self.format_date(target_date),
            'end_date': self.format_date(end_date),
            'page': page_number,
            'fq': 'print_page:1'
        }
        raw_response = requests.get(ARTICLE_SEARCH_EP, params=payload).json()
        while 'response' not in raw_response:
            self.error_count += 1
            if self.error_count == 10:
                print('***** Current key burned out, switching to next one and retrying... {} *****'.format(
                    self.format_date(target_date)))
                self.current_key_index += 1
                self.error_count = 0
                if self.current_key_index == len(self.api_key_pool):
                    self.current_key_index = 0
            print("API Rate exceed error, sleep 2 seconds and retry: {}".format(
                self.format_date(target_date)))
            time.sleep(2)
            payload['api-key'] = self.api_key_pool[self.current_key_index]
            raw_response = requests.get(
                ARTICLE_SEARCH_EP, params=payload).json()
        self.error_count = 0
        return raw_response


def main():
    # n = NYT(1990, 1, 1, 2013, 12, 31, 'nyt/archive')
    n = NYT(2018, 6, 7, 2018, 6, 12, 'nyt/archive')


if __name__ == '__main__':
    main()
