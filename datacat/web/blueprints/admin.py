"""
Administrative API for Datacat
"""

from flask import Blueprint
from flask.ext import restful

admin_bp = Blueprint('admin', __name__)
admin_api = restful.Api(admin_bp)


class ResourceIndex(restful.Resource):
    def get(self):
        """List or search resources"""
        # todo: add support for pagination
        pass

    def post(self):
        """Create a new resource, from **data**"""
        pass


class ResourceData(restful.Resource):
    def get(self, resource_id):
        """Get some data from the resources storage"""
        pass

    def put(self, resource_id):
        """Put some data in the resources storage"""
        pass

    def delete(self, resource_id):
        pass


class ResourceMetadata(restful.Resource):
    def get(self, resource_id):
        pass

    def put(self, resource_id):
        pass

    def patch(self, resource_id):
        pass


admin_api.add_resource(ResourceIndex, '/resource/')
admin_api.add_resource(ResourceData, '/resource/<int:resource_id>')
admin_api.add_resource(ResourceMetadata, '/resource/<int:resource_id>/meta')
