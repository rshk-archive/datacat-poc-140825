"""
Administrative API for Datacat
"""

from cgi import parse_header
import json

from flask import Blueprint, request, url_for
from werkzeug.exceptions import NotFound

from datacat.db import get_db
from datacat.web.utils import json_view, _get_json_from_request

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/resource/', methods=['GET'])
@json_view
def get_resource_index():
    # todo: add paging support
    db = get_db()
    with db, db.cursor() as cur:
        cur.execute("""
        SELECT id, metadata, mimetype FROM resource
        ORDER BY id ASC
        """)
        return list({'id': x['id'],
                     'metadata': x['metadata'],
                     'mimetype': x['mimetype'],
                     }
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

    db = get_db()

    # First, store the data in a PostgreSQL large object
    with db:
        lobj = db.lobject(oid=0, mode='wb')
        oid = lobj.oid
        lobj.write(request.data)
        lobj.close()

    # Then, create a record for the metadata
    with db, db.cursor() as cur:
        cur.execute("""
        INSERT INTO "resource" (metadata, auto_metadata, mimetype, data_oid)
        VALUES ('{}', '{}', %(mimetype)s, %(oid)s)
        RETURNING id;
        """, dict(mimetype=content_type, oid=oid))
        resource_id = cur.fetchone()[0]

    # Last, retun 201 + Location: header
    location = url_for('.get_resource_data', resource_id=resource_id)
    return '', 201, {'Location': location}


@admin_bp.route('/resource/<int:resource_id>', methods=['GET'])
def get_resource_data(resource_id):
    # We can just redirect to the endpoint serving resource data
    return '', 301, {'Location': url_for('public.serve_resource_data',
                                         resource_id=resource_id,
                                         _external=True)}


@admin_bp.route('/resource/<int:resource_id>', methods=['PUT'])
def put_resource_data(resource_id):
    content_type = 'application/octet-stream'
    if request.headers.get('Content-type'):
        content_type, _ = parse_header(request.headers['Content-type'])

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, data_oid FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    # todo: better use a streaming response here..?
    with db:
        lobj = db.lobject(oid=resource['data_oid'], mode='wb')
        lobj.seek(0)
        lobj.truncate()
        lobj.write(request.data)
        lobj.close()

    # Then, create a record for the metadata
    with db, db.cursor() as cur:
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
    with db:
        lobj = db.lobject(oid=resource['data_oid'], mode='wb')
        lobj.unlink()

    # Then, create a record for the metadata
    with db, db.cursor() as cur:
        cur.execute("""
        DELETE FROM "resource" WHERE id=%(id)s;
        """, dict(id=resource_id))

    db.commit()
    return '', 200


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['GET'])
@json_view
def get_resource_metadata(resource_id):
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, metadata FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    return resource['metadata']


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['PUT'])
def put_resource_metadata(resource_id):
    new_metadata = _get_json_from_request()

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, metadata FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound('This resource does not exist')

    with db, db.cursor() as cur:
        cur.execute("""
        UPDATE "resource" SET metadata=%(meta)s::json WHERE id = %(id)s;
        """, dict(id=resource_id, meta=json.dumps(new_metadata)))

    return '', 200


@admin_bp.route('/resource/<int:resource_id>/meta', methods=['PATCH'])
def patch_resource_metadata(resource_id):
    new_metadata = _get_json_from_request()

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, metadata FROM "resource" WHERE id = %(id)s;
        """, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound('This resource does not exist')

    _meta = resource['metadata']
    _meta.update(new_metadata)

    with db, db.cursor() as cur:
        cur.execute("""
        UPDATE "resource" SET metadata=%(meta)s::json WHERE id = %(id)s;
        """, dict(id=resource_id, meta=json.dumps(_meta)))

    return '', 200


# ======================================================================
# Dataset configuration CRUD
# ======================================================================


@admin_bp.route('/dataset/', methods=['GET'])
@json_view
def get_dataset_index():
    # todo: add paging support
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM dataset
        ORDER BY id ASC
        """)
        return list({'id': x['id'],
                     'configuration': x['configuration']}
                    for x in cur.fetchall())


@admin_bp.route('/dataset/', methods=['POST'])
def post_dataset_index():
    content_type = 'application/octet-stream'
    if request.headers.get('Content-type'):
        content_type, _ = parse_header(request.headers['Content-type'])

    data = _get_json_from_request()

    db = get_db()
    with db, db.cursor() as cur:
        cur.execute("""
        INSERT INTO "dataset" (configuration)
        VALUES (%s::json)
        RETURNING id;
        """, (json.dumps(data),))
        dataset_id = cur.fetchone()[0]

    # Last, retun 201 + Location: header
    location = url_for('.get_dataset_configuration', dataset_id=dataset_id)
    return '', 201, {'Location': location}


@admin_bp.route('/dataset/<int:dataset_id>', methods=['GET'])
@json_view
def get_dataset_configuration(dataset_id):
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM "dataset" WHERE id = %(id)s;
        """, dict(id=dataset_id))
        dataset = cur.fetchone()

    if dataset is None:
        raise NotFound()

    return dataset['configuration']


@admin_bp.route('/dataset/<int:dataset_id>', methods=['PUT'])
def put_dataset_configuration(dataset_id):
    data = _get_json_from_request()
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM "dataset" WHERE id = %(id)s;
        """, dict(id=dataset_id))
        dataset = cur.fetchone()

    if dataset is None:
        raise NotFound()

    with db, db.cursor() as cur:
        cur.execute("""
        UPDATE "dataset"
        SET configuration=%(configuration)s::json
        WHERE id=%(id)s;
        """, dict(id=dataset_id, configuration=json.dumps(data)))

    return '', 200


@admin_bp.route('/dataset/<int:dataset_id>', methods=['PATCH'])
def patch_dataset_configuration(dataset_id):
    data = _get_json_from_request()
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
        SELECT id, configuration FROM "dataset" WHERE id = %(id)s;
        """, dict(id=dataset_id))
        dataset = cur.fetchone()

    if dataset is None:
        raise NotFound()

    new_meta = dataset['configuration']
    new_meta.update(data)

    with db, db.cursor() as cur:
        cur.execute("""
        UPDATE "dataset"
        SET configuration=%(configuration)s::json
        WHERE id=%(id)s;
        """, dict(id=dataset_id, configuration=json.dumps(new_meta)))

    return '', 200


@admin_bp.route('/dataset/<int:dataset_id>', methods=['DELETE'])
def delete_dataset_configuration(dataset_id):
    db = get_db()
    with db, db.cursor() as cur:
        cur.execute("""
        DELETE FROM "dataset" WHERE id = %(id)s;
        """, dict(id=dataset_id))

    return '', 200
