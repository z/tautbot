import codecs
import os
import random
import re

from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Joke(PluginBase, Observer):
    def __init__(self, command='joke'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.one_liner = None
        self.load_jokes()

    def load_jokes(self):
        with codecs.open(os.path.join(self.conf['data_dir'], "one_liners.txt"), encoding="utf-8") as f:
            self.one_liner = [line.strip() for line in f.readlines() if not line.startswith("//")]

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^joke$', command):
            self.say_joke(channel)

    def say_joke(self, channel):
        joke = random.choice(self.one_liner)

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=joke, as_user=True)
