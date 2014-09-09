from collections import defaultdict
from flask import Blueprint


class Plugin(object):
    def __init__(self, import_name):
        """
        :param config:
            The main application configuration
        """
        self.import_name = import_name
        self._hooks = defaultdict(list)
        self._blueprint = None

    def setup(self, app):
        """Setup the plugin by attaching an application"""

        # Register blueprint, if any
        if self._blueprint is not None:
            app.register_blueprint(self._blueprint, url_prefix='/api/1')

        # Register all the plugin-defined celery tasks
        self._app = app
        if hasattr(app, 'celery'):
            for a, kw, func in self._tasks:
                app.celery.task(*a, **kw)(func)

    def hook(self, hook_type):
        """
        Decorator function to register a "hook" function, to be used later for
        various purposes.
        """

        def decorator(func):
            _hook_type = hook_type
            if not isinstance(_hook_type, (tuple, list)):
                _hook_type = (_hook_type,)
            for t in _hook_type:
                self._hooks[t].append(func)
            return func
        return decorator

    def call_hook(self, hook_type, *a, **kw):
        return [hook(*a, **kw) for hook in self._hooks.get(hook_type, [])]

    def route(self, *a, **kw):
        """
        Decorator function to register an API view for this plugin
        """

        if self._blueprint is None:
            self._blueprint = Blueprint(self.import_name, self.import_name)
        return self._blueprint.route(*a, **kw)

    def task(self, *a, **kw):
        """
        Decorator function to register a celery task
        """

        from datacat.core import celery_app
        return celery_app.task(*a, **kw)
