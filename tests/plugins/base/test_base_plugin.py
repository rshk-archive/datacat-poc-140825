import json
import re
import urlparse

import mock


# @mock.patch('datacat.utils.testing.plugins.on_dataset_delete')
# @mock.patch('datacat.utils.testing.plugins.on_dataset_update')
# @mock.patch('datacat.utils.testing.plugins.on_dataset_create')
def test_dataset_hooks_are_called(
        # on_dataset_create,
        # on_dataset_update,
        # on_dataset_delete,
        configured_app):

    from datacat.utils.testing.plugins import dummy_plugin

    # We have to mock objects like this, since the *registered*
    # function will be called, not directly the one from the module!

    on_dataset_create_mocks = [
        mock.Mock(x) for x in dummy_plugin._hooks['dataset_create']]
    on_dataset_update_mocks = [
        mock.Mock(x) for x in dummy_plugin._hooks['dataset_update']]
    on_dataset_delete_mocks = [
        mock.Mock(x) for x in dummy_plugin._hooks['dataset_delete']]
    mock_patching = mock.patch.dict(dummy_plugin._hooks, {
        'dataset_create': on_dataset_create_mocks,
        'dataset_update': on_dataset_update_mocks,
        'dataset_delete': on_dataset_delete_mocks,
    })

    with mock_patching:
        assert 'datacat.utils.testing.plugins:dummy_plugin' \
            in configured_app.config['PLUGINS']

        assert all(x.call_count == 0 for x in on_dataset_create_mocks)
        assert all(x.call_count == 0 for x in on_dataset_update_mocks)
        assert all(x.call_count == 0 for x in on_dataset_delete_mocks)

        # assert on_dataset_create.call_count == 0
        # assert on_dataset_update.call_count == 0
        # assert on_dataset_delete.call_count == 0

        # ------------------------------------------------------------
        # Now, create a dataset

        apptc = configured_app.test_client()
        resp = apptc.post('/api/1/admin/dataset/',
                          headers={'Content-type': 'application/json'},
                          data=json.dumps({'Hello': 'World'}))
        assert resp.status_code == 201

        # Get the ID from the ``Location`` header
        path = urlparse.urlparse(resp.headers['Location']).path
        match = re.match('/api/1/admin/dataset/([0-9]+)', path)
        dataset_id = int(match.group(1))

        assert all(x.call_count == 1 for x in on_dataset_create_mocks)
        assert all(x.call_count == 0 for x in on_dataset_update_mocks)
        assert all(x.call_count == 0 for x in on_dataset_delete_mocks)

        # ------------------------------------------------------------
        # Update

        resp = apptc.put('/api/1/admin/dataset/{0}'.format(dataset_id),
                         headers={'Content-type': 'application/json'},
                         data=json.dumps({'foo': 'BAR'}))
        assert resp.status_code == 200

        assert all(x.call_count == 1 for x in on_dataset_create_mocks)
        assert all(x.call_count == 1 for x in on_dataset_update_mocks)
        assert all(x.call_count == 0 for x in on_dataset_delete_mocks)

        # ------------------------------------------------------------
        # Delete

        resp = apptc.delete('/api/1/admin/dataset/{0}'.format(dataset_id))
        assert resp.status_code == 200

        assert all(x.call_count == 1 for x in on_dataset_create_mocks)
        assert all(x.call_count == 1 for x in on_dataset_update_mocks)
        assert all(x.call_count == 1 for x in on_dataset_delete_mocks)

        # ------------------------------------------------------------
        # More detailed asserts..

        for x in on_dataset_create_mocks:
            x.assert_called_once_with(dataset_id, {'Hello': 'World'})

        for x in on_dataset_update_mocks:
            x.assert_called_once_with(dataset_id, {'foo': 'BAR'})

        for x in on_dataset_delete_mocks:
            x.assert_called_once_with(dataset_id)
