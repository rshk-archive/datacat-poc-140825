from datacat.settings.default import *  # noqa

# We want this plugin to be included
PLUGINS = list(PLUGINS)
PLUGINS.append('datacat.utils.testing.plugins:dummy_plugin')

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
