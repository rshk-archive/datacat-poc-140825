import flask

from datacat.web.blueprints.admin import admin_bp

app = flask.Flask(__name__)
app.register_blueprint(admin_bp, url_prefix='/api/1/admin')
