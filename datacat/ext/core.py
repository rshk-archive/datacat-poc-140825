from urlparse import urlparse

from flask import url_for, current_app
from werkzeug.exceptions import NotFound

from datacat.db import db
from datacat.ext.base import Plugin
from datacat.web.utils import json_view


core_plugin = Plugin(__name__)
core_plugin.__doc__ = """
The core plugin, providing most of the "standard" functionality.
Having the core functionality in a plugins allows users to easily
extend and replace it to fit any custom needs.
"""


def _make_plugins_make_dataset_metadata(dataset_id, config):
    """
    Create dataset metadata, by asking plugins to contribute
    calling their ``make_dataset_metadata`` hook.
    """

    metadata = {}
    current_app.plugins.call_hook(
        'make_dataset_metadata', dataset_id, config, metadata)
    metadata['id'] = dataset_id
    return metadata


@core_plugin.hook('make_dataset_metadata')
def make_dataset_metadata(dataset_id, config, metadata):
    """
    :hook: make_dataset_metadata
    """

    if 'metadata' in config:
        metadata.update(config['metadata'])

    if 'resources' in config:
        metadata['resources'] = []
        for resource_id, resource in enumerate(config['resources']):
            if isinstance(resource, basestring):
                resource = {'url': resource}

            resource_url = resource['url']
            _parsed_url = urlparse(resource_url)
            if _parsed_url.scheme == 'internal':
                # We need to replace the URL with a public-facing one
                # TODO: we should use something more generic here..
                resource_url = url_for(
                    'public.serve_resource_data',
                    resource_id=int(_parsed_url.path.split('/')[1]),
                    _external=True)

            metadata['resources'].append({
                'url': resource_url,
            })


@core_plugin.route('/data/', methods=['GET'])
@json_view
def get_dataset_index():
    """
    API view returning a (paged) list of datasets.

    :HTTP url: ``/data/``
    :HTTP methods: ``GET``

    The view returns a list of dictionaries representing dataset
    objects.  The schema is entirely up to the enabled plugins; the
    core implementation only guarantees that the ``id`` field is set
    to the correct dataset id.

    **Example request:**

    .. code-block:: http

        GET /api/1/data/ HTTP/1.0

    **Example response:**

    .. code-block:: http

        HTTP/1.0 200 OK
        Content-type: application/json
        Link: ?start=10&size=10; rel=next, ?start=50&size=10; rel=last
        X-page-total: 60
        X-page-start: 0
        X-page-size: 10

    .. code-block:: python

            [{"id": 1}, {"id": 2}, {"id": 3}, ..., {"id": 10}]
    """
    # todo: add paging support
    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM dataset
        ORDER BY id ASC
        """)
        return [_make_plugins_make_dataset_metadata(x['id'], x['configuration'])
                for x in cur.fetchall()]


@core_plugin.route('/data/<int:dataset_id>', methods=['GET'])
@json_view
def get_dataset(dataset_id):
    """
    API view returning information for a single dataset.

    :HTTP url: ``/data/<dataset_id>``
    :HTTP methods: ``GET``

    **Example request:**

    .. code-block:: http

        GET /api/1/data/1 HTTP/1.0

    **Example response:**

    .. code-block:: http

        HTTP/1.0 200 OK
        Content-type: application/json

    .. code-block:: python

            {"id": 1, ...}
    """
    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset"
                    " WHERE id=%s;", (dataset_id,))
        result = cur.fetchone()

    if result is None:
        raise NotFound("Dataset not found: {0}".format(dataset_id))

    return _make_plugins_make_dataset_metadata(
        result['id'], result['configuration'])


@core_plugin.task(name='datacat.ext.core.dummy_task')
def dummy_task(name):
    """
    No-op Celery task, used for testing purposes.

    .. todo:: Move all the testing stuff to the testing plugin
    """
    return 'Hello, {0}!'.format(name)
