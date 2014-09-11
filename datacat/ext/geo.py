"""
Datacat Geographical Plugin

- Imports resources (from an URL or internal resource) into a PostGIS table
- Exports geographical data into various formats
"""

from flask import url_for
from werkzeug.exceptions import NotFound

from datacat.db import get_db
from datacat.ext.base import Plugin
from datacat.web.utils import json_view


class GeoPlugin(Plugin):
    def install(self):
        # Create database schema
        pass

    def uninstall(self):
        pass


geo_plugin = GeoPlugin(__name__)


@geo_plugin.hook('make_dataset_metadata')
def make_dataset_metadata(dataset_id, config, metadata):
    if not config.get('geo', {}).get('enabled', False):
        # Not a geographical dataset
        return

    # For each resource, if it is a geographical resource, add URLs to
    # other formats, etc.

    pass

#     if 'metadata' in config:
#         metadata.update(config['metadata'])

#     if 'resources' in config:
#         metadata['resources'] = []
#         for resource_id, resource in enumerate(config['resources']):
#             metadata['resources'].append({
#                 'url': url_for(__name__ + '.get_dataset_resource',
#                                dataset_id=dataset_id,
#                                resource_id=resource_id,
#                                _external=True)
#             })


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

    import_geo_resources.delay(dataset_id)


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
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/shp')
def export_geo_dataset_shp(dataset_id):
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/geojson')
def export_geo_dataset_geojson(dataset_id):
    pass


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------