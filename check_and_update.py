import os
import json
import sqlalchemy as sa

META_DATA = {
    'New York Times': {
        'JSON_PATH': 'nyt/onetimedata'
    },
    'Wikipedia': {
        'JSON_PATH': 'wikipedia/archive'
    }
}


def get_db_conn():
    engine = sa.create_engine(os.environ['DATABASE_URL'], echo=True)
    return engine.connect()


def get_label_id_from_name(name, conn):
    label_table = sa.table('label', sa.column(
        'id', sa.Integer), sa.column('name', sa.Text))
    s = sa.sql.select([label_table.c.id, label_table.c.name]
                      ).where(label_table.c.name == name)
    result = conn.execute(s)
    return result.fetchone()['id']


def get_rows_from_event(label_id, conn):
    event_table = sa.table('event', sa.column(
        'title', sa.Text), sa.column('label_id', sa.Integer))
    s = sa.sql.select([event_table.c.title]).where(
        event_table.c.label_id == label_id)
    result = conn.execute(s)


def main():
    conn = get_db_conn()
    for key, value in META_DATA.items():
        label_id = get_label_id_from_name(key, conn)


if __name__ == '__main__':
    main()
