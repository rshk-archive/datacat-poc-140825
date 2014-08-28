"""
Administrative API for Datacat
"""

import json
from cgi import parse_header

from flask import Blueprint, request, url_for
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
    """
    We got some data to be stored as a new resource.

    Then we want to return 201 + URL of the created resource in the
    Location: header.
    """

    if 'Content-type' in request.headers:
        content_type, _ = parse_header(request.headers['Content-type'])
    else:
        content_type = 'application/octet-stream'

    db = get_db()

    # First, store the data in a PostgreSQL large object
    lobj = db.lobject(oid=0, mode='wb')
    oid = lobj.oid
    lobj.write(request.data)
    lobj.close()

    # Then, create a record for the metadata
    with db.cursor() as cur:
        cur.execute("""
        INSERT INTO "resource" (metadata, auto_metadata, mimetype, data_oid)
        VALUES ('{}', '{}', %(mimetype)s, %(oid)s)
        RETURNING id;
        """, dict(mimetype=content_type, oid=oid))
        resource_id = cur.fetchone()[0]

    db.commit()

    # Last, retun 201 + Location: header
    location = url_for('.get_resource_data', resource_id=resource_id)
    return '', 201, {'Location': location}


@admin_bp.route('/resource/<int:resource_id>', methods=['GET'])
def get_resource_data(resource_id):
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, mimetype, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        return '', 404

    # todo: better use a streaming response here..?
    lobject = db.lobject(oid=resource['data_oid'], mode='rb')
    data = lobject.read()
    lobject.close()

    return data, 200, {'Content-type': resource['mimetype']}


@admin_bp.route('/resource/<int:resource_id>', methods=['PUT'])
def put_resource_data(resource_id):

    if 'Content-type' in request.headers:
        content_type, _ = parse_header(request.headers['Content-type'])
    else:
        content_type = 'application/octet-stream'

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        return '', 404

    # todo: better use a streaming response here..?
    lobj = db.lobject(oid=resource['data_oid'], mode='wb')
    lobj.seek(0)
    lobj.truncate()
    lobj.write(request.data)
    lobj.close()

    # Then, create a record for the metadata
    with db.cursor() as cur:
        cur.execute("""
        UPDATE "resource" SET mimetype=%(mimetype)s WHERE id=%(id)s;
        """, dict(mimetype=content_type, id=resource_id))

    db.commit()
    return '', 200


@admin_bp.route('/resource/<int:resource_id>', methods=['DELETE'])
def delete_resource_data(resource_id):
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    # todo: better use a streaming response here..?
    lobj = db.lobject(oid=resource['data_oid'], mode='wb')
    lobj.unlink()

    # Then, create a record for the metadata
    with db.cursor() as cur:
        cur.execute("""
        DELETE FROM "resource" WHERE id=%(id)s;
        """, dict(id=resource_id))

    db.commit()
    return '', 200
