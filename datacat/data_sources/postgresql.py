from urlparse import urlparse

import psycopg2
import psycopg2.extras

from .base import DataSourceBase


class PostgreSQLDataSource(DataSourceBase):
    def connect(self):
        parsed_url = urlparse(self.url)
        conn = psycopg2.connect(
            database=parsed_url.path.strip('/').split('/')[0],
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port)
        conn.cursor_factory = psycopg2.extras.DictCursor
        conn.autocommit = False
        return conn

    @property
    def connection(self):
        if getattr(self, '_connection', None) is None:
            self._connection = self.connect()
        return self._connection
