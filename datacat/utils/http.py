from datetime import datetime

from flask import request, Response
from werkzeug.exceptions import NotFound, BadRequest

from datacat.db import db, querybuilder
from datacat.utils.const import HTTP_DATE_FORMAT


def serve_resource(resource_id, transfer_block_size=4096):
    """
    Serve resource data via HTTP, setting ETag and Last-Modified headers
    and honoring ``If-None-Match`` and ``If-modified-since`` headers.

    Currently supported features:

    - Set ``ETag`` header (to the hash of resource body)
    - Set ``Last-Modified`` header (to the last modification date)
    - Honor the ``If-modified-since`` header (if the resource was not
      modified, return 304)

    Planned features:

    - Return response as a stream, to avoid loading everything in memory.
    - Honor the ``If-Match`` / ``If-None-Match`` headers
    - Support ``Range`` requests + 206 partial response
    - Set ``Cache-control`` and ``Expire`` headers (?)
    - Properly support HEAD requests.

    :param resource_id:
        Id of the resource to be served

    :param transfer_block_size:
        Size of the streaming response size. Defaults to 4096 bytes.

    :return:
        A valid return value for a Flask view.
    """

    with db, db.cursor() as cur:
        query = querybuilder.select_pk(
            'resource', fields='id, mimetype, data_oid, mtime, hash')
        cur.execute(query, dict(id=resource_id))
        resource = cur.fetchone()

    if resource is None:
        raise NotFound()

    mimetype = resource['mimetype'] or 'application/octet-stream'
    headers = {
        'Content-type': mimetype,
        'Last-modified': resource['mtime'].strftime(HTTP_DATE_FORMAT),
        'ETag': resource['hash'],
    }

    # ------------------------------------------------------------
    # Check the if-modified-since header

    if 'if-modified-since' in request.headers:
        try:
            if_modified_since_date = datetime.strptime(
                request.headers['if-modified-since'],
                HTTP_DATE_FORMAT)
        except:
            raise BadRequest("Invalid If-Modified-Since header value")

        if if_modified_since_date >= resource['mtime']:
            # The resource was not modified -> return ``304 NOT MODIFIED``
            return Response('', status=304, headers=headers)

    # ------------------------------------------------------------
    # Stream the response data

    with db:
        lobject = db.lobject(oid=resource['data_oid'], mode='rb')
        data = lobject.read()
        lobject.close()

    return Response(data, status=200, headers=headers)

    # def generate_data():
    #     with db:
    #         lobject = db.lobject(oid=resource['data_oid'], mode='rb')
    #         while True:
    #             data = lobject.read(transfer_block_size)
    #             if not data:
    #                 break
    #             yield data
    #         lobject.close()

    # return Response(generate_data(), status=200, headers=headers)
