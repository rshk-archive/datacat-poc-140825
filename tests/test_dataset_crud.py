import json
import re
import urlparse


def test_dataset_empty_listing(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/dataset/')
    assert resp.status_code == 200
    assert json.loads(resp.data) == []


def test_dataset_crud(configured_app):
    apptc = configured_app.test_client()

    # ------------------------------------------------------------
    # Create a new dataset
    # ------------------------------------------------------------

    resp = apptc.post('/api/1/admin/dataset/',
                      headers={'Content-type': 'application/json'},
                      data=json.dumps({'Hello': 'World'}))
    assert resp.status_code == 201
    assert resp.data == ''
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/dataset/([0-9]+)', path)
    dataset_id = int(match.group(1))

    # ------------------------------------------------------------
    # Get it back and check
    # ------------------------------------------------------------

    resp = apptc.get('/api/1/admin/dataset/{0}'.format(dataset_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'Hello': 'World'}
    assert resp.headers['Content-type'] == 'application/json'

    # Make sure it is listed in the index
    resp = apptc.get('/api/1/admin/dataset/')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == dataset_id
    assert data[0]['configuration'] == {'Hello': 'World'}

    # ------------------------------------------------------------
    # Update and make sure it is updated
    # ------------------------------------------------------------

    resp = apptc.put('/api/1/admin/dataset/{0}'.format(dataset_id),
                     headers={'Content-type': 'application/json'},
                     data=json.dumps({'foo': 'BAR'}))
    assert resp.status_code == 200

    resp = apptc.get('/api/1/admin/dataset/{0}'.format(dataset_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'foo': 'BAR'}
    assert resp.headers['Content-type'] == 'application/json'

    # ------------------------------------------------------------
    # Make sure we get 400 if sending non-json data
    # ------------------------------------------------------------

    resp = apptc.put('/api/1/admin/dataset/{0}'.format(dataset_id),
                     headers={'Content-type': 'text/plain'},
                     data='HELLO WORLD')
    assert resp.status_code == 400

    resp = apptc.put('/api/1/admin/dataset/{0}'.format(dataset_id),
                     headers={'Content-type': 'application/json'},
                     data='This is not valid json')
    assert resp.status_code == 400

    # ------------------------------------------------------------
    # Patch to update stuff
    # ------------------------------------------------------------

    resp = apptc.patch('/api/1/admin/dataset/{0}'.format(dataset_id),
                       headers={'Content-type': 'application/json'},
                       data=json.dumps({'bar': 'BAZ'}))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/dataset/{0}'.format(dataset_id))
    assert resp.status_code == 200
    assert json.loads(resp.data) == {'foo': 'BAR', 'bar': 'BAZ'}
    assert resp.headers['Content-type'] == 'application/json'

    # ------------------------------------------------------------
    # Delete and make sure it's gone
    # ------------------------------------------------------------

    resp = apptc.delete('/api/1/admin/dataset/{0}'.format(dataset_id))
    assert resp.status_code == 200
    assert resp.data == ''

    resp = apptc.get('/api/1/admin/dataset/{0}'.format(dataset_id))
    assert resp.status_code == 404

    # Make sure it is not listed in the index anymore
    resp = apptc.get('/api/1/admin/dataset/')
    assert resp.status_code == 200
    assert json.loads(resp.data) == []


def test_dataset_crud_errors(configured_app):
    apptc = configured_app.test_client()

    resp = apptc.get('/api/1/admin/dataset/12345')
    assert resp.status_code == 404

    resp = apptc.put('/api/1/admin/dataset/12345',
                     headers={'Content-type': 'application/json'},
                     data=json.dumps({'foo': 'BAR'}))
    assert resp.status_code == 404

    resp = apptc.patch('/api/1/admin/dataset/12345',
                       headers={'Content-type': 'application/json'},
                       data=json.dumps({'foo': 'BAR'}))
    assert resp.status_code == 404

    resp = apptc.delete('/api/1/admin/dataset/12345')
    assert resp.status_code == 200
