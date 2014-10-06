"""
Background jobs control system.
Provide facilities for registering and running background jobs.

- Job definitions are stored in the database
- To each job definition, multiple "runs" can be attached.
- Each run has a start/end time, status, exit status, logs and output data
  (job-type-dependent).
- All the logs during a task execution are stored in a table
- Facilities are provided to periodically clean up the logs table
  from old logs, according to a retention policy based on the log
  level (less important messages are deleted first)
"""

from datetime import datetime, timedelta
import json
import logging
import threading

from datacat.db import db, querybuilder
from datacat.utils.plugin_loading import import_object


logger = logging.getLogger(__name__)


def create_job(runner, args=None, kwargs=None):
    """
    Create a job to be executed.

    .. warning:: No check is made on the job runner!

    .. todo:: Fire an event to signal a job was created,
              to allow execution right away, via celery, if
              available.
    """

    if isinstance(runner, basestring):
        runner_name = runner
    else:
        # assume it is a class
        runner_name = '{0}:{1}'.format(runner.__module__, runner.__name__)
    data = {
        'ctime': datetime.now(),
        'runner': runner_name,
        'args': json.dumps(args or []),
        'kwargs': json.dumps(kwargs or {}),
    }
    query = querybuilder.insert('background_job', data=data)
    with db, db.cursor() as cur:
        cur.execute(query, data)
        job_id = cur.fetchone()[0]
    return job_id


def start_job(job_id):
    """
    Wrapper around job execution

    .. warning:: No check is made on the job runner!
    """

    job_def = get_job_def(job_id)
    runner_class = import_object(job_def['runner'])

    _setup_logging()

    data = {
        'job_id': job_id,
        'start_time': datetime.now(),
        'started': True,
        'finished': False,
    }
    query = querybuilder.insert('background_job_run', data=data)
    with db, db.cursor() as cur:
        cur.execute(query, data)
        job_run_id = cur.fetchone()[0]

    try:
        logger.info('Creating runner for job {0}'.format(job_id))
        runner = runner_class(job_def['configuration'])

        logger.info('Starting execution of job {0}'.format(job_id))
        runner.run()  # Do stuff!

    except:
        logger.exception('Job run failed')
        success = False

    else:
        logger.info('Job run successful')
        success = True

    finally:
        data = {
            'id': job_run_id,  # PK
            'end_time': datetime.now(),
            'finished': True,
            'success': success,
        }
        query = querybuilder.update('background_job_run', data=data)
        with db, db.cursor() as cur:
            cur.execute(query, data)


def get_job_def(job_id):
    """
    Get job definition, in a dictionary.
    """

    query = querybuilder.select_pk('background_job')
    with db, db.cursor() as cur:
        cur.execute(query, {'id': job_id})
        result = cur.fetchone()
    if not result:
        raise ValueError('Job with id {0} was not found'.format(job_id))
    return result


def delete_job(job_id):
    """
    Completely delete all information related to a given job
    """

    with db, db.cursor() as cur:
        cur.execute("DELETE FROM background_job_run_log WHERE job_id=%(id)s",
                    {'job_id': job_id})  # Delete logs
        cur.execute("DELETE FROM background_job_run WHERE job_id=%(id)s",
                    {'id': job_id})  # Delete runs
        cur.execute("DELETE FROM background_job WHERE id=%(id)s",
                    {'id': job_id})  # Delete job def


def get_job_run_status(job_run_id):
    query = "SELECT * FROM background_job_run WHERE id=%(id)s"
    with db, db.cursor() as cur:
        cur.execute(query, {'id': job_run_id})
    return cur.fetchone()


def list_job_runs(job_id):
    """List job runs"""

    query = "SELECT * FROM background_job_run WHERE job_id=%(id)s"
    with db, db.cursor() as cur:
        cur.execute(query, {'id': job_id})
    return list(cur.fetchall())


def delete_job_run(job_run_id):
    """Delete information about a job run"""

    query = querybuilder.delete('background_job_run')
    with db, db.cursor() as cur:
        cur.execute(query, {'id': job_run_id})

    with db, db.cursor() as cur:
        cur.execute(
            "DELETE FROM background_job_run_log WHERE job_run_id=%(id)s",
            {'id': job_run_id})  # Delete logs
        cur.execute(
            "DELETE FROM background_job_run WHERE id=%(id)s",
            {'id': job_run_id})  # Delete run


class JobRunner(object):
    """
    Decorator class to be used to mark callables as suitable
    for job running.
    """

    def __init__(self, func=None):
        import functools
        self.func = func
        functools.update_wrapper(self, func)
        self.import_name = ':'.join(
            func.__module__,
            func.__name__)

    def __call__(self, *a, **kw):
        return self.func(*a, **kw)

    def apply_async(self, args=None, kwargs=None, **ignored):
        job_id = create_job(self.import_name, args=args, kwargs=kwargs)
        return Job(job_id)

    def delay(self, *args, **kwargs):
        return self.apply_async(args=args, kwargs=kwargs)


