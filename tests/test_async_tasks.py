import pytest


@pytest.mark.xfail(True, reason="Not supported yet")
def test_simple_async_task(configured_app, redis_instance, celery_worker):
    from datacat.ext.core import dummy_task
    result = dummy_task.delay('world')
    assert result.get() == 'Hello, world!'
