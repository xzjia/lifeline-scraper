"""Add wikipedia data into database

Revision ID: 1d019196b47c
Revises: 812fd2e73486
Create Date: 2018-06-08 15:05:58.350263

"""
import os
import json
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '1d019196b47c'
down_revision = '812fd2e73486'
branch_labels = None
depends_on = None


def get_db_conn():
    engine = sa.create_engine(
        os.environ['DATABASE_URL'], echo=True)
    return engine.connect()


def get_label_id_from_name(name):
    label_table = sa.table('label', sa.column(
        'id', sa.Integer), sa.column('name', sa.Text))
    s = sa.sql.select([label_table.c.id, label_table.c.name]
                      ).where(label_table.c.name == name)
    conn = get_db_conn()
    result = conn.execute(s)
    return result.fetchone()['id']


def map_one_entry(event, label_id):
    try:
        if any([i in event['date'] for i in ['BC', 'AD']]):
            return None
        datetime_object = datetime.strptime(event['date'], '%Y-%m-%d')
    except:
        return None
    return {
        'timestamp': datetime_object,
        'title': event['title'],
        'text': event['text'],
        'link': event['link'].pop() if len(event['link']) == 1 else '',
        'label_id': label_id
    }


def upgrade():
    event_table = sa.table('event',
                           sa.column('timestamp', sa.DateTime),
                           sa.column('title', sa.Text),
                           sa.column('text', sa.Text),
                           sa.column('link', sa.Text),
                           sa.column('label_id', sa.Integer)
                           )
    label_id = get_label_id_from_name('Wikipedia')
    data = []
    for filename in os.listdir('wikipedia/archive'):
        with open('wikipedia/archive/' + filename) as infile:
            data.extend(json.load(infile))
    mapped_data = list(
        filter(lambda x: x, map(lambda x: map_one_entry(x, label_id), data)))
    print('All data mapped, length is {}'.format(len(mapped_data)))
    op.bulk_insert(
        event_table,
        mapped_data
    )


def downgrade():
    pass
