from flask import g
import psycopg2
import psycopg2.extras
from werkzeug.local import LocalProxy


def connect(database, user=None, password=None, host='localhost', port=5432):
    conn = psycopg2.connect(database=database, user=user, password=password,
                            host=host, port=port)
    conn.cursor_factory = psycopg2.extras.DictCursor
    conn.autocommit = False
    return conn


def create_tables(conn):
    """
    Create database schema for a given connection.
    """

    # We need to be in autocommit mode (i.e. out of transactions)
    # in order to create tables / do administrative stuff..
    conn.autocommit = True

    # ------------------------------------------------------------
    # See this: http://stackoverflow.com/questions/18404055
    # for creating indices on JSON field items.
    #
    # We will need to allow defining such indices in the configuration
    # but maybe a plugin should be used to handle that..
    # ------------------------------------------------------------

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE info (
            key CHARACTER VARYING (256),
            value TEXT);

        CREATE TABLE dataset (
            id SERIAL,
            configuration JSON,
            ctime TIMESTAMP WITHOUT TIME ZONE,
            mtime TIMESTAMP WITHOUT TIME ZONE);

        CREATE TABLE resource (
            id SERIAL,
            metadata JSON,
            auto_metadata JSON,
            mimetype CHARACTER VARYING (128),
            data_oid INTEGER,
            ctime TIMESTAMP WITHOUT TIME ZONE,
            mtime TIMESTAMP WITHOUT TIME ZONE);
        """)


def drop_tables(conn):
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE info;
        DROP TABLE dataset;
        DROP TABLE resource;
        """)


def get_db():
    from flask import current_app
    if not hasattr(g, 'database'):
        g.database = connect(**current_app.config['DATABASE'])
    return g.database


db = LocalProxy(get_db)
