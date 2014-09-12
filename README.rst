Data Catalog - PoC 2014-08-25
#############################

Project goal
============

Create a service, talking via RESTful API, to provide facilities for
storing data, adding metadata, and generating "derivates" from the
stored data.


Project documentation
=====================

Documentation is hosted on GitHub pages:
http://rshk.github.io/datacat-poc-140825/


Technology
==========

**Core:**

Mandatory requirements to make the application work.

- Python 2.7 (Flask, Psycopg2)
- PostgreSQL 9.2+ (we need JSON column type) [tested on 9.4]
- Celery for the asynchronous tasks running facilities

**Core plugins:**

Requirements for plugins shipped with the core, but not mandatory.

- PostGIS (for the geo data plugin)
- Mapnik (for rendering geo data)
- shp2pgsql, for importing geo data from shapefiles

.. note:: In order to use Celery-based tasks (only required for
          certain plugins, you'll also need to install and configure a
          broker, such as RabbitMQ or Redis).

	  See `Celery - Brokers
	  <http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html>`_
	  for more information.


Example use cases
=================

**Tabular data:**

- store original data as (one of) CSV/ODS/XLS/...
- expose data as derivate formats:

  - normalize CSV dialect (comma as separator, double quotes, ..)
  - normalize charset (utf-8)
  - ODS/XLS/...
  - JSON (apply column types, ..)
  - Other custom formats (even on a per-dataset basis, eg. a CSV
    containing coordinates can be converted to a Shapefile)


**Geographical data:**

- store original data as (one of) Esri Shapefile, GML, KML, GeoJSON..
- import the data in a PostGIS table, to allow further queries /
  transformations.
- expose data as other formats: SHP, GML, KML, GeoJSON, ..
- use mapnik to render tile layers, according to a configuration
- clean up the data before republishing:

  - use utf-8 as encoding for the text
  - use a standard projection for the data (WGS48) (?)
  - make sure output shapefiles have projection specification (PRJ
    file, in WKT format) [hint: use `gdalsrsinfo
    <http://www.gdal.org/gdalsrsinfo.html>`_ to convert proj description]


**Textual data:**

For example, PDFs, ODT, MS DOC, ...

- Extract plain text
- Index the plain text, offer full-text search functionality
- Convert to HTML to view in the browser


**Custom, per-dataset, transforms:**

For example, we can create new datasets by aggregating other resources, ...


The RESTful API
===============

The API v1 exposes two different kinds of endpoints:

- ``/api/1/admin`` -> the administrative API
- ``/api/1/data`` -> the public API


The administrative API
----------------------

The `administrative API
<http://rshk.github.io/datacat-poc-140825/api/admin.html>`_ is used to
manage resources and dataset configurations.

Usually, it would be protected by some authentication / authorization
layer in case the service is exposed to the public "as-is".


The public API
--------------

The `public API
<http://rshk.github.io/datacat-poc-140825/api/public.html>`_ is
entirely managed by plugins, which expose their own endpoints to
republish the datasets in some way.


Background service
==================

The background task execution is implemented using Celery_; periodic
tasks are scheduled via `Celery Beat`_.

.. _Celery: http://www.celeryproject.org/
.. _Celery Beat: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html


Usage
=====

.. note:: a more appropariate configuration method will be added later on

The ``DATACAT_SETTINGS`` variable can be used to point to the
(filesystem) path to a Python module containing configuration
overrides.

Create a "launcher" script:

.. code-block:: python

    from datacat.core import app

    # Configure
    # app.config['DATABASE'] = ...

    # To create database:
    # from datacat.db import create_db
    # create_db(app.config)

    # Run the webapp
    app.run()
