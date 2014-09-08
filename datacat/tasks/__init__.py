from celery import Celery, Task


# This is the "base" celery app, used to setup tasks etc.
# It will then be "hot-swapped" on tasks using the application
# context / flask.current_app
celery_app = Celery('datacat.tasks')


class AppContextTask(celery_app.Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        from flask import current_app
        with current_app.app_context():
            return Task.__call__(self, *args, **kwargs)

    @property
    def _app(self):
        from flask import current_app
        return current_app.celery


celery_app.Task = AppContextTask
