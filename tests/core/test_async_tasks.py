import pytest


def test_simple_async_task(configured_app):
    from datacat.ext.core import dummy_task
    with configured_app.app_context():
        result = dummy_task.delay('world')
        assert result.get(timeout=2) == 'Hello, world!'
