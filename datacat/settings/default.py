# ============================================================
#     Flask configuration
# ============================================================
# See: http://flask.pocoo.org/docs/latest/config/#builtin-configuration-values

DEBUG = False
TESTING = False

# SECRET_KEY = 'This is some secret'


# ============================================================
#     Datacat configuration
# ============================================================

DATABASE = {
    'database': None,
    'user': None,
    'password': None,
    'host': 'localhost',
    'port': 5432,
}

PLUGINS = [
    'datacat.ext.core:core_plugin',
]


# ============================================================
#     Celery configuration
# ============================================================
# See: http://docs.celeryproject.org/en/latest/configuration.html


CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULTS_BACKEND = 'redis://localhost:6379/0'

# CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
