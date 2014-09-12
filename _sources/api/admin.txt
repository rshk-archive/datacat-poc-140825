Administrative API
##################

The administrative API is used to read/write resources and dataset
configurations.


``GET /api/1/admin/resource/``
==============================

List / search resources.


``POST /api/1/admin/resource/``
===============================

Create a new resource, by posting some data.

The ``Content-Type`` header will be stored and sent back when
``GET`` ting the original data.

If operation was successful, return ``201`` with the newly-created
resource URL in the ``Location`` header.


``GET /api/1/admin/resource/<id>``
==================================

Get the data for a specific resource.

On success, return ``200`` with the resource data as the response
body and a ``Content-type`` header properly set.


``PUT /api/1/admin/resource/<id>``
==================================

Update the resource data.


``DELETE /api/1/admin/resource/<id>``
=====================================

Delete the resource at once (both data and metadata).


``GET /api/1/admin/resource/<id>/meta``
=======================================

Get the resource metadata, as json.


``PUT /api/1/admin/resource/<id>/meta``
=======================================

Update the resource metadata, from json.

The metadata object will be replaced.

Note that ``Content-type`` in the request must be set to
``application/json``.


``PATCH /api/1/admin/resource/<id>/meta``
=========================================

Update the resource metadata, from json.

The metadata object will be simply updated.

Note that ``Content-type`` in the request must be set to
``application/json``.
