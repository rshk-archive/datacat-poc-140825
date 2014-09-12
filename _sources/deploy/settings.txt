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

    {
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

    [
        'datacat.ext.eggs:EggsPlugin',
        'datacat.ext.spam:SpamPlugin',
        'datacat.ext.bacon:BaconPlugin',
    ]
