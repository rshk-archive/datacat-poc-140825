def test_dataset_hooks_are_called(configured_app):
    assert 'datacat.utils.testing.plugins:dummy_plugin' \
        in configured_app.config['PLUGINS']
    pass
