DEBUG = False

DATABASE = {
    'database': None,
    'user': None,
    'password': None,
    'host': 'localhost',
    'port': 5432,
}

PLUGINS = [
    'datacat.ext.core:CorePlugin',
]


CELERY_BROKER_URL = 'redis://localhost:6379/0'
