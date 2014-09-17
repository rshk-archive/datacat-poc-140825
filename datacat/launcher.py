"""
Quick launcher for datacat.

Will setup and run:

- the web application
- a redis server
- a celery worker


.. warning:: This is intended for development / testing purposes only!
             Don't use this in production!
"""

REDIS_PORT = 6389
WEBSERVER_PORT = 8080


import multiprocessing
import tempfile
import time
import subprocess

from datacat.core import make_app, celery_app


app = make_app()


def run_webapp():
    app.run(host='127.0.0.1', port=WEBSERVER_PORT)


def run_celery():
    redis_url = 'redis://127.0.0.1:{0}/0'.format(REDIS_PORT)
    celery_app.conf.BROKER_URL = redis_url
    celery_app.conf.RESULT_BACKEND = redis_url
    celery_app.worker_main(argv=['datacat.launcher'])


def run_redis():
    tempdir = tempfile.mkdtemp()
    # Note we are using a non-standard port (would be 6379)
    proc = subprocess.Popen(['redis-server', '--port', str(REDIS_PORT)],
                            cwd=tempdir)
    proc.wait()  # todo: we need to abort if redis-server command missing!


class ProcessWatcher(object):
    def __init__(self):
        self._proc_args = []
        self._procs = {}

    def add(self, *a, **kw):
        self._proc_args.append((a, kw))

    def start(self):
        while True:
            for i, (a, kw) in enumerate(self._proc_args):
                if not (i in self._procs and self._procs[i].is_alive()):
                    self._procs[i] = multiprocessing.Process(*a, **kw)
                    self._procs[i].start()
            time.sleep(1)


def launch():
    watcher = ProcessWatcher()
    watcher.add(target=run_webapp)
    watcher.add(target=run_redis)
    watcher.add(target=run_celery)
    watcher.start()


if __name__ == '__main__':
    launch()
