import json
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
    assert urlparse.urlparse(resp.headers['Location']).path == '/api/1/admin/resource/1'  # noqa

    # ------------------------------------------------------------
    # Get it back and check
    # ------------------------------------------------------------

    resp = apptc.get('/api/1/admin/resource/1')
    assert resp.status_code == 200
    assert resp.data == DATA_PAYLOAD
    assert resp.headers['Content-type'] == 'application/json'

    # ------------------------------------------------------------
    # Update and make sure it is updated
    # ------------------------------------------------------------

    resp = apptc.put('/api/1/admin/resource/1',
                     headers={'Content-type': 'text/plain'},
                     data='HELLO WORLD')
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/1')
    assert resp.status_code == 200
    assert resp.data == 'HELLO WORLD'
    assert resp.headers['Content-type'] == 'text/plain'

    # ------------------------------------------------------------
    # Delete and make sure it's gone
    # ------------------------------------------------------------

    resp = apptc.delete('/api/1/admin/resource/1')
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/1')
    assert resp.status_code == 404


def test_resource_error_404(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/resource/12345')
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
    assert urlparse.urlparse(resp.headers['Location']).path == '/api/1/admin/resource/2'  # noqa

    resource_id = 2

    # ------------------------------------------------------------
    # Initial metadata should be empty

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {}

    resp = apptc.put('/api/1/admin/resource/{0}/meta'.format(resource_id),
                     headers={'Content-type': 'application/json'},
                     data=json.dumps({'key1': 'FOO', 'key2': 'BAR'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'key1': 'FOO', 'key2': 'BAR'}

    resp = apptc.patch('/api/1/admin/resource/{0}/meta'.format(resource_id),
                       headers={'Content-type': 'application/json'},
                       data=json.dumps({'key1': 'FOOBAR'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/resource/{0}/meta'.format(resource_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'key1': 'FOOBAR', 'key2': 'BAR'}

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
