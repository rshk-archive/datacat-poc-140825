"""
Quick launcher for datacat.

Will setup and run:

- the web application
- a redis server
- a celery worker


.. warning:: This is intended for development / testing purposes only!
             Don't use this in production!
"""

import multiprocessing
import tempfile
import time
import subprocess

from datacat.web import make_app
from datacat.tasks import make_celery


def run_webapp():
    app = make_app()
    app.run(host='127.0.0.1', port=8080)


def run_celery():
    app = make_app()
    app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6399/0'
    celery_app = make_celery(app)
    celery_app.worker_main(argv=['datacat.launcher'])


def run_redis():
    tempdir = tempfile.mkdtemp()
    # Note we are using a non-standard port (would be 6379)
    proc = subprocess.Popen(['redis-server', '--port', '6399'],
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
