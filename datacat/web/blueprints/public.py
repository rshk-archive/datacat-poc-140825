from flask import Blueprint, current_app
from werkzeug.exceptions import NotFound

from datacat.db import get_db
from datacat.web.utils import json_view
from datacat.utils.http import serve_resource

public_bp = Blueprint('public', __name__)


def make_dataset_metadata(dataset_id, config):
    """
    Create dataset metadata from some dataset configuration.
    """

    metadata = {}
    for plugin in current_app.plugins:
        plugin.call_hook('make_dataset_metadata', dataset_id, config, metadata)
    metadata['id'] = dataset_id
    return metadata


@public_bp.route('/', methods=['GET'])
@json_view
def get_dataset_index():
    # todo: add paging support
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM dataset
        ORDER BY id ASC
        """)
        return [make_dataset_metadata(x['id'], x['configuration'])
                for x in cur.fetchall()]


@public_bp.route('/<int:dataset_id>', methods=['GET'])
@json_view
def get_dataset(dataset_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset"
                    " WHERE id=%s;", (dataset_id,))
        result = cur.fetchone()

    if result is None:
        raise NotFound("Dataset not found: {0}".format(dataset_id))

    return make_dataset_metadata(result['id'], result['configuration'])


@public_bp.route('/resource/<int:resource_id>', methods=['GET'])
def serve_resource_data(resource_id):
    return serve_resource(resource_id)
