"""
Used for launching Celery workers::

    % celery worker -A datacat.tasks.app.celery_app
"""

from datacat.tasks import make_celery
from datacat.web import app

celery_app = make_celery(app)
