import os
import json
import logging
import boto3
import sqlalchemy as sa
import requests
from datetime import datetime, timedelta

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(message)s", level='INFO')

META_DATA = {
    'New-York-Times': {
        'LOCAL_JSON_PATH': 'nyt/archive_test/'
    },
    # 'Movies': {
    #     'LOCAL_JSON_PATH': 'Movies/archive/'
    # }
    # 'Billboard': {
    #     'LOCAL_JSON_PATH': 'billboard/archive_test/'
    # },
    # 'Wikipedia': {
    #     'LOCAL_JSON_PATH': 'wikipedia/archive_test/'
    # }
}

YOUTUBE_API = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_PREFIX = 'https://www.youtube.com/watch?v='
BUCKET_NAME = 'lifeline-cc4'
MEMO = {}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


s3 = boto3.client('s3')


def get_db_conn():
    engine = sa.create_engine(os.environ['DATABASE_URL'], echo=False)
    return engine.connect()


def get_label_id_from_name(conn, name):
    label_table = sa.table('label', sa.column(
        'id', sa.Integer), sa.column('name', sa.Text))
    s = sa.sql.select([label_table.c.id, label_table.c.name]
                      ).where(label_table.c.name == name)
    result = conn.execute(s)
    if result.rowcount < 1:
        ins = label_table.insert().values(name=name)
        conn.execute(ins)
    result = conn.execute(s)
    return result.fetchone()['id']


def get_existing_events(conn, event_table, label_id, target_timestamp, target_title):
    s = sa.sql.select([event_table.c.title, event_table.c.timestamp, event_table.c.link, event_table.c.text, event_table.c.image_link, event_table.c.media_link]).where(
        sa.and_(
            event_table.c.label_id == label_id,
            event_table.c.timestamp == target_timestamp,
            event_table.c.title == target_title
        )
    )
    result = conn.execute(s)
    return result


def get_matching_s3_objects(bucket, prefix='', suffix=''):
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix
    while True:
        resp = s3.list_objects_v2(**kwargs)
        try:
            contents = resp['Contents']
        except KeyError:
            return
        for obj in contents:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield obj
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def get_logging_string(string, level):
    return '{} {} {}'.format(level, string, bcolors.ENDC)


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj['Key']


def get_json_content(bucket_name, file_key):
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    json_obj = json.load(obj['Body'])
    return json_obj


def get_json_content_from_local_file(path_prefix, file_key):
    res = None
    with open(path_prefix + file_key) as infile:
        res = json.load(infile)
    return res


def get_media_link_for_billboard(title, artist):
    query = get_query_for_billboard(title, artist)
    if query in MEMO:
        return MEMO[query]
    payload = {
        'q': query,
        'maxResult': 5,
        'key': os.environ['YOUTUBE_API_KEY'],
        'part': 'snippet'
    }
    items = requests.get(YOUTUBE_API, params=payload).json()['items']
    videos = list(filter(lambda x: x['id']['kind'] == 'youtube#video', items))
    if len(videos) > 0:
        winner = videos[0]
        image_link = winner['snippet']['thumbnails']['default']['url']
        media_link = YOUTUBE_PREFIX + winner['id']['videoId']
    else:
        image_link = ''
        media_link = ''
    MEMO[query] = (image_link, media_link)
    return image_link, media_link


