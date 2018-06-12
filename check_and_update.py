import os
import json
import boto3
import sqlalchemy as sa
from datetime import datetime, timedelta

# META_DATA is the dictionary that stores all the META data about how JSON files should be migrated into database
META_DATA = {
    'New-York-Times': {
        # TODO The body now is not used at all.
        'TIMESTAMP_KEY': ['pub_date'],
        'TITLE_KEY': ['headline||print_headline', 'headline||main'],
        'TEXT_KEY': ['snippet'],
        'LINK_KEY': ['web_url']
        # TODO The body now is not used at all.
    },
    # 'Wikipedia': {
    #     'TIMESTAMP_KEY': ['date']
    # },
    # 'Non-existing': {

    # }
}

BUCKET_NAME = 'lifeline-cc4'

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


def get_existing_events(conn, label_id, target_date):
    event_table = sa.table('event',
                           sa.column('title', sa.Text),
                           sa.column('timestamp', sa.DateTime),
                           sa.column('label_id', sa.Integer)
                           )
    s = sa.sql.select([event_table.c.title, event_table.c.timestamp]).where(
        sa.and_(
            event_table.c.label_id == label_id,
            event_table.c.timestamp >= target_date,
            event_table.c.timestamp < target_date + timedelta(days=1)
        )
    )
    result = conn.execute(s)
    return result


def get_rows_from_event(label_id, conn):
    event_table = sa.table('event', sa.column(
        'title', sa.Text), sa.column('label_id', sa.Integer))
    s = sa.sql.select([event_table.c.title]).where(
        event_table.c.label_id == label_id)
    result = conn.execute(s)


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


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj['Key']


def get_json_content(bucket, file_key):
    # obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
    # json_obj = json.load(obj['Body'])
    res = None
    with open('nyt/archive/' + file_key) as infile:
        res = json.load(infile)
    return res


def get_value_from_map(candidate_fields, event_obj):
    # TODO Fix this function so it works general
    for candidate in candidate_fields:
        if candidate in event_obj:
            return event_obj[candidate]
        layers = candidate.split('||')


def map_json_to_data(meta_info, json_array, label_id):
    # TODO Fix this function so it works general
    def dict2row(event):
        result = {}
        result['timestamp'] = get_value_from_map(
            meta_info['TIMESTAMP_KEY'], event)
        result['title'] = get_value_from_map(meta_info['TITLE_KEY'], event)
        result['text'] = get_value_from_map(meta_info['TEXT_KEY'], event)
        result['link'] = get_value_from_map(meta_info['LINK_KEY'], event)
        result['label_id'] = label_id
        return result
    return map(dict2row, json_array)


def map_json_to_row(data_source, json_array, label_id):
    if data_source == 'New-York-Times':
        try:
            return list(map(lambda jsevt: {
                'timestamp': jsevt['pub_date'],
                'title': jsevt['headline']['print_headline'],
                'text': jsevt['snippet'],
                'link': jsevt['web_url'],
                'label_id': label_id
            }, json_array))
        except KeyError:
            return list(map(lambda jsevt: {
                'timestamp': jsevt['pub_date'],
                'title': jsevt['headline']['main'],
                'text': jsevt['snippet'],
                'link': jsevt['web_url'],
                'label_id': label_id
            }, json_array))
        except:
            print('KeyError and skipping this json_array {}'.format(json_array))
    else:
        return []


def insert_events_from_json(conn, meta_info, json_array, label_id, data_source):
    print('Inserting {} events into the database'.format(len(json_array)))
    event_table = sa.table('event',
                           sa.column('timestamp', sa.DateTime),
                           sa.column('title', sa.Text),
                           sa.column('text', sa.Text()),
                           sa.column('link', sa.Text()),
                           sa.column('label_id', sa.Integer))
    rows = map_json_to_row(data_source, json_array, label_id)
    ins = event_table.insert().values(rows)
    conn.execute(ins)


def main():
    conn = get_db_conn()
    for key, value in META_DATA.items():
        label_id = get_label_id_from_name(conn, key)
        # for json_key in list(get_matching_s3_keys(BUCKET_NAME, prefix=key, suffix='json')):
        for json_key in os.listdir('nyt/archive'):
            # target_date = datetime.strptime(json_key, '{}/%Y-%m-%d.json'.format(key))
            target_date = datetime.strptime(json_key, '%Y-%m-%d.json')
            events = get_existing_events(
                conn, label_id, target_date).fetchall()
            if len(events) == 0:
                insert_events_from_json(
                    conn, value, get_json_content(BUCKET_NAME, json_key), label_id, key)
            else:
                print(
                    'Found {} events on  **{}**, so skipping'.format(len(events), json_key))


if __name__ == '__main__':
    main()
