#!/usr/bin/env python3
import argparse
import datetime
import json
from requests_html import HTMLSession


def parse_args():
    """Parse and return the command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Retrieve movie box office sales figures for fridays within the given range.')
    parser.add_argument(
        'start_date', help='the start date for the data scraping (inclusive).')
    parser.add_argument(
        'end_date', help='the end date for the data scraping (exclusive).')
    return parser.parse_args()


def get_chart(raw_html):
    """Return all the charting movies that appear in the given raw_html.

    Args:
        raw_html: A raw_html object that is returned by requests_html.find()

    Returns:
        An array of objects. Each object represents a single movie that is on the chart.
    """
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
    """Return an array of movies that were on the charts for the weekend of the given date.

    Args:
        year: target year
        month: target month
        date: target date

    Returns:
        An array of objects. Each object represents a single movie that is on the chart.
    """
    session = HTMLSession()
    raw_html = session.get(
        "https://www.the-numbers.com/box-office-chart/weekend/{}/{}/{}".format(year, month, date))
    return get_chart(raw_html)


def get_weekly_chart(year, month, date):
    """Return an array of movies that were on the charts for the week of the given date.

    Args:
        year: target year
        month: target month
        date: target date

    Returns:
        An array of objects. Each object represents a single movie that is on the chart.
    """
    session = HTMLSession()
    raw_html = session.get(
        "https://www.the-numbers.com/box-office-chart/weekly/{}/{}/{}".format(year, month, date))
    return get_chart(raw_html)


def get_movies_for_day(date):
    """Return an array of movies that were on the charts for the given date.
    If there is data for the weekly chart, use it.
    Else if there is data for the weekend chart, use it.
    Else, return None.

    Args:
        date: target date

    Returns:
        An array of objects. Each object represents a single movie that is on the chart.
    """
    chart = get_weekly_chart(date.year, date.month, date.day)
    if len(chart) < 1:
        chart = get_weekend_chart(date.year, date.month, date.day)
    if len(chart) < 1:
        return None
    return chart


def write_json_for_movies(date):
    """Write a file that contains all the movies that were on the charts for the given day.
    The resulting file will be created in the "the-numbers/archive" folder.
    The filename will be "YYYY-MM-DD.json"

    Args:
        date: target date
    """
    movies = get_movies_for_day(date)
    if movies is not None:
        with open('{}/{}.json'.format("the-numbers/archive", date.isoformat()), 'w') as outfile:
            json.dump(movies, outfile, indent=2)
            print('Successfully finished {}'.format(date))
    else:
        print("{} -> no data".format(date))


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
        write_json_for_movies(date)
        date = date + datetime.timedelta(days=7)


if __name__ == '__main__':
    main()
