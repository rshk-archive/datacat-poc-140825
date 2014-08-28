import pytest
import psycopg2

from datacat.db import create_tables, drop_tables


def test_table_create_drop(postgres_user_db):
    conn = postgres_user_db

    create_tables(conn)
    with pytest.raises(Exception):
        create_tables(conn)

    drop_tables(conn)
    with pytest.raises(Exception):
        drop_tables(conn)


def test_db_large_objects(postgres_user_db):
    conn = postgres_user_db

    lobject = conn.lobject(oid=0, mode='wb')
    lo_oid = lobject.oid
    lobject.write("This is some string")
    lobject.close()

    lobj1 = conn.lobject(oid=lo_oid, mode='rb')
    assert lobj1.read() == 'This is some string'

    lobj1.unlink()

    with pytest.raises(psycopg2.OperationalError):
        conn.lobject(oid=lo_oid, mode='rb')


def test_db_crud(postgres_user_db):
    conn = postgres_user_db

    create_tables(conn)

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM resource;")
        assert list(cur.fetchall()) == []

        cur.execute("""
        INSERT INTO resource (metadata, mimetype) VALUES
        ('{"name": "foo"}', 'application/json'),
        ('{"name": "bar"}', 'application/json'),
        ('{"name": "baz"}', 'application/json');
        """)

    with conn.cursor() as cur:
        cur.execute('SELECT * FROM resource')
        data = list(cur.fetchall())
        assert len(data) == 3

        # Make sure json deserialization works
        assert data[0]['metadata']['name'] == 'foo'
        assert data[1]['metadata']['name'] == 'bar'
        assert data[2]['metadata']['name'] == 'baz'

        # Make sure we can query the json field
        cur.execute("SELECT * FROM resource WHERE metadata->>'name' = 'foo'")
        data = list(cur.fetchall())
        assert len(data) == 1
        assert data[0]['metadata']['name'] == 'foo'
