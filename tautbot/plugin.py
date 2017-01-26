import importlib
from abc import ABCMeta, abstractmethod


class PluginRegistry:
    def __init__(self):
        self.plugins = []
        self.commands = []
        self.aliases = []
        self.patterns = []
        self.instances = {}

    def register_plugin(self, name, command, subcommands=None, aliases=None, patterns=None, instance=None):
        """
        Register a plugin to the global registry for quick look-ups and routing

        :param name:
            Plugin Name (MUST be class name)
        :type name: ``str``

        :param command:
            Main command (SHOULD be class name lowercased)
        :type command: ``str``

        :param subcommands:
            (optional) A mapping of subcommands to class methods
            These are matched combined with command, e.g. "command subcommand"
            A tuple of key/value tuples ((echo, do_echo), (run, run_it))
        :type subcommands: ``tuple``

        :param aliases:
            (optional) A mapping of aliases to class methods
            A tuple of key/value tuples ((echo, do_echo), (run, run_it))
        :type aliases: ``tuple``

        :param patterns:
            (optional) A mapping of regex patterns to class methods
            A tuple of key/value tuples (('^Hello!$', say_hi), ('CAP-[0-9]+', find_jira_ticket))
        :type patterns: ``tuple``

        :returns: ``MapPackage``
        """
        entry_points = {'name': name, 'command': command, 'subcommands': subcommands,
                        'aliases': aliases, 'patterns': patterns, 'instance': instance}
        self.plugins.append(entry_points)

        _class = getattr(importlib.import_module("tautbot.plugins.{}".format(name.lower())), name)
        self.commands.append({command: _class})

        if aliases:
            for alias in aliases:
                self.aliases.append(alias)

        if patterns:
            for pattern in patterns:
                self.patterns.append(pattern)

        self.instances.update({name: instance})

        return entry_points

    def register_plugin_list(self, plugins):
        """
        A helper to register a list of plugins quickly from a list of class names.
        All metadata is pulled from the class.

        :param plugins:
            A list of plugin Class names e.g. ['Trivia']
        :type plugins: ``list``

        :returns: ``MapPackage``
        """
        for p in plugins:
            try:
                _class = getattr(importlib.import_module("tautbot.plugins.{}".format(p.lower())), p)
                plugin = _class()
                self.register_plugin(name=plugin.name, command=plugin.command, subcommands=plugin.subcommands, aliases=plugin.aliases, patterns=plugin.patterns, instance=plugin)
                plugin.events()
            except FileExistsError as e:
                raise SystemExit("Failed to load plugin: {}: {}".format(p, e))


class PluginBase(metaclass=ABCMeta):
    """
    PluginBase interface

    :param command:
        Main command (SHOULD be class name lowercased)
    :type command: ``str``

    :param subcommands:
        (optional) A mapping of subcommands to class methods.
        These are matched combined with command, e.g. "command subcommand"
        A tuple of key/value tuples ((echo, do_echo), (run, run_it))
    :type subcommands: ``tuple``

    :param aliases:
        (optional) A mapping of aliases to class methods
        A tuple of key/value tuples ((echo, do_echo), (run, run_it))
    :type aliases: ``tuple``

    :param patterns:
        (optional) A mapping of regex patterns to class methods
        A tuple of key/value tuples (('^Hello!$', say_hi), ('CAP-[0-9]+', find_jira_ticket))
    :type patterns: ``tuple``

    :returns: ``MapPackage``
    """
    def __init__(self, command=None, subcommands=None, aliases=None, patterns=None):
        self.plugin_registry = plugin_registry
        self.command = command
        self.subcommands = subcommands
        self.aliases = aliases
        self.patterns = patterns
        self.name = self.__class__.__name__

        if not self.command:
            self.command = self.name.lower()

    @abstractmethod
    def events(self, *args, **kwargs):
        pass


plugin_registry = PluginRegistry()
