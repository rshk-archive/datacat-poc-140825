import pytest

from datacat.db import querybuilder


def test_querybuilder_insert():
    data = {'foo': 'FOO', 'bar': 'BAR'}
    query = querybuilder.insert('mytable', sorted(data.keys()))

    assert query == ('INSERT INTO "mytable" ("bar", "foo") '
                     'VALUES (%(bar)s, %(foo)s) RETURNING "id"')

    query = querybuilder.insert('mytable', sorted(data.keys()),
                                table_key='myid')
    assert query == ('INSERT INTO "mytable" ("bar", "foo") '
                     'VALUES (%(bar)s, %(foo)s) RETURNING "myid"')


def test_querybuilder_update():
    data = {'foo': 'FOO', 'bar': 'BAR'}
    query = querybuilder.update('mytable', sorted(data.keys()))
    assert query == ('UPDATE "mytable" SET "bar"=%(bar)s, "foo"=%(foo)s '
                     'WHERE "id"=%(id)s')

    data = {'foo': 'FOO', 'bar': 'BAR', 'id': 123}
    query = querybuilder.update('mytable', sorted(data.keys()))
    assert query == ('UPDATE "mytable" SET "bar"=%(bar)s, "foo"=%(foo)s '
                     'WHERE "id"=%(id)s')

    data = {'foo': 'FOO', 'bar': 'BAR', 'myid': 123}
    query = querybuilder.update('mytable', sorted(data.keys()),
                                table_key='myid')
    assert query == ('UPDATE "mytable" SET "bar"=%(bar)s, "foo"=%(foo)s '
                     'WHERE "myid"=%(myid)s')


def test_querybuilder_sanity_checks():
    with pytest.raises(ValueError):
        querybuilder.insert('invalid table name', {'foo': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.insert('mytable', {'invalid field name': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.insert('mytable', {'foo': 'bar'}, table_key='invalid key')

    with pytest.raises(ValueError):
        querybuilder.update('invalid table name', {'foo': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.update('mytable', {'invalid field name': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.update('mytable', {'foo': 'bar'}, table_key='invalid key')
