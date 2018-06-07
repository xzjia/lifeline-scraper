import os
import json
import time
from datetime import timedelta, date
import requests

API_KEY = os.environ['NYT_API_KEY']
ARTICLE_SEARCH_EP = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
# ARTICLE_SEARCH_EP = 'http://localhost:8080'


def format_date(date_object):
    return date_object.strftime('%Y%m%d')


def get_one_batch(target_date, page_number=0):
    end_date = target_date + timedelta(days=1)
    payload = {
        'api-key': API_KEY,
        'begin_date': format_date(target_date),
        'end_date': format_date(end_date),
        'page': page_number,
        'fq': 'print_page:1'
    }
    return requests.get(ARTICLE_SEARCH_EP, params=payload).json()


def get_one_day(target_date):
    result = []
    one_batch = get_one_batch(target_date)
    num_pages = one_batch['response']['meta']['hits'] // 10
    current_page = 0
    while (current_page < num_pages):
        try:
            print('Processing for {}, progress of pages: {}/{}'.format(
                format_date(target_date), current_page, num_pages-1))
            current_page += 1
            result.extend(one_batch['response']['docs'])
            time.sleep(0.5)
            one_batch = get_one_batch(target_date, current_page)
        except:
            print(
                'Something unexpected happened and returning the results up to this point')
            return result
    return result


def process_one_day(year, month, day):
    one_day = date(year, month, day)
    result = get_one_day(one_day)
    with open('nyt/archive/{}.json'.format(format_date(one_day)), 'w') as outfile:
        json.dump(result, outfile, indent=2)


def main():
    # for single_date in range(20, 28):
        # process_one_day(2018, 5, single_date)
    process_one_day(2018, 5, 5)


if __name__ == '__main__':
    main()
