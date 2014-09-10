"""
Datacat Geographical Plugin

- Imports resources (from an URL or internal resource) into a PostGIS table
- Exports geographical data into various formats
"""

# from flask import url_for
# from werkzeug.exceptions import NotFound

# from datacat.db import get_db
from datacat.db import db
from datacat.ext.base import Plugin
# from datacat.web.utils import json_view


class DummyPlugin(Plugin):
    def install(self):
        db.autocommit = True
        with db, db.cursor() as cur:
            cur.execute("""
            CREATE TABLE dummy_plugin (
                dataset_id INTEGER PRIMARY KEY,
                foo TEXT,
                bar TEXT);
            """)

    def uninstall(self):
        db.autocommit = True
        with db, db.cursor() as cur:
            cur.execute("""
            DROP TABLE dummy_plugin;
            """)


dummy_plugin = DummyPlugin(__name__ + ':dummy_plugin')


@dummy_plugin.hook(['dataset_create'])
def on_dataset_create(dataset_id, dataset_conf):
    db.autocommit = False
    with db, db.cursor() as cur:
        cur.execute("""
        INSERT INTO dummy_plugin
        (dataset_id, foo, bar)
        VALUES (%s, %s, %s);
        """, (dataset_id, 'FOO data', 'BAR data'))


@dummy_plugin.hook(['dataset_update'])
def on_dataset_update(dataset_id, dataset_conf):
    db.autocommit = False
    with db, db.cursor() as cur:
        cur.execute("""
        UPDATE dummy_plugin
        SET foo='Updated FOO data'
        WHERE dataset_id=%s;
        """, (dataset_id,))


@dummy_plugin.hook(['dataset_delete'])
def on_dataset_delete(dataset_id):
    db.autocommit = False
    with db, db.cursor() as cur:
        cur.execute("""
        DELETE FROM dummy_plugin
        WHERE dataset_id=%s;
        """, (dataset_id,))


@dummy_plugin.task(name=__name__ + ':dummy_plugin.dummy_task')
def dummy_task():
    pass
