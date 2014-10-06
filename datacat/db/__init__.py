from collections import MutableMapping
import json
import functools

from flask import g
import psycopg2
import psycopg2.extras
from werkzeug.local import LocalProxy

from .schema import ALL_TABLES


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
    if not conn.autocommit:
        raise ValueError("Was expecting a connection with autocommit on")

    # ------------------------------------------------------------
    # See this: http://stackoverflow.com/questions/18404055
    # for creating indices on JSON field items.
    #
    # We will need to allow defining such indices in the configuration
    # but maybe a plugin should be used to handle that..
    # ------------------------------------------------------------

    with conn.cursor() as cur:
        for table in ALL_TABLES:
            cur.execute(table.get_create_sql())


def drop_tables(conn):
    if not conn.autocommit:
        raise ValueError("Was expecting a connection with autocommit on")

    with conn.cursor() as cur:
        for table in reversed(ALL_TABLES):
            cur.execute(table.get_drop_sql())


def _cached(key_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapped():
            if not hasattr(g, key_name):
                setattr(g, key_name, func())
            return getattr(g, key_name)
        return wrapped
    return decorator


@_cached('_database')
def get_db():
    from flask import current_app
    c = connect(**current_app.config['DATABASE'])
    c.autocommit = False
    return c


@_cached('_admin_database')
def get_admin_db():
    from flask import current_app
    c = connect(**current_app.config['DATABASE'])
    c.autocommit = True
    return c


class DbInfoDict(MutableMapping):
    def __init__(self, db):
        self._db = db

    def __getitem__(self, key):
        with self._db.cursor() as cur:
            cur.execute("""
            SELECT * FROM info WHERE "key" = %s;
            """, (key,))
            row = cur.fetchone()
            if row is None:
                raise KeyError(key)
        return json.loads(row['value'])

    def __setitem__(self, key, value):
        # Note that the update would be void if anybody deleted
        # the key between the two queries! -- but we can be optimistic
        # as key deletes are quite infrequent..
        value = json.dumps(value)
        try:
            with self._db, self._db.cursor() as cur:
                cur.execute("""
                INSERT INTO info (key, value) VALUES (%s, %s)
                """, (key, value))
        except psycopg2.IntegrityError:
            with self._db, self._db.cursor() as cur:
                cur.execute("""
                UPDATE info SET value=%s WHERE key=%s
                """, (value, key))

    def __delitem__(self, key):
        with self._db, self._db.cursor() as cur:
            cur.execute("""
            DELETE FROM info WHERE key=%s
            """, (key,))

    def __iter__(self):
        with self._db.cursor() as cur:
            cur.execute("SELECT key FROM info;")
            for row in cur:
                yield row['key']

    def iteritems(self):
        with self._db.cursor() as cur:
            cur.execute("SELECT key, value FROM info;")
            for row in cur:
                yield row['key'], json.loads(row['value'])

    def __len__(self):
        with self._db.cursor() as cur:
            cur.execute("SELECT count(*) AS count FROM info;")
            row = cur.fetchone()
            return row['count']


db = LocalProxy(get_db)
admin_db = LocalProxy(get_admin_db)
db_info = LocalProxy(lambda: DbInfoDict(get_db()))
