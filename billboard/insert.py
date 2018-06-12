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

conn = get_db_conn()
# ins = label.insert().values(name='Billboard')
# conn.execute(ins)


s = sa.sql.select([label.c.id]).where(label.c.name == 'Billboard')

result = conn.execute(s)

try:
    event_label_id = result.fetchone()['id']
except:
    ins = label.insert().values(name='Billboard')
    conn.execute(ins)
    result = conn.execute(s)
    event_label_id = result.fetchone()['id']

metadata = sa.MetaData()

event = sa.Table('event', metadata,
                 sa.Column('id', sa.Integer),
                 sa.Column('timestamp', sa.DateTime),
                 sa.Column('title', sa.Text),
                 sa.Column('text', sa.Text),
                 sa.Column('link', sa.Text),
                 sa.Column('label_id', sa.Integer))

for filename in os.listdir('archive'):
    with open('archive/' + filename) as in_file:

        data = json.load(in_file)
        for eventsObj in data:
            event_date = eventsObj["date"]
            event_title = eventsObj["entries"][0]["title"]
            event_artist = eventsObj["entries"][0]["artist"]
            event_weeks = eventsObj["entries"][0]["weeks"]

            ins = event.insert().values(timestamp=event_date,
                                        title=event_title + ' by ' + event_artist,
                                        text=event_title + " was on the Billboard charts for " +
                                        str(event_weeks) + " weeks.",
                                        link='https://www.youtube.com/results?search_query=' +
                                        event_title.replace(
                                            " ", "+") + '+' + event_artist.replace(" ", "+"),
                                        label_id=event_label_id)

            result = conn.execute(ins)
