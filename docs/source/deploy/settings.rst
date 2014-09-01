Settings
########

``DATABASE``
============

PostgreSQL database configuration:

.. code-block:: python

    {
        'database': 'datacat-db',
	'user': 'datacat',
	'password': 'S3cur3-P4ssw0rd'
        'host': 'localhost',
        'port': 5432,
    }


``DATASET_PLUGINS``
===================

Dictionary mapping names to classes to be used to process dataset
configuration:

.. code-block:: python

    {
        'default': '$simple',
	'simple': 'datacat.ext.dataset:Simple',
    }


``RESOURCE_PLUGINS``
====================

Dictionary mapping names to classes to be used to process resource
configuration. Accepts the same syntax as `DATASET_PLUGINS`_.
