import psycopg2
import psycopg2.extras


def connect(database, user=None, password=None, host='localhost', port=5432):
    conn = psycopg2.connect(database=database, user=user, password=password,
                            host=host, port=port)
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn


def create_tables(conn):
    """
    Create database schema for a given connection.
    """

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE info (
            key character varying(256),
            value text);

        CREATE TABLE dataset (
            id uuid,
            configuration json,
            state json);

        CREATE TABLE resource (
            id uuid,
            metadata json,
            auto_metadata json,
            state json);
        """)


def drop_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE info;
        DROP TABLE dataset;
        DROP TABLE resource;
        """)
