"""
Datacat Geographical Plugin

- Imports resources (from an URL or internal resource) into a PostGIS table
- Exports geographical data into various formats
"""

import os
import re

from werkzeug.exceptions import NotFound

from datacat.db import db, admin_db
from datacat.ext.base import Plugin
from datacat.utils.data_extraction import find_shapefiles, shp2pgsql
from datacat.utils.resource_access import open_resource
from datacat.utils.tempfile import TemporaryDir


class GeoPlugin(Plugin):
    def install(self):
        # Create database schema
        # with admin_db, admin_db.cursor() as cur:
        #     cur.execute("create extension postgis")
        pass

    def uninstall(self):
        pass


geo_plugin = GeoPlugin(__name__)


@geo_plugin.hook('make_dataset_metadata')
def make_dataset_metadata(dataset_id, config, metadata):
    if not config.get('geo', {}).get('enabled', False):
        # Not a geographical dataset
        return

    # todo: Add URLs to resources for the converted formats

    pass


@geo_plugin.hook(['dataset_create', 'dataset_update'])
def on_dataset_create_update(dataset_id, dataset_conf):
    """
    On dataset create/update, import geographical resources.

    This means:

    - download a copy of the remote resource
    - use some importer to extract geographical information from the resource
    - import the data in a postgis table named after the dataset

    .. todo:: We need a common library to download resources honoring caches
    """

    if dataset_conf.get('geo', {}).get('enabled', False):
        import_geo_dataset.delay(dataset_id)


@geo_plugin.hook(['dataset_delete'])
def on_dataset_delete(dataset_id):
    """
    On dataset delete, also delete geographical resources.

    - Delete postgis tables containing the geo data

    .. todo:: related things, like cached copies, should be deleted
              by some "core" plugin -> use some kind of reference
              mechanism to "cascade" deletes.
    """
    # todo: write this


@geo_plugin.task(name=__name__ + '.import_geo_dataset')
def import_geo_dataset(dataset_id):
    """
    Task to import geographical resources from a dataset
    into a PostGIS table.
    """

    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset"
                    " WHERE id=%s;", (dataset_id,))
        result = cur.fetchone()

    if result is None:
        # Should be logged as an error
        raise NotFound("Dataset not found: {0}".format(dataset_id))

    conf = result['configuration']

    if not conf.get('geo', {}).get('enabled', False):
        # Task was called from hook.. by error?
        raise ValueError("Requested import for non-geo-enabled dataset")

    if conf['geo']['importer'] == 'find_shapefiles':
        return import_dataset_find_shapefiles(dataset_id, conf)

    else:
        raise ValueError("Unsupported importer: {0}"
                         .format(conf['geo']['importer']))


@geo_plugin.route('/data/<int:dataset_id>/export/shp')
def export_geo_dataset_shp(dataset_id):
    """
    Export dataset to a Shapefile.
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/geojson')
def export_geo_dataset_geojson(dataset_id):
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/csv')
def export_geo_dataset_csv(dataset_id):
    """
    Export dataset to CSV, in a format that can be used for
    PostgreSQL COPY operations.
    """
    pass


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def _random_file_name(ext=None):
    name = os.urandom(20).encode('hex')
    if ext is not None:
        name += '.' + ext
    return name


def _copy_resource_to_file(resource, filename):
    res_object = open_resource(resource['url'])
    with open(filename, 'wb') as fp:
        res_object.save_to_file(fp)


def _get_internal_resource_data(resource_id):
    """Get all data form an internally-stored resource"""

    # todo: improve this function to avoid keeping the whole thing in memory
    # todo: also, make this more generic (and move from here)

    with db, db.cursor() as cur:
        cur.execute("""
        SELECT id, mimetype, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    with db:
        lobject = db.lobject(oid=resource['data_oid'], mode='rb')
        data = lobject.read()
        lobject.close()

    return data


def import_dataset_find_shapefiles_DUMMY(dataset_id, dataset_conf):
    with admin_db, admin_db.cursor() as cur:
        cur.execute("""
        CREATE TABLE geodata_{0} (
            key CHARACTER VARYING (256) PRIMARY KEY,
            value TEXT);
        """.format(dataset_id))


def import_dataset_find_shapefiles(dataset_id, dataset_conf):
    # ------------------------------------------------------------
    # - Find all the shapefiles inside the zip and extract them
    #   to a temporary path
    # ------------------------------------------------------------

    destination_table = 'geodata_{0}'.format(dataset_id)

    create_table_sqls = []
    import_data_sqls = []

    with TemporaryDir() as tempdir:
        # First, copy zip files to temporary directory

        for resource in dataset_conf['resources']:
            # We assume the file is a zip, but we should double-check that!
            dest_file = os.path.join(tempdir, _random_file_name('zip'))

            if isinstance(resource, basestring):
                resource = {'url': resource}

            # Copy the resource to disk
            _copy_resource_to_file(resource, dest_file)

            # Let's look for shapefiles inside that thing..
            found = find_shapefiles(dest_file)
            for basename, files in found.iteritems():
                if 'shp' not in files:
                    continue  # Bad match..

                # Export shapefiles to temporary files
                base_name = _random_file_name()
                for ext, item in files.iteritems():
                    dest = os.path.join(tempdir, base_name + '.' + ext)

                    with open(dest, 'wb') as fp:
                        # todo: copy file in chunks, not as a whole
                        fp.write(item.open().read())

                shp_full_path = os.path.join(tempdir, base_name + '.shp')

                create_table_sql = shp2pgsql(
                    shp_full_path,
                    table=destination_table,
                    create_table_only=True, mode='create',
                    geometry_column='geom', create_gist_index=True)

                # Use TEXT fields instead of varchar(XX)
                # todo: use a less-hackish way!!
                create_table_sql = re.sub(
                    r'varchar\([0-9]+\)', 'text', create_table_sql,
                    flags=re.IGNORECASE)

                import_data_sql = shp2pgsql(
                    shp_full_path,
                    table=destination_table,
                    mode='append',
                    geometry_column='geom',
                    create_gist_index=False)

                create_table_sqls.append(create_table_sql)
                import_data_sqls.append(import_data_sql)

    with admin_db, admin_db.cursor() as cur:
        cur.execute(create_table_sqls[0])

    with db, db.cursor() as cur:
        for sql in import_data_sqls:
            cur.execute(sql)
