Data Catalog - PoC 2014-08-25
#############################

**Project goal:** create a service, talking via RESTful API, to
provide facilities for storing data, adding metadata, and generating
"derivates" from the stored data.


Technology
==========

**Core:**

Mandatory requirements to make the application work.

- Python (Flask, Psycopg2)
- PostgreSQL 9.2+ (we need JSON column type) [tested on 9.4]

**Core plugins:**

Requirements for plugins shipped with the core, but not mandatory.

- PostGIS (for the geo data plugin)
- Mapnik (for rendering geo data)


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


Public interface
================

**NOTE:** This section is slightly outdated!

The service communicates with the outside using a RESTful API.

The main administrative endpoints are:

- ``/resource/`` - list / search resources
- ``/resource/<name>`` - GET / PUT / DELETE a resource *data*
- ``/resource/<name>/metadata`` - GET / PUT / PATCH a resource *metadata*

- ``/dataset/`` - list / search dataset configuration
- ``/dataset/<name>`` - GET / PUT / PATCH / DELETE a dataset configuration

The main "public" endpoints are:

- ``/<name>/`` - Get metadata about the dataset
- ``/<name>/<related>/`` - Get "other related" items about the
  dataset. Plugins are responsible of generating contents here.

The above endpoints should be "mounted" to some URL,
eg. ``/api/<version>/admin/`` and ``/api/<version>/data/``
respectively.


Resources management
--------------------

Each resource is a record with the following fields:

- ``id`` - serial resource id
- ``metadata`` - JSON metadata of the resource
- ``mimetype`` - Mimetype as specified during data PUT
- ``data_oid`` - PostgreSQL large objects oid of the data


Dataset management
------------------

Each dataset is simply a json (yaml?) text file describing how to
build the published dataset.

- ``id``
- ``configuration``
- ``configuration_format`` - JSON / YAML


Background service
==================

- Periodically check for outdated information, regenerate the dataset
  metadata + data
- Optionally support using a message queue (rabbit / redis / ..) for
  better scheduling of tasks


Usage
=====

**Note:** a more appropariate configuration method will be added later on

Create a "launcher" script:

.. code-block:: python

    from datacat.web import app

    # Configure
    # app.config['DATABASE'] = ...

    # To create database:
    # from datacat.db import create_db
    # create_db(app.config)

    # Run the webapp
    app.run()
