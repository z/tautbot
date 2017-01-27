import re

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.plugin import plugin_registry
from tautbot.util.events import Observer


class List(PluginBase, Observer):
    def __init__(self, command='list'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^list$', command):
            self.list_plugins(channel)

    @staticmethod
    def list_plugins(channel):
        response = ' '.join(sorted({k for d in plugin_registry.commands for k in d}))

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
