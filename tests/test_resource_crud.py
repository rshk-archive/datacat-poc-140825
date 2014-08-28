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

    apptc = configured_app.test_client()
    resp = apptc.put('/api/1/admin/resource/12345', data='foobar')
    assert resp.status_code == 404
