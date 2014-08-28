"""
Administrative API for Datacat
"""

import json

from flask import Blueprint
# from flask.ext import restful

from datacat.db import get_db

admin_bp = Blueprint('admin', __name__)
# admin_api = restful.Api(admin_bp)


def _json_response(data, code=200, headers=None):
    _headers = {}
    if headers is not None:
        _headers.update(headers)
    _headers['Content-type'] = 'application/json'
    _data = json.dumps(data)
    return _data, code, _headers


@admin_bp.route('/resource/', methods=['GET'])
def get_resource_index():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM resource")
        return _json_response(list(cur.fetchall()))


@admin_bp.route('/resource/', methods=['POST'])
def post_resource_index():
    pass


@admin_bp.route('/resource/<int:resource_id>', methods=['GET'])
def get_resource_data(resource_id):
    pass


@admin_bp.route('/resource/<int:resource_id>', methods=['PUT'])
def put_resource_data(resource_id):
    pass


@admin_bp.route('/resource/<int:resource_id>', methods=['DELETE'])
def delete_resource_data(resource_id):
    pass


# class ResourceIndex(restful.Resource):
#     def get(self):
#         """List or search resources"""
#         # todo: add support for pagination
#         pass

#     def post(self):
#         """Create a new resource, from **data**"""
#         pass


# class ResourceData(restful.Resource):
#     def get(self, resource_id):
#         """Get some data from the resources storage"""
#         pass

#     def put(self, resource_id):
#         """Put some data in the resources storage"""
#         pass

#     def delete(self, resource_id):
#         pass


# class ResourceMetadata(restful.Resource):
#     def get(self, resource_id):
#         pass

#     def put(self, resource_id):
#         pass

#     def patch(self, resource_id):
#         pass


# admin_api.add_resource(ResourceIndex, '/resource/')
# admin_api.add_resource(ResourceData, '/resource/<int:resource_id>')
# admin_api.add_resource(ResourceMetadata, '/resource/<int:resource_id>/meta')
