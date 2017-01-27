import random
import re

import requests

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Giphy(PluginBase, Observer):
    def __init__(self, command='giphy'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'}
        self.base_url = 'http://api.giphy.com/v1/gifs'

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        text = text.replace(command, '').strip()
        if re.match('^giphy', command):
            self.giphy(command, channel, text)

    def giphy(self, command, channel, text):
        """Searches giphy.com for a gif using the provided search term."""
        search_url = self.base_url + '/search'
        params = {
            'q': text,
            'limit': 10,
            'fmt': "json",
            'api_key': self.conf['giphy_api_key']
        }

        r = None
        response = 'No gif found.'

        # fetch
        try:
            results = requests.get(search_url, params=params)
            r = results.json()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            response = "Could not get gif".format(e)

        if 'data' in r and r['data']:
            gif = random.choice(r['data'])
            if gif['rating']:
                response = "{} content rating: {}. (Powered by GIPHY)".format(gif['images']['downsized_large']['url'], gif['rating'].upper())
            else:
                response = "{} - (Powered by GIPHY)".format(gif['embed_url'])

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
