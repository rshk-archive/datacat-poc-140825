Plugins interface
#################

Plugins are used to extend the application functionality, by offering
functionality such as:

- add views to the API, through a blueprint
- expose some "hooks" that will be called in other parts of the application
- expose celery tasks


.. todo:: We need to figure out a better way to register tasks: the
          decorator must return a Task object for things to work;
          better, it should return a task wrapping an application
          context. Problem is, we don't have an application yet at
          task definition time..


.. py:module:: datacat.ext.base


.. autoclass:: Plugin
    :members:
    :special-members: __init__
    :undoc-members:


Example plugin
==============

.. code-block:: python

    from flask import url_for
    from werkzeug.exceptions import NotFound

    from datacat.db import get_db
    from datacat.ext.base import Plugin
    from datacat.web.utils import json_view


    core_plugin = Plugin(__name__)


    @core_plugin.hook('dataset_create')
    def on_dataset_create(dataset_id, config):
	# A dataset was created -- let's do something!
        do_something_with_dataset.delay(dataset_id)

    @core_plugin.hook('dataset_create')
    def do_something_with_dataset(dataset_id, config):
        pass

    @core_plugin.route('/data/<int:dataset_id>/my-custom-view')
    @json_view
    def get_dataset_custom_view(dataset_id):
        # Return something to the user..
	return {'message': 'Hello, world!'}
