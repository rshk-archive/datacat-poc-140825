datacat.utils.resource_access
#############################

.. py:module:: datacat.utils.resource_access

.. automodule:: datacat.utils.resource_access


Resource opener function
========================

.. autofunction:: open_resource


Base interface
==============

.. autoclass:: BaseResourceAccessor
    :members:
    :undoc-members:
    :special-members: __init__


Core resource accessors
=======================

.. autoclass:: InternalResourceAccessor
    :members:
    :undoc-members:
    :special-members: __init__

.. autoclass:: HttpResourceAccessor
    :members:
    :undoc-members:
    :special-members: __init__


Exceptions
==========

.. autoclass:: ResourceAccessError

.. autoclass:: ResourceNotFound

.. autoclass:: ResourceAccessDenied

.. autoclass:: ResourceAccessFailure
