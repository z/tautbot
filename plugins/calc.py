import re

from asteval import Interpreter

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Calc(PluginBase, Observer):
    def __init__(self, command='calc'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.aeval = Interpreter()

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^calc', command):
            text = text.replace(command, '').strip()
            self.calc(channel, text)

    def calc(self, channel, text):
        response = self.aeval(text)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
