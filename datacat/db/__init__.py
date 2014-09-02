from flask import g
import psycopg2
import psycopg2.extras


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

    conn.autocommit = True

    # See this: http://stackoverflow.com/questions/18404055
    # for creating indices on JSON field items

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE info (
            key CHARACTER VARYING (256),
            value TEXT);

        CREATE TABLE dataset (
            id SERIAL,
            configuration JSON);

        CREATE TABLE resource (
            id SERIAL,
            metadata JSON,
            auto_metadata JSON,
            mimetype CHARACTER VARYING (128),
            data_oid INTEGER);
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
