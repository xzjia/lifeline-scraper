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


class constants:
    SPLIT_HYPHEN = '-|–|－'
    EVENTS_INDEX = 1
    BIRTHS_INDEX = 2
    DEATHS_INDEX = 3
    WIKI_ENTRY = 'https://en.wikipedia.org/wiki/List_of_historical_anniversaries'


class Wikipedia(object):
    def __init__(self, store_json):
        self.all_links = self.get_date_links()
        self.data = {}
        for single_link in self.all_links:
            w = Wiki(single_link)
            self.data[w.date_without_year] = w.data
            if store_json:
                w.store_json('wikipedia/archive')

    def get_date_links(self):
        session = HTMLSession()
        r = session.get(constants.WIKI_ENTRY)
        nav = r.html.find('.navbox-list')
        return set.union(*map(lambda one_month: one_month.absolute_links, nav))


class Wiki(object):
    def __init__(self, one_date_wiki_url):
        # Adding 2020 is a workaround for strptime default to 1900, which is not a leap year
        eng_date = '2020_'+one_date_wiki_url.split('/').pop()
        obj_date = datetime.strptime(eng_date, '%Y_%B_%d')
        self.date_without_year = '{}-{}'.format(obj_date.month, obj_date.day)
        self.data = self.get_one_date(one_date_wiki_url)

    def store_json(self, prefix):
        with open('{}/{}.json'.format(prefix, self.date_without_year), 'w') as outfile:
            json.dump(self.data, outfile, indent=2)
            print('{} Successfully finishes {} {}'.format(
                bcolors.OKGREEN, self.date_without_year, bcolors.ENDC))

    def get_one_date(self, one_date_wiki_url):
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
        result.extend(self.process_one_list(
            all_uls[constants.EVENTS_INDEX+offset].find('li'), 'events', self.date_without_year))
        result.extend(self.process_one_list(
            all_uls[constants.BIRTHS_INDEX+offset].find('li'), 'births', self.date_without_year))
        result.extend(self.process_one_list(
            all_uls[constants.DEATHS_INDEX+offset].find('li'), 'deaths', self.date_without_year))
        return result

    def process_one_list(self, list, type, date_without_year):
        if type == 'events':
            return self.process_events(list, date_without_year)
        elif type == 'births':
            return self.process_events(list, date_without_year, ' was born on this day.')
        elif type == 'deaths':
            return self.process_events(list, date_without_year, ' passed away on this day.')
        else:
            return []

    def process_events(self, events_list, date_without_year, postfix=''):
        def get_correct_raw_html(html_string):
            with_links = html_string.replace(
                '/wiki/', 'https://en.wikipedia.org/wiki/')
            splitted = re.split(constants.SPLIT_HYPHEN, with_links, maxsplit=1)
            assert len(splitted) == 2
            return splitted[1]

        def get_correct_links(links, year):
            res = sorted([x for x in links if year not in x])
            return res

        def event_2_dict(event):
            if event.find('ul'):
                print('{}Error: Nested list of {} {} **{}** '.format(bcolors.FAIL, date_without_year,
                                                                     bcolors.ENDC, event.text))
                return None
            splitted = re.split(constants.SPLIT_HYPHEN, event.text, maxsplit=1)
            if len(splitted) < 2:
                print('{}Error: No hyphen of {} {} **{}** '.format(bcolors.FAIL, date_without_year,
                                                                   bcolors.ENDC, event.text))
                return None
            result = {}
            year = splitted[0].strip()
            desc = splitted[1].strip()
            result['date'] = year + '-' + date_without_year
            result['title'] = desc + postfix
            result['text'] = get_correct_raw_html(event.html)
            result['link'] = get_correct_links(event.absolute_links, year)
            return result
        return filter(lambda e: e, map(event_2_dict, events_list))
