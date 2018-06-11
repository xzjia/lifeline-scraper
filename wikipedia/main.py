import json
import re
from datetime import datetime
from requests_html import HTMLSession


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_date_links():
    session = HTMLSession()
    r = session.get(
        'https://en.wikipedia.org/wiki/List_of_historical_anniversaries')
    nav = r.html.find('.navbox-list')
    return set.union(*map(lambda one_month: one_month.absolute_links, nav))


def process_events(events_list, date_without_year, postfix=''):
    def event_2_dict(event):
        if event.find('ul'):
            print('{}Error: Nested list of {} {} **{}** '.format(bcolors.FAIL, date_without_year,
                                                                 bcolors.ENDC, event.text))
            return None
        splitted = re.split('-|–|－', event.text)
        if len(splitted) < 2:
            print('{}Error: No hyphen of {} {} **{}** '.format(bcolors.FAIL, date_without_year,
                                                               bcolors.ENDC, event.text))
            return None
        result = {}
        year = splitted[0].strip()
        desc = splitted[1].strip()
        result['date'] = year + '-' + date_without_year
        result['title'] = desc + postfix
        result['text'] = event.html
        result['link'] = list(event.absolute_links)
        return result
    return filter(lambda e: e, map(event_2_dict, events_list))


def process_one_list(list, type, date_without_year):
    if type == 'events':
        return process_events(list, date_without_year)
    elif type == 'births':
        return process_events(list, date_without_year, ' was born on this day.')
    elif type == 'deaths':
        return process_events(list, date_without_year, ' passed away on this day.')
    else:
        return []


def get_one_date(one_date_wiki_url, date_without_year):
    result = []
    session = HTMLSession()
    r = session.get(one_date_wiki_url)
    all_uls = r.html.find('ul')
    if '2 Events' in all_uls[0].text:
        # This is a workaround for January 1: https://en.wikipedia.org/wiki/January_1
        offset = 1
    elif '3 Events' in all_uls[0].text:
        # This is a workaround for February 29: https://en.wikipedia.org/wiki/February_29
        offset = 2
    else:
        assert '1 Events' in all_uls[0].text
        offset = 0
    result.extend(process_one_list(
        all_uls[1+offset].find('li'), 'events', date_without_year))
    result.extend(process_one_list(
        all_uls[2+offset].find('li'), 'births', date_without_year))
    result.extend(process_one_list(
        all_uls[3+offset].find('li'), 'deaths', date_without_year))
    return result


def process_one_date(one_date_wiki_url):
    # Adding 2020 is a workaround for strptime default to 1900, which is not a leap year
    eng_date = '2020_'+one_date_wiki_url.split('/').pop()
    obj_date = datetime.strptime(eng_date, '%Y_%B_%d')
    date_without_year = '{}-{}'.format(obj_date.month, obj_date.day)
    data = get_one_date(one_date_wiki_url, date_without_year)
    with open('wikipedia/archive/{}.json'.format(date_without_year), 'w') as outfile:
        json.dump(data, outfile, indent=2)
        print('{} Successfully finishes {} {}'.format(
            bcolors.OKGREEN, date_without_year, bcolors.ENDC))


def main():
    # Some data needs to be fixed by hand because of unstructured Wikipedia page
    # 1936-7-18: Fix the wrong hyphen place
    # Feb-6: Delete entries that has no year because of bad hyphen location
    # 1959-11-20: Fix the wrong hyphen place
    # Sep-11: Delete entries that has no year because of bad hyphen location
    all_links = get_date_links()
    for single_link in all_links:
        process_one_date(single_link)


if __name__ == '__main__':
    main()
