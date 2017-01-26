import re
from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Hello(PluginBase, Observer):
    def __init__(self, command='hello',
                       patterns=(
                          ('^hello!$', 'say_hello_world'),
                          ('^ni!$', 'say_ni')
                       )):
        super(self.__class__, self).__init__(command=command, patterns=patterns)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        print('registered events for: {}'.format(self.name))
        self.observe('channel_pattern_matched', self.route_event)

    def route_event(self, pattern, channel, text, output):
        if re.match('^hello!$', pattern):
            self.say_hello_world(channel)
        if re.match('^ni!$', pattern):
            self.say_ni(channel)

    @staticmethod
    def say_hello_world(channel):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Hello World!", as_user=True)

    @staticmethod
    def say_ni(channel):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text='We are the Knights who say..... "Ni"!', as_user=True)