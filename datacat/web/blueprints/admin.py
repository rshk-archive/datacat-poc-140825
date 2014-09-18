"""
Administrative API for Datacat
"""

from cgi import parse_header
import datetime
import json
import hashlib

from flask import Blueprint, request, url_for, current_app
from werkzeug.exceptions import NotFound

from datacat.db import db
from datacat.db import querybuilder
from datacat.utils.const import DATE_FORMAT, HTTP_DATE_FORMAT
from datacat.web.utils import json_view, _get_json_from_request

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/resource/', methods=['GET'])
@json_view
def get_resource_index():
    # todo: add paging support
    with db, db.cursor() as cur:
        cur.execute("""
        SELECT id, metadata, mimetype, mtime, ctime FROM resource
        ORDER BY id ASC
        """)
        return list({'id': x['id'],
                     'metadata': x['metadata'],
                     'mimetype': x['mimetype'],
                     'ctime': x['ctime'].strftime(DATE_FORMAT),
                     'mtime': x['mtime'].strftime(DATE_FORMAT)}
                    for x in cur.fetchall())


@admin_bp.route('/resource/', methods=['POST'])
def post_resource_index():
    """
    We got some data to be stored as a new resource.

    Then we want to return 201 + URL of the created resource in the
    Location: header.
    """

    content_type = 'application/octet-stream'
    if request.headers.get('Content-type'):
        content_type, _ = parse_header(request.headers['Content-type'])

    # First, store the data in a PostgreSQL large object
    with db, db.cursor() as cur:
        lobj = db.lobject(oid=0, mode='wb')
        oid = lobj.oid
        lobj.write(request.data)
        lobj.close()

        resource_hash = 'sha1:' + hashlib.sha1(request.data).hexdigest()

        data = dict(
            metadata='{}',
            auto_metadata='{}',
            mimetype=content_type,
            data_oid=oid,
            ctime=datetime.datetime.utcnow(),
            mtime=datetime.datetime.utcnow(),
            hash=resource_hash)

        # Then, create a record for the metadata
        query = querybuilder.insert('resource', data)
        cur.execute(query, data)
        resource_id = cur.fetchone()[0]

    # Last, retun 201 + Location: header
    location = url_for('.get_resource_data', resource_id=resource_id)
    return '', 201, {'Location': location}


@admin_bp.route('/resource/<int:resource_id>', methods=['GET'])
def get_resource_data(resource_id):
    """
    Just redirect to the endpoint in the public API serving resource data.
    Note that in the future we might want to change this behavior if we
    want to keep some resources "private".
    """

    dest_url = url_for('public.serve_resource_data',
                       resource_id=resource_id, _external=True)
    return '', 301, {'Location': dest_url}


@admin_bp.route('/resource/<int:resource_id>', methods=['PUT'])
def put_resource_data(resource_id):
    content_type = 'application/octet-stream'
    if request.headers.get('Content-type'):
        content_type, _ = parse_header(request.headers['Content-type'])

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    # todo: better use a streaming response here..?
    with db, db.cursor() as cur:
        lobj = db.lobject(oid=resource['data_oid'], mode='wb')
        lobj.seek(0)
        lobj.truncate()
        lobj.write(request.data)
        lobj.close()

        resource_hash = 'sha1:' + hashlib.sha1(request.data).hexdigest()

        data = dict(
            id=resource_id,
            mimetype=content_type,
            mtime=datetime.datetime.utcnow(),
            hash=resource_hash)

        query = querybuilder.update('resource', data)
        cur.execute(query, data)

    return '', 200


