import flask

from datacat.web.blueprints.admin import admin_bp
from datacat.web.blueprints.public import public_bp
from datacat.utils.plugin_loading import get_plugin_class


def make_app():
    app = flask.Flask(__name__)
    app.register_blueprint(admin_bp, url_prefix='/api/1/admin')
    app.register_blueprint(public_bp, url_prefix='/api/1/data')

    app.config.from_object('datacat.settings.default')
    app.config.from_envvar('DATACAT_SETTINGS', silent=True)

    app.plugins = []
    for name in app.config['PLUGINS']:
        # Instantiate plugin class
        klass = get_plugin_class(name)
        plugin = klass(app.config)
        app.plugins.append(plugin)

        # Setup
        plugin.setup()

        # Add blueprint, if the plugin provides one
        if plugin.blueprint is not None:
            app.register_blueprint(
                plugin.blueprint,
                url_prefix='/api/1/data/<int:dataset_id>')

    return app


app = make_app()
