import json
import re
import urlparse


def test_core_plugin_metadata_resources(configured_app_ctx):
    apptc = configured_app_ctx.test_client()

    # First we want to create two resources and a dataset linking to
    # those two resources

    resources = [
        ('text/plain', 'This is some plain text'),
        ('application/json', '{"This": "is", "some": "JSON"}'),
    ]

    dataset_conf = {
        'metadata': {
            'title': "My First Dataset",
        },
        'resources': [],
    }

    for mimetype, data in resources:
        resp = apptc.post('/api/1/admin/resource/',
                          headers={'Content-type': mimetype},
                          data=data)
        assert resp.status_code == 201
        path = urlparse.urlparse(resp.headers['Location']).path
        match = re.match('/api/1/admin/resource/([0-9]+)', path)
        resource_id = int(match.group(1))
        dataset_conf['resources'].append({
            'url': 'internal:///{0}'.format(resource_id),
        })

    resp = apptc.post('/api/1/admin/dataset/',
                      headers={'Content-type': 'application/json'},
                      data=json.dumps(dataset_conf))
    assert resp.status_code == 201
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/dataset/([0-9]+)', path)
    dataset_id = int(match.group(1))

    # ------------------------------------------------------------
    # Now, get the dataset from the public API and check..

    resp = apptc.get('/api/1/data/{0}'.format(dataset_id))
    assert resp.status_code == 200
    assert resp.headers['Content-type'] == 'application/json'
    data = json.loads(resp.data)
    assert data['title'] == 'My First Dataset'
    assert isinstance(data['resources'], list)
    assert len(data['resources']) == 2

    # Check resource metadata
    assert data['resources'][0]['url'].startswith('http://')

    assert urlparse.urlparse(data['resources'][0]['url']).path == \
        '/api/1/data/resource/1'
    assert urlparse.urlparse(data['resources'][1]['url']).path == \
        '/api/1/data/resource/2'

    # Try getting the metadata and check
    path1 = urlparse.urlparse(data['resources'][0]['url']).path
    resp = apptc.get(path1)
    assert resp.status_code == 200
    assert resp.headers['Content-type'] == 'text/plain'
    assert resp.data == 'This is some plain text'

    path2 = urlparse.urlparse(data['resources'][1]['url']).path
    resp = apptc.get(path2)
    assert resp.headers['Content-type'] == 'application/json'
    assert resp.data == '{"This": "is", "some": "JSON"}'
