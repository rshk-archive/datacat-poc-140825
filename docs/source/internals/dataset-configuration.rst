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