@admin_bp.route('/resource/<int:resource_id>', methods=['DELETE'])
def delete_resource_data(resource_id):
    with db.cursor() as cur:
        cur.execute("""
        SELECT id, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    # todo: better use a streaming response here..?
    with db:
        lobj = db.lobject(oid=resource['data_oid'], mode='wb')
        lobj.unlink()

    # Then, create a record for the metadata
    with db, db.cursor() as cur:
        query = querybuilder.delete('resource')
        cur.execute(query, dict(id=resource_id))

    db.commit()
    return '', 200


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['GET'])
@json_view
def get_resource_metadata(resource_id):
    with db.cursor() as cur:
        query = querybuilder.select_pk('resource', fields='id, metadata')
        cur.execute(query, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    return resource['metadata']


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['PUT'])
def put_resource_metadata(resource_id):
    new_metadata = _get_json_from_request()

    with db.cursor() as cur:
        query = querybuilder.select_pk('resource', fields='id, metadata')
        cur.execute(query, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound('This resource does not exist')

    with db, db.cursor() as cur:
        data = dict(
            id=resource_id,
            metadata=json.dumps(new_metadata))
        query = querybuilder.update('resource', data)
        cur.execute(query, data)

    return '', 200


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['PATCH'])
def patch_resource_metadata(resource_id):
    new_metadata = _get_json_from_request()

    with db.cursor() as cur:
        query = querybuilder.select_pk('resource', fields='id, metadata')
        cur.execute(query, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound('This resource does not exist')

    _meta = resource['metadata']
    _meta.update(new_metadata)

    with db, db.cursor() as cur:
        data = dict(
            id=resource_id,
            metadata=json.dumps(_meta))
        query = querybuilder.update('resource', data)
        cur.execute(query, data)

    return '', 200


# ======================================================================
# Dataset configuration CRUD
# ======================================================================


@admin_bp.route('/dataset/', methods=['GET'])
@json_view
def get_dataset_index():
    # todo: add paging support

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration, ctime, mtime FROM dataset
        ORDER BY id ASC
        """)
        return list({'id': x['id'],
                     'configuration': x['configuration'],
                     'ctime': x['ctime'].strftime(DATE_FORMAT),
                     'mtime': x['mtime'].strftime(DATE_FORMAT)}
                    for x in cur.fetchall())


@admin_bp.route('/dataset/', methods=['POST'])
def post_dataset_index():
    content_type = 'application/octet-stream'
    if request.headers.get('Content-type'):
        content_type, _ = parse_header(request.headers['Content-type'])

    data = _get_json_from_request()

    with db, db.cursor() as cur:
        cur.execute("""
        INSERT INTO "dataset" (configuration, ctime, mtime)
        VALUES (%(conf)s::json, %(mtime)s, %(mtime)s)
        RETURNING id;
        """, dict(conf=json.dumps(data), mtime=datetime.datetime.utcnow()))
        dataset_id = cur.fetchone()[0]

    for plugin in current_app.plugins:
        plugin.call_hook('dataset_create', dataset_id, data)

    # Last, retun 201 + Location: header
    location = url_for('.get_dataset_configuration', dataset_id=dataset_id)
    return '', 201, {'Location': location}


def _get_dataset_record(dataset_id):
    with db.cursor() as cur:
        query = querybuilder.select_pk('dataset')
        cur.execute(query, dict(id=dataset_id))
        dataset = cur.fetchone()
    if dataset is None:
        raise NotFound()
    return dataset


def _update_dataset_record(dataset_id, **fields):
    if 'configuration' in fields:
        fields['configuration'] = json.dumps(fields['configuration'])
    fields['mime'] = datetime.datetime.utcnow()
    query = querybuilder.update('dataset', fields)

    with db, db.cursor() as cur:
        cur.execute(query, fields)

    for plugin in current_app.plugins:
        plugin.call_hook('dataset_update', dataset_id, fields)


@admin_bp.route('/dataset/<int:dataset_id>', methods=['GET'])
@json_view
def get_dataset_configuration(dataset_id):
    dataset = _get_dataset_record(dataset_id)
    headers = {
        'Last-modified': dataset['mtime'].strftime(HTTP_DATE_FORMAT),
    }
    return dataset['configuration'], 200, headers


@admin_bp.route('/dataset/<int:dataset_id>', methods=['PUT'])
def put_dataset_configuration(dataset_id):
    _get_dataset_record(dataset_id)  # Make sure it exists
    user_conf = _get_json_from_request()
    _update_dataset_record(dataset_id, user_conf)
    return '', 200


@admin_bp.route('/dataset/<int:dataset_id>', methods=['PATCH'])
def patch_dataset_configuration(dataset_id):
    user_conf = _get_json_from_request()
    dataset = _get_dataset_record(dataset_id)
    new_meta = dataset['configuration']
    new_meta.update(user_conf)
    _update_dataset_record(dataset_id, new_meta)
    return '', 200


@admin_bp.route('/dataset/<int:dataset_id>', methods=['DELETE'])
def delete_dataset_configuration(dataset_id):
    with db, db.cursor() as cur:
        query = querybuilder.delete('dataset')
        cur.execute(query, dict(id=dataset_id))

    for plugin in current_app.plugins:
        plugin.call_hook('dataset_delete', dataset_id)

    return '', 200
