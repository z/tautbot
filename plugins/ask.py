import re

from cleverbot import Cleverbot

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Ask(PluginBase, Observer):
    def __init__(self, command='ask'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.cb = Cleverbot('cleverbot-tautbot')

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^ask', command):
            text = text.replace(command, '').strip()
            self.ask(channel, text)

    def ask(self, channel, text):
        response = self.cb.ask(text)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
