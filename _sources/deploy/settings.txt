Settings
########


The default settings are in ``datacat.settings.default``.

To pass extra configuration, set the environment variable
:envvar:`!DATACAT_SETTINGS` to point to a Python file containing the
configuration overrides.

Many configuration variables are used directly by Flask, and their
documentation can be found at:
http://flask.pocoo.org/docs/latest/config/#builtin-configuration-values


``DATABASE``
============

PostgreSQL database configuration:

.. code-block:: python

    DATABASE = {
        'host': 'localhost',
        'port': 5432,
        'database': 'datacat-db',
	'user': 'datacat-user',
	'password': 'S3cur3-P4ssw0rd'
    }


``PLUGINS``
===========

List of enabled plugins.

.. code-block:: python

    PLUGINS = [
        'datacat.ext.eggs:EggsPlugin',
        'datacat.ext.spam:SpamPlugin',
        'datacat.ext.bacon:BaconPlugin',
    ]


``RESOURCE_ACCESSORS``
======================

.. code-block:: python

    RESOURCE_ACCESSORS = {
        'http': 'datacat.utils.resource_access:HttpResourceAccessor',
        'https': 'datacat.utils.resource_access:HttpResourceAccessor',
        'internal': 'datacat.utils.resource_access:InternalResourceAccessor',
    }


Celery configuration
====================

See `the Celery Project documentation
<http://docs.celeryproject.org/en/latest/configuration.html>`_ for
more information about accepted configuration options.

``CELERY_BROKER_URL``
---------------------

.. code-block:: python

    CELERY_BROKER_URL = 'redis://localhost:6379/0'

``CELERY_RESULT_BACKEND``
-------------------------

.. code-block:: python

    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

``CELERY_ACCEPT_CONTENT``
-------------------------

.. note::

    The ``pickle`` serialization method has been removed by default,
    as it is greatly insecure.

    The msgpack and yaml serialization require the ``msgpack-python``
    and ``yaml`` packages to be installed, respectively.

.. code-block:: python

    CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
