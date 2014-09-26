from collections import Sequence, namedtuple


class HookExecutionResult(namedtuple('HookExecutionResult',
                                     'plugin,result,exception')):
    """Named tuple representing a hook execution result"""

    __slots__ = []

    def __repr__(self):
        return ("HookExecutionResult(plugin={0!r}, "
                "result={1!r}, exception={2!r})").format(
                    plugin=self.plugin,
                    result=self.result,
                    exception=self.exception)


class PluginManager(Sequence):
    def __init__(self, iterable):
        self._plugins = []
        self._plugins.extend(iterable)

    def call_hook(self, hook_type, *args, **kwargs):
        return list(self.call_hook_async(hook_type, *args, **kwargs))

    def call_hook_async(self, hook_type, *args, **kwargs):
        for plugin in self._plugins:
            for res in plugin.call_hook_async(hook_type, *args, **kwargs):
                yield res

    def __getitem__(self, item):
        return self._plugins[item]

    def __len__(self):
        return len(self._plugins)

    def __iter__(self):
        return iter(self._plugins)

    def __contains__(self, item):
        return item in self._plugins