class Job(object):
    def __init__(self, job_id):
        self.job_id = job_id
        self.job_def = get_job_def(job_id)

    def list_job_runs(self):
        for job_run in list_job_runs(self.job_id):
            yield JobRunResult(job_run['id'], status=job_run)


class JobRunResult(object):
    def __init__(self, job_run_id, status=None):
        self.job_run_id = job_run_id
        self._job_run_status = status

    def update(self):
        """Update status for this job run"""
        self._job_run_status = get_job_run_status(self.job_run_id)

    def get_status(self):
        """Get the current status for this job run"""
        if self._job_run_status is None:
            self.update()
        return self._job_run_status

    def get_logs(self):
        """Iter log records for this job run"""
        pass

    def get_result(self):
        """Get result data, once the task has completed"""
        pass


# class AsyncJobResult(object):
#     def __init__(self, job_id, job_run_id):
#         pass


HOUR = 3600
DAY = 24 * HOUR
MONTH = 30 * DAY


class PostgresLogHandler(logging.Handler):
    """
    Logging handler writing to a PostgreSQL table.
    """

    log_retention_policy = {
        logging.DEBUG: 15 * DAY,
        logging.INFO: MONTH,
        logging.WARNING: 3 * MONTH,
        logging.ERROR: 6 * MONTH,
        logging.CRITICAL: 6 * MONTH,
    }
    log_max_retention = 12 * MONTH

    def __init__(self, table_name):
        super(PostgresLogHandler, self).__init__()
        self.table_name = table_name
        self.setLevel(logging.DEBUG)  # Log everything by default

    def flush(self):
        pass  # Nothing to flush!

    def serialize(self, record):
        """Prepare log record for insertion into PostgreSQL"""

        import traceback

        record_dict = {
            'args': json.dumps(record.args),
            'created': record.created,
            'filename': record.filename,
            'funcName': record.funcName,
            'levelname': record.levelname,
            'levelno': record.levelno,
            'lineno': record.lineno,
            'module': record.module,
            'msecs': record.msecs,
            'msg': record.msg,
            'name': record.name,
            'pathname': record.pathname,
            'process': record.process,
            'processName': record.processName,
            'relativeCreated': record.relativeCreated,
            'thread': record.thread,
            'threadName': record.threadName}

        if record.exc_info is not None:
            # We cannot serialize exception information.
            # The best workaround here is to simply add the
            # relevant information to the message, as the
            # formatter would..
            exc_class = u'{0}.{1}'.format(
                record.exc_info[0].__module__,
                record.exc_info[0].__name__)
            exc_message = str(record.exc_info[1])
            exc_repr = repr(record.exc_info[1])
            exc_traceback = '\n'.join(
                traceback.format_exception(*record.exc_info))

            # record_dict['_orig_msg'] = record_dict['msg']
            # record_dict['msg'] += "\n\n"
            # record_dict['msg'] += exc_traceback
            record_dict['exc_class'] = exc_class
            record_dict['exc_message'] = exc_message
            record_dict['exc_repr'] = exc_repr
            record_dict['exc_traceback'] = exc_traceback

        return record_dict

    def emit(self, record):
        """Handle a received log message"""

        data = self.serialize(record)
        data['job_id'] = _current_job_info.job_id
        data['job_run_id'] = _current_job_info.job_run_id

        query = querybuilder.insert(self.table_name, data=data)
        with db, db.cursor() as cur:
            cur.execute(query, data)

    def cleanup_old_messages(self):
        """Delete old log messages, according to log retention policy"""

        query = """
        DELETE FROM "{0}"
        WHERE "levelno" <= %(levelno)s
          AND "created" <= %(expiredate)s;
        """.format(self.table_name)

        # Apply log retention policy
        for minlevel, retention in self.log_retention_policy.iteritems():
            expiredate = datetime.now() - timedelta(seconds=retention)
            with db, db.cursor() as cur:
                cur.execute(query, {'levelno': minlevel,
                                    'expiredate': expiredate})

        # Delete all the logs older than self.log_max_retention
        expiredate = datetime.now() - timedelta(seconds=self.log_max_retention)
        query = """
        DELETE FROM "{0}" WHERE "created" <= %(expiredate)s;
        """.format(self.table_name)
        with db, db.cursor() as cur:
            cur.execute(query, {'expiredate': expiredate})


_current_job_info = threading.local()
_job_log_handler = None
_logging_setup_done = False


def _get_job_log_handler():
    global _job_log_handler
    if _job_log_handler is None:
        _job_log_handler = PostgresLogHandler(
            table_name='background_job_run_log')
    return _job_log_handler


def _setup_logging(job_id, job_run_id):
    global _current_job_info
    _current_job_info.job_id = job_id
    _current_job_info.job_run_id = job_run_id

    global _logging_setup_done
    if _logging_setup_done:
        return

    handler = _get_job_log_handler()
    logging.getLogger('').addHandler(handler)

    _logging_setup_done = True
