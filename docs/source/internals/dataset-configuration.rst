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

          The datacat core doesn't enforce any schema on this configuration,
          everything is up to the enabled plugins.

Key: ``metadata``
=================

**Plugins behavior**

:py:mod:`Core Plugin <datacat.ext.core>`

    Takes values from the ``metadata`` object and expand them directly
    in the dataset metadata.


Key: ``resources``
==================

List of resouce items.

Each item is either a string (representing directly the URL of the
resource) or a dictionary. In the latter case, the resource URL MUST
be provided via the "url" dictionary item.

URL opening is done via the :py:mod:`resource_access
<datacat.utils.resource_access>` system.

**Plugins behavior**

:py:mod:`Core Plugin <datacat.ext.core>`

    Unless ``resource.hidden == True``, links will be built to expose
    resources for "as-is" download, in the dataset metadata.

.. warning:: "hidden" does not mean "private": although the link
             will not be advertised, the resource is still
             accessible by directly visiting the URL.


Key: ``resources.url``
----------------------

The resource URL, eg. ``http://www.example.com/myresource.json`` or
``internal:///1234``.

URLs will be opened via :py:func:`~datacat.utils.resource_access.open_resource`.


Key: ``resources.hidden``
--------------------------

.. todo:: implement the ``resources.hidden`` dataset configuration functionality

If set to ``True``, the default plugin will leave this resource alone, and
will not add a download link.


Key: ``geo``
============

Hold configuration for extraction of geographical data from a dataset.

**Plugins behavior**

:py:mod:`Geo Plugin <datacat.ext.geo>`

    - on metadata creation, add own resource links (conversions
      to other formats)
    - expose API endpoints to query the geographical data
    - on dataset create/update import datasets to PostGIS table
      (and remove those tables on delete)
    - render tiles via mapnik


Key: ``geo.enabled``
--------------------

If set to ``True``, indicates that this dataset should be treated as a
geographical dataset by the Geo plugin. Otherwise, it will simply be
ignored.


Key: ``geo.importer``
---------------------

The name of the geographical data importer to be used to extract data
from the resources.

Accepted values:

- ``find_shapefiles``: finds shapefiles inside a (possibiy recursive)
  structure of archives. Extracts all the encountered shapefiles along
  the path.

.. todo:: Write more importers, with improved "autodiscovery" mechanism


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


Key: ``geo.override_projection``
--------------------------------

Force use this projection, even if one was specified in the source.

See the `geo.default_projection <#key-geo-default-projection>`_
documentation for more info about accepted values.
