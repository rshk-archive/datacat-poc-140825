Geo
###

Plugin offering functionality for treating geographical data.

See also the geo plugin internal API documentation: :py:mod:`datacat.ext.geo`


Features
========

- Import geographical data into PostGIS tables
- *[planned]* Allow querying the geographical data
- *[planned]* Export geo data to other formats: shp, csv, geojson, gml, kml, ..
- *[planned]* Render map tiles
- *[planned]* Expose data via WFS/WMS


Setup
=====

This plugin requires the database to have the PostGIS extension
enabled.

To do so, you can simply create the extension from the PostgreSQL
CLI (as superuser)::

    create extension postgis;

It also requires ``shp2pgsql`` in order to import Shapefiles to PostGIS.


Usage
=====

.. todo:: Document the Geo plugin usage
