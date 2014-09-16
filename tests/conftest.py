import os
import random
import time
from urlparse import urlparse
import shutil

import pytest
import py.path


TESTS_ROOT_DIR = py.path.local(__file__).dirpath()
TESTS_DATA_DIR = TESTS_ROOT_DIR.join('data')


POSTGRES_ENV_NAME = 'POSTGRES_URL'


def _celery_testing_conf():
    return dict(
        CELERY_BROKER_URL='redis://localhost:6399/0',
        CELERY_RESULT_BACKEND='redis://localhost:6399/0',
        CELERY_ACCEPT_CONTENT=['json', 'msgpack', 'yaml'],
        CELERY_ALWAYS_EAGER=True,
    )


def _celery_testing_conf_py():
    return "\n".join("{0} = {1!r}".format(key, val)
                     for key, val in _celery_testing_conf().iteritems()) + "\n"


@pytest.fixture(scope='module')
def postgres_conf():
    if POSTGRES_ENV_NAME not in os.environ:
        raise RuntimeError(
            "Missing configuration: the {0} environment variable is required"
            " in order to be able to create a PostgreSQL database for running"
            " tests. Please set it to something like: ``postgresql://"
            "user:password@host:port/database``."
            .format(POSTGRES_ENV_NAME))
    url = urlparse(os.environ[POSTGRES_ENV_NAME])
    return {
        'database': url.path.split('/')[1],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port or 5432,
    }


@pytest.fixture(scope='module')
def postgres_admin_db(request, postgres_conf):
    from datacat.db import connect
    conn = connect(**postgres_conf)
    request.addfinalizer(lambda: conn.close())
    return conn


@pytest.fixture(scope='module')
def postgres_user_conf(request, postgres_conf):
    from datacat.db import connect
    conn = connect(**postgres_conf)
    conn.autocommit = True

    randomcode = random.randint(0, 999999)
    name = 'dtctest_{0:06d}'.format(randomcode)

    # Note: we need to use separate transactions to perform
    # administrative activities such as creating/dropping databases
    # and roles.

    # For this reason, we need to set the connection isolation level
    # to "autocommit"

    with conn.cursor() as cur:
        cur.execute("""
        CREATE ROLE "{name}" LOGIN
        PASSWORD %(password)s;
        """.format(name=name), dict(password=name))

        cur.execute("""
        CREATE DATABASE "{name}"
        WITH OWNER "{name}"
        ENCODING = 'UTF-8';
        """.format(name=name))

    def cleanup():
        conn.autocommit = True
        with conn.cursor() as cur:
            # Kill all connections to database first
            cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{name}'
            AND pid <> pg_backend_pid();
            """.format(name=name))
            cur.execute('DROP DATABASE "{name}";'.format(name=name))
            cur.execute('DROP ROLE "{name}";'.format(name=name))

    request.addfinalizer(cleanup)

    conf = postgres_conf.copy()
    conf['user'] = name
    conf['password'] = name
    conf['database'] = name

    # HACK to create PostGIS extension, used by some plugins
    _conf = postgres_conf.copy()
    _conf['database'] = name
    _conn = connect(**_conf)
    _conn.autocommit = True
    with _conn.cursor() as cur:
        cur.execute("CREATE EXTENSION postgis;")

    return conf


@pytest.fixture
def postgres_user_db(request, postgres_user_conf):
    from datacat.db import connect
    conn = connect(**postgres_user_conf)
    conn.autocommit = False
    request.addfinalizer(lambda: conn.close())
    return conn


@pytest.fixture
def postgres_user_db_ac(request, postgres_user_conf):
    """User database with autocommit on"""
    from datacat.db import connect
    conn = connect(**postgres_user_conf)
    conn.autocommit = True
    request.addfinalizer(lambda: conn.close())
    return conn


@pytest.fixture(scope='module')
def app_config(postgres_user_conf):
    from flask.config import Config
    from datacat.settings import testing

    conf = Config('')
    conf.from_object(testing)
    conf['DATABASE'] = postgres_user_conf
    return conf


@pytest.fixture(scope='module')
def configured_app(request, app_config):
    from datacat.core import make_app

    app_config.update(_celery_testing_conf())

    app = make_app(app_config)
    app.debug = True

    return app


@pytest.fixture(scope='module')
def redis_instance(request):
    import subprocess
    import tempfile
    tempdir = tempfile.mkdtemp()
    command = ['redis-server', '--port', '6399']
    proc = subprocess.Popen(command, cwd=tempdir)

    def cleanup():
        proc.terminate()
        proc.wait()
        shutil.rmtree(tempdir)

    request.addfinalizer(cleanup)

    time.sleep(1)
    return ('localhost', 6399)


@pytest.fixture
def data_dir():
    return TESTS_DATA_DIR
