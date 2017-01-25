from abc import ABCMeta, abstractmethod
import importlib


class PluginRegistry:
    def __init__(self):
        self.plugins = []
        self.commands = []
        self.aliases = []

    def register_plugin(self, name, command, subcommands, aliases):
        entry_points = {'name': name, 'command': command, 'subcommands': subcommands, 'aliases': aliases}
        self.plugins.append(entry_points)

        _class = getattr(importlib.import_module("tautbot.plugins.{}".format(name.lower())), name)
        self.commands.append({command: _class})

        if aliases:
            for alias in aliases:
                self.aliases.append(alias)

        return entry_points

    def register_plugin_list(self, plugins):
        for p in plugins:
            try:
                _class = getattr(importlib.import_module("tautbot.plugins.{}".format(p.lower())), p)
                plugin = _class()
                self.register_plugin(name=plugin.name, command=plugin.command, subcommands=plugin.subcommands, aliases=plugin.aliases)
            except Exception:
                raise SystemExit("Failed to load plugin: {}".format(p.name))


class PluginBase(metaclass=ABCMeta):
    def __init__(self, command=None, subcommands=None, aliases=None):
        self.plugin_registry = plugin_registry
        self.command = command
        self.subcommands = subcommands
        self.aliases = aliases
        self.name = self.__class__.__name__

        if not self.command:
            self.command = self.name.lower()

    @abstractmethod
    def foo(self):
        pass


plugin_registry = PluginRegistry()
