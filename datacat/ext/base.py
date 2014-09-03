class BasePlugin(object):
    """
    Base class (and interface) for defining plugins.
    """

    def __init__(self, config):
        """
        :param config:
            The main application configuration
        """
        self._config = config

    def setup(self):
        """
        Called at service startup for all the configured plugins.

        May be used, eg, to ensure database schema or other resources
        are set up properly, etc.
        """

    def make_dataset_metadata(self, dataset_id, config, meta):
        """
        :param dataset_id:
            The dataset dataset_id
        :param config:
            The dataset configuration object
        :param meta:
            The current state of the dataset metadata, to be changed in place
        :return:
            The generated dataset metadata
        """

    blueprint = None

    def handle_event(self, event_type, event_data):
        """Handle an event"""

        method_name = 'on_{0}'.format(event_type)
        if hasattr(self, method_name):
            return getattr(self, method_name)(event_data)
