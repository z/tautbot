import random
import re

from tautbot.events import Observer
from tautbot.plugin import PluginBase
from tautbot.slack import slack_client


class DWI(PluginBase, Observer):
    def __init__(self, command='dwi'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.one_liner = None
        self.macros = [
            'https://i.imgur.com/WhgY2sX.gif',
            'https://i.imgur.com/eGInc.jpg',
            'https://i.imgur.com/KA3XSt5.gif',
            'https://i.imgur.com/rsuXB69.gif',
            'https://i.imgur.com/fFXmuSS.jpg',
            'https://j.gifs.com/L9mmYr.gif',
            'https://i.imgur.com/nxMBqb4.gif',
        ]
        self.phrases = [
            'Stop complaining, {}, and',
            'Psssh {}, just',
            'Looks like {} needs to',
            'Ever think that {} just needs to'
        ]

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^dwi\s+[@\w+\d+]', text):
            user = text.split(' ')[1]
            self.dealwithit(channel, user)

    def dealwithit(self, channel, user):
        response = '{} {}'.format(random.choice(self.phrases).format(user), random.choice(self.macros))

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
