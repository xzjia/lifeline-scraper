import os
import json
import time
from datetime import timedelta, date
import requests


ARTICLE_SEARCH_EP = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
ARCHIVE_EP = 'https://api.nytimes.com/svc/archive/v1/{}/{}.json'


class NYT(object):
    def __init__(self, year_start, month_start, day_start, year_end, month_end, day_end, path_prefix, granularity):
        self.current_key_index = 0
        self.api_key_pool = os.environ['NYT_API_KEYS'].split('_')
        self.error_count = 0

        if granularity == 'day':
            self.start_date = date(year_start, month_start, day_start)
            self.end_date = date(year_end, month_end, day_end)
            while self.start_date <= self.end_date:
                self.process_one_day(self.start_date, path_prefix)
                self.start_date = self.start_date + timedelta(days=1)
        elif granularity == 'month':
            all_date = [date(m//12, m % 12+1, 1)
                        for m in range(year_start*12+month_start-1, year_end*12+month_end)]
            for one_date in all_date:
                self.process_one_month(
                    one_date.year, one_date.month, path_prefix)

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

    def store_as_json(self, result, date, path_prefix):
        if len(result) > 0:
            with open('{}/{}.json'.format(path_prefix, self.format_date(date, with_hyphen=True)), 'w') as outfile:
                json.dump(result, outfile, indent=2)
                print('***** Successfully done for {} , {} entries in total'.format(
                    self.format_date(date), len(result)))
        else:
            print('***** No data for {} so skipping... '.format(self.format_date(date)))

    def process_one_day(self, date, path_prefix):
        result = self.get_one_day(date)
        result = self.remove_duplicate(result)
        self.store_as_json(result, date, path_prefix)

    def filter_one_month(self, result):
        all_events = result['response']['docs']
        return list(filter(lambda x: x['print_page'] in [1, '1'] if 'print_page' in x else False, all_events))

    def process_one_month(self, year, month, path_prefix):
        result = self.get_one_month(year, month)
        result = self.filter_one_month(result)
        self.store_as_json(result, date(year, month, 1), path_prefix)

    def get_one_month(self, year, month):
        payload = {
            'api-key': self.api_key_pool[self.current_key_index]
        }
        raw_response = requests.get(ARCHIVE_EP.format(
            year, month), params=payload).json()
        while 'response' not in raw_response:
            raw_response = self.retry_api_call(ARCHIVE_EP, payload)
        return raw_response

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

    def retry_api_call(self, endpoint, payload):
        self.error_count += 1
        if self.error_count == 10:
            print('***** Current key burned out, switching to next one and retrying... ')
            self.current_key_index += 1
            if self.current_key_index == len(self.api_key_pool):
                self.current_key_index = 0
            self.error_count = 0
        print("API Rate exceed error, sleep 2 seconds and retry")
        time.sleep(2)
        payload['api-key'] = self.api_key_pool[self.current_key_index]
        return requests.get(endpoint, params=payload).json()

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
            raw_response = self.retry_api_call(ARTICLE_SEARCH_EP, payload)
        self.error_count = 0
        return raw_response


def main():
    # n = NYT(1990, 1, 1, 2013, 12, 31, 'nyt/archive')
    # n = NYT(2018, 6, 7, 2018, 6, 12, 'nyt/archive', 'day')
    n = NYT(2018, 6, 16, 2018, 6, 17, 'nyt/archive', 'day')


if __name__ == '__main__':
    main()