def map_json_array_to_rows(label_name, json_array, json_key, label_id):
    """
    OR Mapper
    """
    result = []
    if label_name == 'New-York-Times':
        for jsevt in json_array:
            try:
                result.append({
                    'timestamp': jsevt['pub_date'],
                    'title': jsevt['headline'].get('print_headline', jsevt['headline']['main']),
                    'text': jsevt['snippet'],
                    'link': jsevt['web_url'],
                    'label_id': label_id,
                    'image_link': 'https://www.nytimes.com/' + next(filter(lambda e: e['subtype'] == 'thumbnail', jsevt['multimedia']))['url'],
                    'media_link': ''
                })
            except Exception as exception:
                logging.error('{:<25} {} {} {}'.format(
                    get_logging_string(label_name, bcolors.FAIL),
                    get_logging_string(json_key, bcolors.HEADER),
                    get_logging_string(type(exception).__name__, bcolors.FAIL),
                    jsevt['pub_date']))
        return result
    elif label_name == 'Billboard':
        for jsevt in json_array:
            event_date = jsevt["date"]
            event_title = jsevt["entries"][0]["title"]
            event_artist = jsevt["entries"][0]["artist"]
            event_weeks = jsevt["entries"][0]["weeks"]
            try:
                image_link, media_link = get_media_link_for_billboard(
                    event_title, event_artist)
                result.append({
                    'timestamp': event_date,
                    'title':  event_title + ' by ' + event_artist,
                    'text': "{} was on the Billboard charts for {} weeks.".format(event_title, str(event_weeks)),
                    'link': 'https://www.youtube.com/results?search_query=' + get_query_for_billboard(event_title, event_artist),
                    'label_id': label_id,
                    'image_link': image_link,
                    'media_link': media_link
                })
            except Exception as exception:
                logging.error('{:<25} {} {} {}'.format(
                    get_logging_string(label_name, bcolors.FAIL),
                    get_logging_string(json_key, bcolors.HEADER),
                    get_logging_string(type(exception).__name__, bcolors.FAIL),
                    event_date))
        return result
    elif label_name == 'Wikipedia':
        for jsevt in json_array:
            try:
                if any([i in jsevt['date'] for i in ['BC', 'AD']]):
                    continue
                datetime_object = datetime.strptime(jsevt['date'], '%Y-%m-%d')
            except:
                continue
            result.append({
                'timestamp': datetime_object,
                'title': jsevt['title'],
                'text': jsevt['text'],
                'link': jsevt['link'].pop() if len(jsevt['link']) == 1 else '',
                'label_id': label_id
            })
        return result


def get_query_for_billboard(title, artist):
    raw = title + '+' + artist
    return raw.replace(' ', '+')


def get_event_table():
    return sa.table('event',
                    sa.column('timestamp', sa.DateTime),
                    sa.column('title', sa.Text),
                    sa.column('text', sa.Text),
                    sa.column('link', sa.Text),
                    sa.column('label_id', sa.Integer),
                    sa.column('image_link', sa.Text),
                    sa.column('media_link', sa.Text)
                    )


def insert_events_from_json(conn, json_array, json_key, label_id, label_name):

    def already_same(existing_event, row):
        return existing_event['link'] == row['link'] and existing_event['image_link'] == row['image_link'] and existing_event['media_link'] == row['media_link'] and existing_event['text'] == row['text']
    event_table = get_event_table()
    already_same_count = 0
    update_count = 0
    rows = map_json_array_to_rows(label_name, json_array, json_key, label_id)
    inserts = []
    for row in rows:
        existing_event = get_existing_events(
            conn, event_table, label_id, row['timestamp'], row['title']).fetchone()
        if existing_event and len(existing_event) > 0:
            if not already_same(existing_event, row):
                update = event_table.update().values(text=row['text'], media_link=row['media_link'], link=row['link'], image_link=row['image_link']).where(sa.and_(
                    event_table.c.label_id == label_id,
                    event_table.c.timestamp == row['timestamp'],
                    event_table.c.title == row['title']
                ))
                update_count += 1
                conn.execute(update)
            else:
                already_same_count += 1
        else:
            inserts.append(row)
    if len(inserts) > 0:
        ins = event_table.insert().values(inserts)
        conn.execute(ins)
    logging.info('{:<25} {} Total from json:{:>15} Inserted: {:>15} Up-to-date: {:>15} Updated: {:>15}'.format(
        get_logging_string(label_name, bcolors.HEADER),
        get_logging_string(json_key, bcolors.HEADER),
        get_logging_string(len(rows), bcolors.OKBLUE),
        get_logging_string(len(inserts), bcolors.OKBLUE),
        get_logging_string(already_same_count, bcolors.OKBLUE),
        get_logging_string(update_count, bcolors.OKBLUE))
    )


def check_n_update(conn, json_key, label_name, label_id, path_prefix=''):
    # json_array = get_json_content(BUCKET_NAME, json_key) # Used when fetching from S3
    json_array = get_json_content_from_local_file(path_prefix, json_key)
    insert_events_from_json(conn, json_array, json_key, label_id, label_name)


def main():
    conn = get_db_conn()
    for label_name, meta_info in META_DATA.items():
        label_id = get_label_id_from_name(conn, label_name)
        # for json_key in list(get_matching_s3_keys(BUCKET_NAME, prefix=label_name, suffix='json')):
        for json_key in os.listdir(meta_info['LOCAL_JSON_PATH']):
            check_n_update(
                conn, json_key, label_name, label_id, path_prefix=meta_info['LOCAL_JSON_PATH'])


if __name__ == '__main__':
    main()
