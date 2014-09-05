def get_plugin_class(name):
    raise DeprecationWarning()


def import_object(name):
    if name.count(':') != 1:
        raise ValueError("Invalid object name: {0!r}. "
                         "Expected format: '<module>:<name>'."
                         .format(name))

    module_name, class_name = name.split(':')
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)
