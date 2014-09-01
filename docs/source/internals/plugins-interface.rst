Plugins interface
#################


.. py:module:: datacat.ext.plugin


.. py:class:: BasePlugin

    Base class (and interface) for defining plugins.

    .. py:method:: __init__(conf)

        :param conf: The main application configuration

    .. py:method:: setup()

        Called at service startup for all the configured plugins.

        May be used, eg, to ensure database schema or other resources
        are set up properly, etc.

    .. py:method:: make_dataset(conf)

        :param conf: The dataset configuration object
        :return: The generated dataset metadata


.. py:class:: SimpleDatasetPlugin
