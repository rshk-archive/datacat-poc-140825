import json
import re
import urlparse


def test_resource_empty_listing(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/resource/')
    assert resp.status_code == 200
    assert json.loads(resp.data) == []


def test_resource_crud(configured_app):
    apptc = configured_app.test_client()
    DATA_PAYLOAD = json.dumps({'Hello': 'World'})

    # ------------------------------------------------------------
    # Create a new resource
    # ------------------------------------------------------------

    resp = apptc.post('/api/1/admin/resource/',
                      headers={'Content-type': 'application/json'},
                      data=DATA_PAYLOAD)
    assert resp.status_code == 201
    assert resp.data == ''
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/resource/([0-9]+)', path)
    resource_id = int(match.group(1))

    # ------------------------------------------------------------
    # Get it back and check
    # ------------------------------------------------------------

    resp = apptc.get('/api/1/admin/resource/{0}'.format(resource_id))
    assert resp.status_code == 301
    path = urlparse.urlparse(resp.headers['Location']).path
    assert path == '/api/1/data/resource/{0}'.format(resource_id)

    resp = apptc.get(resp.headers['Location'])
    assert resp.status_code == 200
    assert resp.data == DATA_PAYLOAD
    assert resp.headers['Content-type'] == 'application/json'

    # Make sure it is listed in the index
    resp = apptc.get('/api/1/admin/resource/')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == resource_id
    assert data[0]['metadata'] == {}
    assert data[0]['mimetype'] == 'application/json'

    # ------------------------------------------------------------
    # Update and make sure it is updated
    # ------------------------------------------------------------

    resp = apptc.put('/api/1/admin/resource/{0}'.format(resource_id),
                     headers={'Content-type': 'text/plain'},
                     data='HELLO WORLD')
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}'.format(resource_id))
    assert resp.status_code == 301
    path = urlparse.urlparse(resp.headers['Location']).path
    assert path == '/api/1/data/resource/{0}'.format(resource_id)

    resp = apptc.get(resp.headers['Location'])
    assert resp.status_code == 200
    assert resp.data == 'HELLO WORLD'
    assert resp.headers['Content-type'] == 'text/plain'

    # ------------------------------------------------------------
    # Delete and make sure it's gone
    # ------------------------------------------------------------

    resp = apptc.delete('/api/1/admin/resource/{0}'.format(resource_id))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}'.format(resource_id))
    assert resp.status_code == 301
    path = urlparse.urlparse(resp.headers['Location']).path
    assert path == '/api/1/data/resource/{0}'.format(resource_id)

    resp = apptc.get(resp.headers['Location'])
    assert resp.status_code == 404

    # Make sure it is not listed in the index anymore
    resp = apptc.get('/api/1/admin/resource/')
    assert resp.status_code == 200
    assert json.loads(resp.data) == []


def test_resource_create_default_mime(configured_app):
    apptc = configured_app.test_client()

    # ------------------------------------------------------------
    # Create a new resource
    # ------------------------------------------------------------

    resp = apptc.post('/api/1/admin/resource/',
                      headers={},
                      data='Some data')
    assert resp.status_code == 201
    assert resp.data == ''
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/resource/([0-9]+)', path)
    resource_id = int(match.group(1))

    # ------------------------------------------------------------
    # Get it back and check
    # ------------------------------------------------------------

    resp = apptc.get('/api/1/admin/resource/{0}'.format(resource_id))
    assert resp.status_code == 301
    path = urlparse.urlparse(resp.headers['Location']).path
    assert path == '/api/1/data/resource/{0}'.format(resource_id)

    resp = apptc.get(resp.headers['Location'])
    assert resp.status_code == 200
    assert resp.data == 'Some data'
    assert resp.headers['Content-type'] == 'application/octet-stream'


def test_resource_error_404(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/resource/12345')
    assert resp.status_code == 301

    resp = apptc.get(resp.headers['Location'])
    assert resp.status_code == 404

    resp = apptc.put('/api/1/admin/resource/12345', data='foobar')
    assert resp.status_code == 404


def test_resource_metadata_crud(configured_app):
    apptc = configured_app.test_client()

    # ------------------------------------------------------------
    # We need to put some data first

    resp = apptc.post('/api/1/admin/resource/',
                      headers={'Content-type': 'application/json'},
                      data='{"Hello": "World"}')
    assert resp.status_code == 201
    assert resp.data == ''
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/resource/([0-9]+)', path)
    resource_id = int(match.group(1))

    # ------------------------------------------------------------
    # Initial metadata should be empty

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {}

    # ------------------------------------------------------------
    # PUT metadata

    resp = apptc.put('/api/1/admin/resource/{0}/meta'.format(resource_id),
                     headers={'Content-type': 'application/json'},
                     data=json.dumps({'key1': 'FOO', 'key2': 'BAR'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'key1': 'FOO', 'key2': 'BAR'}

    # ------------------------------------------------------------
    # PATCH metadata (update some keys)

    resp = apptc.patch('/api/1/admin/resource/{0}/meta'.format(resource_id),
                       headers={'Content-type': 'application/json'},
                       data=json.dumps({'key1': 'FOOBAR'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'key1': 'FOOBAR', 'key2': 'BAR'}

    # ------------------------------------------------------------
    # PUT metadata

    resp = apptc.put('/api/1/admin/resource/{0}/meta'.format(resource_id),
                     headers={'Content-type': 'application/json'},
                     data=json.dumps({'key1': 'BAZ'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'key1': 'BAZ'}


def test_resource_metadata_crud_errors(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/resource/12345/meta')
    assert resp.status_code == 404

    resp = apptc.put('/api/1/admin/resource/12345/meta', data='{}',
                     headers={'Content-type': 'application/json'})
    assert resp.status_code == 404

    resp = apptc.put('/api/1/admin/resource/12345/meta', data='INVALID-JSON',
                     headers={'Content-type': 'application/json'})
    assert resp.status_code == 400

    resp = apptc.put('/api/1/admin/resource/12345/meta',
                     data='{"no-content-type": true}')
    assert resp.status_code == 400

    resp = apptc.patch('/api/1/admin/resource/12345/meta', data='{}',
                       headers={'Content-type': 'application/json'})
    assert resp.status_code == 404

    resp = apptc.patch('/api/1/admin/resource/12345/meta', data='INVALID-JSON',
                       headers={'Content-type': 'application/json'})
    assert resp.status_code == 400

    resp = apptc.patch('/api/1/admin/resource/12345/meta',
                       data='{"no-content-type": true}')
    assert resp.status_code == 400

    resp = apptc.post('/api/1/admin/resource/12345/meta')
    assert resp.status_code == 405

    resp = apptc.delete('/api/1/admin/resource/12345/meta')
    assert resp.status_code == 405
