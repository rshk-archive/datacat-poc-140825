"""
Datacat - Database schema
"""

from collections import OrderedDict


class TableSchema(object):
    def __init__(self, name, fields=None):
        self.name = name
        if fields is None:
            fields = []
        self.fields = fields

    def get_create_sql(self):
        return 'CREATE TABLE "{name}" ({definition});'.format(
            name=self.name,
            definition=", ".join(
                self._build_field_def(x) for x in self.fields))

    def get_drop_sql(self):
        return 'DROP TABLE "{name}";'.format(name=self.name)

    def _build_field_def(self, field_def):
        name, definition = field_def
        return '"{0}" {1}'.format(name, definition)


ALL_TABLES = OrderedDict()


def make_table(name, *a, **kw):
    table = TableSchema(name, *a, **kw)
    ALL_TABLES[name] = table
    return table


make_table('info', [
    ('key', 'CHARACTER VARYING (256) PRIMARY KEY')
    ('value', 'TEXT')
])

make_table('dataset', [
    'id', 'SERIAL PRIMARY KEY',
    'configuration', 'JSON',
    'ctime', 'TIMESTAMP WITHOUT TIME ZONE',
    'mtime', 'TIMESTAMP WITHOUT TIME ZONE',
])

make_table('resource', [
    ('id', 'SERIAL PRIMARY KEY'),
    ('metadata', 'JSON'),
    ('auto_metadata', 'JSON'),
    ('mimetype', 'CHARACTER VARYING (128)'),
    ('data_oid', 'INTEGER'),
    ('ctime', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('mtime', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('hash', 'VARCHAR(128)'),
])

make_table('data_source', [
    ('id', 'CHARACTER VARCHAR (128) PRIMARY KEY'),
    ('ctime', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('mtime', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('url', 'CHARACTER VARYING (2048)'),
    ('connector', 'CHARACTER VARYING (256)'),
    ('configuration', 'JSON'),
])

make_table('background_job', [
    ('id', 'SERIAL PRIMARY KEY'),
    ('ctime', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('runner', 'CHARACTER VARYING (256)'),
    ('args', 'JSON'),
    ('kwargs', 'JSON'),
])

make_table('background_job_run', [
    ('id', 'SERIAL PRIMARY KEY'),
    ('job_id', 'INTEGER REFERENCES background_job (id)'),
    ('start_time', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('end_time', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('started', 'BOOLEAN DEFAULT false'),
    ('finished', 'BOOLEAN DEFAULT false'),
    ('success', 'BOOLEAN'),
    ('progress_current', 'INTEGER'),
    ('progress_total', 'INTEGER'),
])

make_table('background_job_run_log', [
    ('id', 'SERIAL PRIMARY KEY'),
    ('job_id', 'INTEGER REFERENCES background_job (id)'),
    ('job_run_id', 'INTEGER REFERENCES background_job_run (id)'),
    ('args', 'TEXT'),
    ('created', 'TIMESTAMP WITHOUT TIME ZONE'),
    ('filename', 'TEXT'),
    ('funcName', 'TEXT'),
    ('levelname', 'TEXT'),
    ('levelno', 'INTEGER'),
    ('lineno', 'INTEGER'),
    ('module', 'TEXT'),
    ('msecs', 'INTEGER'),
    ('message', 'TEXT'),
    ('msg', 'TEXT'),
    ('name', 'TEXT'),
    ('pathname', 'TEXT'),
    ('process', 'INTEGER'),
    ('processName', 'TEXT'),
    ('relativeCreated', 'INTEGER'),
    ('thread', 'INTEGER'),
    ('threadName', 'TEXT'),
    ('exc_class', 'TEXT'),
    ('exc_message', 'TEXT'),
    ('exc_repr', 'TEXT'),
    ('exc_traceback', 'TEXT'),
])
