from io import BytesIO
import re


VALID_IDENTIFIER_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def insert(table, data, table_key='id'):
    """
    Build a SQL query for inserting some data in a table.

    :param table:
        Name of the table in which to insert data

    :param data:
        Iterable providing names of the fields to be inserted.
        Can be the data dictionary itself, or any kind of (sub)set
        of its keys.

    :param table_key:
        The name of the key field for the table, to be returned by
        the query using a ``RETURNING`` clause.

    :return:
        The query, as a string
    """

    sql = BytesIO()
    sql.write('INSERT INTO "{0}" '.format(table))

    if not VALID_IDENTIFIER_RE.match(table):
        raise ValueError("Invalid table name: {0}".format(table))

    if not VALID_IDENTIFIER_RE.match(table_key):
        raise ValueError("Invalid field name: {0}".format(table_key))

    fields_spec = []
    values_spec = []

    for field in data:
        if not VALID_IDENTIFIER_RE.match(field):
            raise ValueError("Invalid field name: {0}".format(field))

        fields_spec.append('"{0}"'.format(field))
        values_spec.append('%({0})s'.format(field))

    sql.write('(')
    sql.write(', '.join(fields_spec))
    sql.write(') VALUES (')
    sql.write(', '.join(values_spec))
    sql.write(') RETURNING "{0}"'.format(table_key))

    return sql.getvalue()


def update(table, data, table_key='id'):
    """
    Build a SQL query for updating table records.

    :param table:
        Name of the table to operate on.

    :param data:
        Iterable providing names of the fields to be updated.
        Can be the data dictionary itself, or any kind of (sub)set
        of its keys.

    :param table_key:
        The name of the key field for the table, used to build
        the ``WHERE`` clause.

    :return:
        The query, as a string
    """

    sql = BytesIO()
    sql.write('UPDATE "{0}" SET '.format(table))

    if not VALID_IDENTIFIER_RE.match(table):
        raise ValueError("Invalid table name: {0}".format(table))

    if not VALID_IDENTIFIER_RE.match(table_key):
        raise ValueError("Invalid field name: {0}".format(table_key))

    updates_spec = []

    for field in data:
        if field == table_key:
            # Don't attempt updating the table key!
            continue

        if not VALID_IDENTIFIER_RE.match(field):
            raise ValueError("Invalid field name: {0}".format(field))

        updates_spec.append('"{0}"=%({0})s'.format(field))

    sql.write(", ".join(updates_spec))
    sql.write(' WHERE "{0}"=%({0})s'.format(table_key))
    return sql.getvalue()
