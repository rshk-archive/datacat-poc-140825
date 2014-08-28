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
