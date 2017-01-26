import re
import requests

from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Cat(PluginBase, Observer):
    def __init__(self, command='cat'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'}
        self.base_url = 'http://random.cat/meow'

    def events(self, *args, **kwargs):
        print('registered events for: {}'.format(self.name))
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^cat$', command):
            self.random_cat(channel)

    def random_cat(self, channel):
        # fetch
        try:
            request = requests.get(self.base_url, headers=self.headers)
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get cat: {}".format(e)

        data = request.json()
        image = data['file']

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=image, as_user=True)
