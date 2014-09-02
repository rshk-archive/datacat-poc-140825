def get_plugin_class(name):
    if name.count(':') != 1:
        raise ValueError("Invalid plugin name: {0!r}".format(name))

    module_name, class_name = name.split(':')
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)
