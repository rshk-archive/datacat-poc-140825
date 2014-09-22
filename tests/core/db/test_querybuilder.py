import pytest

from datacat.db import querybuilder


def test_querybuilder_select_pk():
    query = querybuilder.select_pk('mytable')
    assert query == 'SELECT * FROM "mytable" WHERE "id"=%(id)s'

    query = querybuilder.select_pk('mytable', table_key='my_id')
    assert query == 'SELECT * FROM "mytable" WHERE "my_id"=%(my_id)s'

    query = querybuilder.select_pk('mytable', fields='one, two')
    assert query == 'SELECT one, two FROM "mytable" WHERE "id"=%(id)s'

    query = querybuilder.select_pk('mytable', fields=['one', 'two'])
    assert query == 'SELECT one, two FROM "mytable" WHERE "id"=%(id)s'

    with pytest.raises(ValueError):
        querybuilder.select_pk('Invalid table name')

    with pytest.raises(ValueError):
        querybuilder.select_pk('mytable', table_key='Invalid field name')


def test_querybuilder_select_paged():
    query = querybuilder.select_paged('mytable')
    assert query == 'SELECT * FROM "mytable" ORDER BY id ASC OFFSET 0 LIMIT 10'

    query = querybuilder.select_paged('mytable', fields='one, two')
    assert query == ('SELECT one, two FROM "mytable" ORDER BY id ASC '
                     'OFFSET 0 LIMIT 10')

    query = querybuilder.select_paged('mytable', fields='one, two',
                                      order_by='my_id ASC', offset=40,
                                      limit=20)
    assert query == ('SELECT one, two FROM "mytable" ORDER BY my_id ASC '
                     'OFFSET 40 LIMIT 20')


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

    # -------------------- Update --------------------

    with pytest.raises(ValueError):
        querybuilder.update('invalid table name', {'foo': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.update('mytable', {'invalid field name': 'bar'})

    with pytest.raises(ValueError):
        querybuilder.update('mytable', {'foo': 'bar'}, table_key='invalid key')


def test_querybuilder_delete():
    query = querybuilder.delete('mytable')
    assert query == 'DELETE FROM "mytable" WHERE "id"=%(id)s'

    query = querybuilder.delete('mytable', table_key='my_id')
    assert query == 'DELETE FROM "mytable" WHERE "my_id"=%(my_id)s'

    with pytest.raises(ValueError):
        querybuilder.delete('Invalid table name')

    with pytest.raises(ValueError):
        querybuilder.delete('mytable', table_key='invalid field')
