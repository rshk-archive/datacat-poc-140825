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


def make_app():
    app = Flask(__name__)
    app.register_blueprint(admin_bp, url_prefix='/api/1/admin')
    app.register_blueprint(public_bp, url_prefix='/api/1/data')
    app.config.update(make_config())
    return app


def make_celery(app):
    celery_app = Celery(app.import_name,
                        broker=app.config['CELERY_BROKER_URL'],
                        backend=app.config['CELERY_RESULT_BACKEND'])
    celery_app.conf.update(app.config)

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
        plugins.append(plugin)

        # Setup the plugin
        plugin.setup(app)

    return plugins


app = make_app()
celery_app = make_celery(app)
app.plugins = load_plugins(app)
