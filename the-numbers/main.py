#!/usr/bin/env python3
import argparse
import datetime
import json
from requests_html import HTMLSession


def parse_args():
    parser = argparse.ArgumentParser(
        description='Retrieve movie box office sales figures for fridays within the given range.')
    parser.add_argument(
        'start_date', help='the start date for the data scraping (inclusive).')
    parser.add_argument(
        'end_date', help='the end date for the data scraping (exclusive).')
    return parser.parse_args()


def get_chart(raw_html):
    table = raw_html.html.find("#page_filling_chart table", first=True)

    # Ignore the first row because it is the table's headings
    rows = table.find("tr")[1:]
    keys = ["current_week_rank", "previous_week_rank", "movie", "distributor",
            "gross", "change", "num_theaters", "per_theater", "total_gross", "days"]
    results = []
    for row in rows:
        this_row = dict()
        cells = row.find("td")
        for i in range(len(cells)):
            this_row[keys[i]] = cells[i].text
        results.append(this_row)
    return results


def get_weekend_chart(year, month, date):
    session = HTMLSession()
    raw_html = session.get(
        "https://www.the-numbers.com/box-office-chart/weekend/{}/{}/{}".format(year, month, date))
    return get_chart(raw_html)


def get_weekly_chart(year, month, date):
    session = HTMLSession()
    raw_html = session.get(
        "https://www.the-numbers.com/box-office-chart/weekly/{}/{}/{}".format(year, month, date))
    return get_chart(raw_html)


def get_movies_for_day(date):
    chart = get_weekly_chart(date.year, date.month, date.day)
    if len(chart) < 1:
        chart = get_weekend_chart(date.year, date.month, date.day)
    if len(chart) < 1:
        return None
    return chart


def main():
    args = parse_args()
    start_date_split = args.start_date.split("-")
    end_date_split = args.end_date.split("-")
    start_date = datetime.date(int(start_date_split[0]),
                               int(start_date_split[1]), int(start_date_split[2]))
    end_date = datetime.date(int(end_date_split[0]),
                             int(end_date_split[1]), int(end_date_split[2]))
    # Normalize start_date to be closest preceding Friday
    days_after_friday = (start_date.weekday()-4 + 7) % 7
    date = start_date + datetime.timedelta(days=-days_after_friday)
    while date < end_date:
        movies = get_movies_for_day(date)
        if movies is not None:
            with open('{}/{}.json'.format("the-numbers/archive", date.isoformat()), 'w') as outfile:
                json.dump(movies, outfile, indent=2)
                print('Successfully finished {}'.format(date))
        else:
            print("{} -> no data".format(date))
        date = date + datetime.timedelta(days=7)


if __name__ == '__main__':
    main()
