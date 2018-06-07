from requests_html import HTMLSession


def get_date_links():
    session = HTMLSession()
    r = session.get(
        'https://en.wikipedia.org/wiki/List_of_historical_anniversaries')
    nav = r.html.find('.navbox-list')
    return set.union(*map(lambda one_month: one_month.absolute_links, nav))


def get_one_date(one_date_wiki_url):
    session = HTMLSession()
    r = session.get(one_date_wiki_url)
    all_uls = r.html.find('ul')
    events = all_uls[1]
    births = all_uls[2]
    deaths = all_uls[3]
    return len(events.find('li')), len(births.find('li')), len(deaths.find('li'))


def main():
    # all_links = get_date_links()
    test_date = 'https://en.wikipedia.org/wiki/April_11'
    print(get_one_date(test_date))


if __name__ == '__main__':
    main()
