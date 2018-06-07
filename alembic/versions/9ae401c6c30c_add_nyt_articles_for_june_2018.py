"""Add NYT articles for June and May 2018

Revision ID: 9ae401c6c30c
Revises: c3ba36e57a09
Create Date: 2018-06-06 14:12:30.780972

"""
import os
import json
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ae401c6c30c'
down_revision = 'c3ba36e57a09'
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


def upgrade():
    event_table = sa.table('event',
                           sa.column('timestamp', sa.DateTime),
                           sa.column('title', sa.Text),
                           sa.column('text', sa.Text),
                           sa.column('link', sa.Text),
                           sa.column('label_id', sa.Integer)
                           )
    label_id = get_label_id_from_name('New York Times')
    data = []
    for filename in os.listdir('nyt/archive'):
        with open('nyt/archive/'+filename) as infile:
            data.extend(json.load(infile))
    mapped_data = list(map(lambda x: {'timestamp': x['pub_date'], 'title': x['headline']
                                      ['print_headline'], 'text': x['snippet'], 'link': x['web_url'], 'label_id': label_id}, data))
    op.bulk_insert(
        event_table,
        mapped_data
    )


def downgrade():
    pass
