from datacat.tasks import make_celery

celery_app = make_celery()
celery_app.worker_main()
