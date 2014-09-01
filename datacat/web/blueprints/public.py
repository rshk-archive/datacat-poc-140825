from cgi import parse_header
import json

from flask import Blueprint, request, url_for
from werkzeug.exceptions import NotFound

from datacat.db import get_db
from datacat.web.utils import json_view, _get_json_from_request

public_bp = Blueprint('public', __name__)


def make_dataset_metadata(id, config):
    """
    Create dataset metadata from some dataset configuration.
    """

    metadata = {}
    metadata.update(config.get('metadata'), {})
    metadata['resources'] = []
    for resource_conf in config.get('resources', []):
        if resource_conf['type'] == 'resource':
            # We want to link to an internal resource directly
            pass
        pass
    metadata['id'] = id
    return metadata


@public_bp.route('/dataset/', methods=['GET'])
@json_view
def get_dataset_index():
    # todo: add paging support
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset")
        return [make_dataset_metadata(x['id'], x['configuration'])
                for x in cur.fetchall()]


@public_bp.route('/dataset/', methods=['GET'])
@json_view
def get_dataset():
    # todo: add paging support
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset")
        return [make_dataset_metadata(x['id'], x['configuration'])
                for x in cur.fetchall()]
