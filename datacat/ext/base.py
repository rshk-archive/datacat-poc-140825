from collections import defaultdict
from flask import Blueprint


class Plugin(object):
    def __init__(self, import_name):
        """
        :param import_name:
            Usually the name of the module concatenated with the
            plugin name, eg::

                myplugin = Plugin(__name__ + '.myplugin')
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

    def install(self):
        """
        Method called to install the plugin, i.e. the first time it appears
        in the ``PLUGINS`` list.
        """
        pass

    def uninstall(self):
        """
        Method called to completely uninstall a plugin.

        It should be called via some administration CLI command.
        """
        pass

    def enable(self):
        """
        Method called when a plugin gets enabled, i.e. when it appears
        in the ``PLUGINS`` list after it was missing.
        """
        pass

    def disable(self):
        """
        Method called when a plugin gets disabled, i.e. when it disappears
        from the ``PLUGINS`` list.
        """
        pass

    def upgrade(self):
        """
        Perform necessary database schema upgrades.
        """

        from datacat.db import db_info

        schema_version_key = 'plugin.{0}.schema_version'\
            .format(self.import_name)

        current_version = db_info.get(schema_version_key, -1)
        upgrade_methods = self._get_upgrade_methods()  # Must be sorted!
        for upgrade_id, method in upgrade_methods:
            if upgrade_id > current_version:
                method()
                db_info[schema_version_key] = upgrade_id

    def _get_upgrade_methods(self):
        found = []
        for name in dir(self):
            if name.startswith('upgrade_'):
                method = getattr(self, name)
                if not hasattr(method, '__call__'):
                    continue
                upgrade_id = int(name[len('upgrade_'):])
                found.append((upgrade_id, method))
        found.sort()
        return found

    def hook(self, hook_type):
        """
        Decorator function to register a "hook" function, to be used later for
        various purposes.

        :param hook_type:
            A string (or list/tuple of) indicating the hook(s) to which
            the handler should be attached

        :type hook_type:
            str, list, tuple
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
        """
        Helper function to call all the handlers for a given hook
        type in this plugin.

        Extra arguments will be passed directly to the hook handler(s)

        :param hook_type: The hook type
        :return: a list of return values for all the called handlers

        .. todo:: Make this a generator -> update tests
        """
        return [hook(*a, **kw) for hook in self._hooks.get(hook_type, [])]

    def route(self, *a, **kw):
        """
        Decorator function to register an API view for this plugin.

        The underlying `Blueprint.route()
        <http://flask.pocoo.org/docs/latest/api/#flask.Blueprint.route>`_
        method will be called.

        Blueprints are then registered under the ``/api/1/`` prefix.
        """

        if self._blueprint is None:
            self._blueprint = Blueprint(self.import_name, self.import_name)
        return self._blueprint.route(*a, **kw)

    def task(self, *a, **kw):
        """
        Decorator function to register a celery task.

        .. note:: Tasks should be registered with their full namespace, eg:

            .. code-block:: python

                @myplugin.task(name=__name__ + '.mytask')
                def mytask(foo, bar):
                    pass

        .. todo:: Automate prefixing name with ``__name__``
        """

        from datacat.core import celery_placeholder_app
        return celery_placeholder_app.task(*a, **kw)
