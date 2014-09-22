datacat.ext.geo
###############

.. automodule:: datacat.ext.geo

.. autodata:: geo_plugin


Plugin base class
=================

.. autoclass:: GeoPlugin
    :members:
    :undoc-members:


Hooks
=====

.. autofunction:: make_dataset_metadata

.. autofunction:: on_dataset_create_update

.. autofunction:: on_dataset_delete


Views
=====


.. autofunction:: export_geo_dataset_shp

.. autofunction:: export_geo_dataset_geojson

.. autofunction:: export_geo_dataset_csv

.. autofunction:: export_geo_dataset_gml

.. autofunction:: export_geo_dataset_kml


Celery tasks
============

.. autofunction:: import_geo_dataset(dataset_id)


Utilities
=========

.. autofunction:: import_dataset_find_shapefiles
