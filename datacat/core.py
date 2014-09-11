"""

Core module, responsible of creating the Flask and Celery application
objects.

"""

from celery import Celery
from flask import Flask, current_app
from flask.config import Config

from datacat.utils.plugin_loading import import_object
from datacat.web.blueprints.admin import admin_bp
from datacat.web.blueprints.public import public_bp


def make_flask_app(config=None):
    app = Flask('datacat')
    app.register_blueprint(admin_bp, url_prefix='/api/1/admin')
    app.register_blueprint(public_bp, url_prefix='/api/1/data')
    app.config.update(make_config())
    if config is not None:
        app.config.update(config)
    return app


def make_celery(config):
    # celery_app = Celery('datacat',
    #                     broker=config['CELERY_BROKER_URL'],
    #                     backend=config['CELERY_RESULT_BACKEND'])

    celery_app = celery_placeholder_app
    celery_app.broker = config['CELERY_BROKER_URL']
    # celery_app.backend = config['CELERY_RESULT_BACKEND']
    celery_app.conf.update(config)

    TaskBase = celery_app.Task

    class AppContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with current_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = AppContextTask
    return celery_app


def make_config():
    cfg = Config('')
    cfg.from_object('datacat.settings.default')
    cfg.from_envvar('DATACAT_SETTINGS', silent=True)
    return cfg


def load_plugins(app):
    plugins = []
    for name in app.config['PLUGINS']:
        # Instantiate plugin class
        plugin = import_object(name)
        plugin._import_name = name
        plugins.append(plugin)

        # Setup the plugin
        plugin.setup(app)

    return plugins


def finalize_app(app):
    """Prepare application for running"""

    from datacat.db import db_info

    with app.app_context():
        app.plugins = load_plugins(app)

        previously_enabled_plugins = set(db_info.get('core.plugins_enabled', []))  # noqa
        previously_installed_plugins = set(db_info.get('core.plugins_installed', []))  # noqa
        enabled_plugins = set(app.config['PLUGINS'])

        # ------------------------------------------------------------
        # Run the ``install()`` method for all the plugins that
        # were not previously installed
        plugins_to_install = enabled_plugins - previously_installed_plugins

        # ------------------------------------------------------------
        # Run the ``enable()`` method for all the plugins that
        # were not previously enabled
        plugins_to_enable = enabled_plugins - previously_enabled_plugins

        # ------------------------------------------------------------
        # Run the ``disable()`` method for all the plugins that
        # were previously enabled (and aren't anymore)
        plugins_to_disable = previously_enabled_plugins - enabled_plugins

        # Nothing will be uninstalled implicitly!

        # ------------------------------------------------------------
        # Perform the operations from above
        # ------------------------------------------------------------

        for plugin in app.plugins:
            if plugin._import_name in plugins_to_install:
                plugin.install()

            if plugin._import_name in plugins_to_enable:
                plugin.enable()

            if plugin._import_name in plugins_to_disable:
                plugin.disable()

            if plugin._import_name in enabled_plugins:
                plugin.upgrade()

        # ------------------------------------------------------------
        # Register new information about plugins

        db_info['core.plugins_enabled'] = list(enabled_plugins)
        db_info['core.plugins_installed'] = list(
            previously_installed_plugins | enabled_plugins)


def make_app(config=None):
    from datacat.db import create_tables, connect

    app = make_flask_app(config)
    celery_app = make_celery(app.config)
    celery_app.set_current()
    create_tables(connect(**app.config['DATABASE']))
    finalize_app(app)
    return app


celery_placeholder_app = Celery('datacat', set_as_current=False)
