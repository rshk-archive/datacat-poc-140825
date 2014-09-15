Dataset configuration
#####################

Dataset configuration is a simple JSON structure, describing how the
dataset metadata + data should be built.

The configuration is passed through all the enabled plugins in order
to generate the final metadata to be exposed.

.. note:: This page describes the configuration values used by plugins
          shipped with the core; other plugins may use their
          conventions, proven that they do not conflict with the
          currently-enabled plugins.

Key: ``metadata``
=================

**Handled by:** :py:data:`datacat.ext.core.core_plugin`

Maps to a dictionary of metadata attributes to be merged as-is in the
generated metadata object.


Key: ``resources``
==================

**Handled by:** :py:data:`datacat.ext.core.core_plugin`, others.

Maps to a list of resources belonging to this dataset.

By default, links will be built to expose the resources as-is in the
dataset metadata, but plugins might extend this by adding their own
resources, ...


Key: ``resources.type``
-----------------------

Indicates the type of linked resource.

Right now, the only supported values are:

+----------------+--------------------------------+-----------------+
| Value          | Description                    | Required fields |
+================+================================+=================+
| ``internal``   | Link to an internally-stored   | ``id``          |
|                | resource                       |                 |
+----------------+--------------------------------+-----------------+
| ``url``        | The resource can be found at   | ``url``         |
|                | a given URL                    |                 |
+----------------+--------------------------------+-----------------+

..of course, again, a plugin can accept its own.


Key: ``resources.id``
---------------------

For resources with ``{"type": "internal"}``, the id of the
internally-stored resource.


Key: ``resources.url``
----------------------

For resources with ``{"type": "url"}``, the url at which the resource
can be found.


Key: ``resources.exposed``
--------------------------

.. todo:: implement the ``resources.exposed`` dataset configuration functionality

Defaults to ``True``. Indicates whether the "raw" resource should be
exposed directly or not. Setting this to ``False`` is especially
useful in cases in which the resource requires further cleanup before
exposing through the API.


Key: ``geo``
============

Hold configuration for extraction of geographical data from a dataset.


Key: ``geo.enabled``
--------------------

If set to ``True``, indicates that this dataset should be treated as a
geographical dataset by the Geo plugin.


Key: ``geo.importer``
---------------------

The name of the geographical data importer to be used to extract data
from the resources.

Accepted values:

- ``find_shapefiles``: finds shapefiles inside a (possibiy recursive)
  structure of archives. Extracts all the encountered shapefiles along
  the path.


Key ``geo.default_projection``
------------------------------

Default projection to be used for datasets that are not specifying one
(eg. shapefiles missing a ``.prj`` file).

Must be in a format recognised by `gdalsrsinfo`_.

.. _gdalsrsinfo: http://www.gdal.org/gdalsrsinfo.html

.. todo:: Support reading projection information in a safe way using
          gdalsrsinfo; from the docs:

               srs_def may be the filename of a dataset supported by
	       GDAL/OGR from which to extract SRS information OR any of
	       the usual GDAL/OGR forms (complete WKT, PROJ.4, EPSG:n
	       or a file containing the SRS)

	  Of course we don't want to allow the user to specify a path
	  on the local filesystem!

.. warning:: Right now, the only supported format is ``EPSG:<number>``
	     indicating the projection SRID directly.
