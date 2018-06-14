import os
import json
import sqlalchemy as sa
import codecs


def get_db_conn():
    engine = sa.create_engine(
        os.environ['DATABASE_URL'], echo=True)
    return engine.connect()


label = sa.Table('label', sa.MetaData(),
                 sa.Column('id', sa.Integer),
                 sa.Column('name', sa.Text))

conn = get_db_conn()


s = sa.sql.select([label.c.id]).where(label.c.name == 'Movies')

result = conn.execute(s)

try:
    event_label_id = result.fetchone()['id']
except:
    ins = label.insert().values(name='Movies')
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
        # filename = '2017-04-21.json'
        # with open('archive/' + filename) as in_file:
        data = json.load(in_file)

        event_date = filename[:10]
        event_title = data[0]["movie"]
        event_total_gross = data[0]["total_gross"]
        # print(event_date, event_title, event_total_gross)
        ins = event.insert().values(timestamp=event_date,
                                    title=event_title,
                                    text=event_title + " grossed a total of " +
                                    str(event_total_gross) + ".",
                                    link='https://www.imdb.com/find?q=' +
                                    event_title.replace(" ", "+"),
                                    label_id=event_label_id)

        result = conn.execute(ins)
