"""
The Public API blueprint provides "common" public functionality.

At the moment, it provides a view to serve internal resource data.
"""

from flask import Blueprint

from datacat.utils.http import serve_resource

public_bp = Blueprint('public', __name__)


@public_bp.route('/resource/<int:resource_id>', methods=['GET'])
def serve_resource_data(resource_id):
    return serve_resource(resource_id)
