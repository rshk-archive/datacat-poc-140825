from datacat.settings.default import *  # noqa

# We want this plugin to be included
PLUGINS.append('datacat.utils.testing.plugins:dummy_plugin')
