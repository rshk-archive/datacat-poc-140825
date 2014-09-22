from urlparse import urlparse

from flask import url_for
from werkzeug.exceptions import NotFound

from datacat.db import db
from datacat.ext.base import Plugin
from datacat.web.utils import json_view


core_plugin = Plugin(__name__)
core_plugin.__doc__ = """The core plugin"""


@core_plugin.hook('make_dataset_metadata')
def make_dataset_metadata(dataset_id, config, metadata):
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


# @core_plugin.route('/data/<int:dataset_id>/resource/<int:resource_id>')
# @json_view
# def get_dataset_resource(dataset_id, resource_id):
#     with db.cursor() as cur:
#         cur.execute("SELECT id, configuration FROM dataset WHERE id = %(id)s",
#                     dict(id=dataset_id))
#         row = cur.fetchone()
#         if row is None:
#             raise NotFound("The dataset was not found")
#         dataset_conf = row['configuration']

#     try:
#         resource_conf = dataset_conf['resources'][resource_id]

#     except (KeyError, IndexError):
#         raise NotFound("The resource was not found")

#     resource_type = resource_conf.get('type')
#     if resource_type == 'internal':
#         url = url_for('public.serve_resource_data',
#                       resource_id=resource_conf['id'],
#                       _external=True)

#     elif 'url' in resource_conf:
#         url = resource_conf['url']

#     else:
#         raise NotFound("Unable to find an URL for the resource")

#     return '', 302, {'Location': url}
#     # return redirect(url, code=302)


@core_plugin.task()
def dummy_task(name):
    open('/tmp/task-done', 'w').write('TASK DONE\n')
    return 'Hello, {0}!'.format(name)
