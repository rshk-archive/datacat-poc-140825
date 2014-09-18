datacat.utils.resource_access
#############################

.. automodule:: datacat.utils.resource_access


Core functions
==============

.. autofunction:: open_resource

.. autofunction:: get_resource_accessors



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
