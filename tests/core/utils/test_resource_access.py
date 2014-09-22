import datetime
import os
import re
import urlparse

import pytest

from datacat.utils.resource_access import open_resource, ResourceAccessFailure


def test_open_internal_resource(configured_app_ctx):
    apptc = configured_app_ctx.test_client()
    DATA_PAYLOAD = '{"Hello": "World"}'

    # -------------------- Create a resource --------------------

    resp = apptc.post('/api/1/admin/resource/',
                      headers={'Content-type': 'application/json'},
                      data=DATA_PAYLOAD)
    assert resp.status_code == 201
    assert resp.data == ''
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/resource/([0-9]+)', path)
    resource_id = int(match.group(1))

    # -------------------- Now try opening it --------------------

    resource = open_resource('internal:///{0}'.format(resource_id))
    assert resource.open_resource().read() == DATA_PAYLOAD
    assert isinstance(resource.last_modified, datetime.datetime)
    assert resource.etag is None  # Not implemented yet..
    assert resource.content_type == 'application/json'


def test_open_http_resource(configured_app_ctx):
    resource = open_resource('http://httpbin.org/cache')
    assert isinstance(resource.last_modified, datetime.datetime)
    assert resource.etag is not None
    assert resource.content_type == 'application/json'

    # HTTPS resource, containing a redirect too..
    resource = open_resource(
        'https://github.com/rshk/datacat-poc-140825-testdata/'
        'raw/master/geodata/roads-folders.zip')
    assert isinstance(resource.last_modified, datetime.datetime) \
        or resource.last_modified is None
    assert resource.etag is not None  # GitHub returns a Etag: header
    assert resource.content_type == 'application/zip'


def test_save_resource_to_file(configured_app_ctx, tmpdir):
    filename = str(tmpdir.join('foobar.json'))

    resource = open_resource('http://httpbin.org/cache')
    with open(filename, 'wb') as fp:
        resource.save_to_file(fp)

    assert os.lstat(filename).st_size > 100


def test_open_unsupported_url(configured_app_ctx):
    with pytest.raises(ResourceAccessFailure):
        open_resource('invalid://foobar')
