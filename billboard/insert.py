import os
import json
import sqlalchemy as sa


def get_db_conn():
    engine = sa.create_engine(
        os.environ['DATABASE_URL'], echo=True)
    return engine.connect()


label = sa.Table('label', sa.MetaData(),
                 sa.Column('id', sa.Integer),
                 sa.Column('name', sa.Text))

s = sa.sql.select([label.c.id]).where(label.c.name == 'Billboard Hot 100')
conn = get_db_conn()
result = conn.execute(s)
event_label_id = result.fetchone()['id']

# ins = label.insert().values(name='Billboard Hot 100')


# result2 = conn.execute(ins)

event = sa.Table('event', sa.MetaData(),
                 sa.Column('id', sa.Integer),
                 sa.Column('timestamp', sa.DateTime),
                 sa.Column('title', sa.Text),
                 sa.Column('label_id', sa.Integer))


with open('data_2018.json') as infile:

    data = json.load(infile)
    for eventsObj in data:
        event_date = eventsObj["date"]
        event_title = eventsObj["entries"][0]["title"]
        event_artist = eventsObj["entries"][0]["artist"]

        ins = event.insert().values(timestamp=event_date,
                                    title=event_title + ' by ' + event_artist,
                                    label_id=event_label_id)

        result = conn.execute(ins)

# def get_label_id_from_name(name):
#     label_table = sa.table('label', sa.column(
#         'id', sa.Integer), sa.column('name', sa.Text))
#     s = sa.sql.select([label_table.c.id, label_table.c.name]
#                       ).where(label_table.c.name == name)
#     conn = get_db_conn()
#     result = conn.execute(s)
#     return result.fetchone()['id']

#  event_table = sa.table('event',
#                            sa.column('timestamp', sa.DateTime),
#                            sa.column('title', sa.Text),
#                            sa.column('text', sa.Text),
#                            sa.column('link', sa.Text),
#                            sa.column('label_id', sa.Integer)
#                            )
#     label_id = get_label_id_from_name('New York Times')
#     data = []
#     for filename in os.listdir('nyt/archive'):
#         with open('nyt/archive/'+filename) as infile:
#             data.extend(json.load(infile))
#     mapped_data = list(map(lambda x: {'timestamp': x['pub_date'], 'title': x['headline']
#                                       ['print_headline'], 'text': x['snippet'], 'link': x['web_url'], 'label_id': label_id}, data))
#     op.bulk_insert(
#         event_table,
#         mapped_data
#     )
