def test_resource_empty_listing(running_app):
    resp = running_app.get('/api/1/admin/resource/')
    assert resp.ok
    assert resp.status_code == 200
    assert resp.json() == []
