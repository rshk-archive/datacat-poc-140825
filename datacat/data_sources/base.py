class DataSourceBase(object):
    def __init__(self, url, config=None):
        self.url = url
        self.config = {}
        if config is not None:
            self.config.update(config)
