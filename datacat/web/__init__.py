import celery
import flask

from datacat.web.blueprints.admin import admin_bp
from datacat.web.blueprints.public import public_bp
from datacat.utils.plugin_loading import import_object


def make_app():
    app = flask.Flask(__name__)
    app.register_blueprint(admin_bp, url_prefix='/api/1/admin')
    app.register_blueprint(public_bp, url_prefix='/api/1/data')

    app.config.from_object('datacat.settings.default')
    app.config.from_envvar('DATACAT_SETTINGS', silent=True)

    app.celery = celery.Celery(app.import_name,
                               broker=app.config['CELERY_BROKER_URL'])
    app.celery.conf.update(app.config)

    app.plugins = []
    for name in app.config['PLUGINS']:
        # Instantiate plugin class
        plugin = import_object(name)
        app.plugins.append(plugin)

        # Setup the plugin
        plugin.setup(app)

    return app


app = make_app()
