from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    Task = celery.Task

    class AppContextTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return Task.__call__(self, *args, **kwargs)

    celery.Task = AppContextTask
    return celery
