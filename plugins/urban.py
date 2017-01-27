import random
import re

import requests

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Urban(PluginBase, Observer):
    def __init__(self, command='urban',
                 aliases=(
                     ('urand', 'urban'),
                 )):
        super(self.__class__, self).__init__(command=command, aliases=aliases)
        Observer.__init__(self)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
                        'Referer': 'http://m.urbandictionary.com'}
        self.base_url = 'http://api.urbandictionary.com/v0'

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)
        self.observe('channel_alias', self.route_event)

    def route_event(self, command, channel, text, output):
        text = text.replace(command, '').strip()
        if re.match('^urand', command):
            self.urban(channel, text=False)
        elif re.match('^urban', command):
            self.urban(channel, text)

    def urban(self, channel, text):
        """urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."""

        define_url = self.base_url + "/define"
        random_url = self.base_url + "/random"

        if text:
            # clean and split the input
            text = text.lower().strip()
            parts = text.split()

            # if the last word is a number, set the ID to that number
            if parts[-1].isdigit():
                id_num = int(parts[-1])
                # remove the ID from the input string
                del parts[-1]
                text = " ".join(parts)
            else:
                id_num = 1

            # fetch the definitions
            try:
                params = {"term": text}
                request = requests.get(define_url, params=params, headers=self.headers)
                request.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                return "Could not get definition: {}".format(e)

            page = request.json()

            if page['result_type'] == 'no_results':
                return 'Not found.'
        else:
            # get a random definition!
            try:
                request = requests.get(random_url, headers=self.headers)
                request.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                return "Could not get definition: {}".format(e)

            page = request.json()
            id_num = None

        definitions = page['list']

        if id_num:
            # try getting the requested definition
            try:
                definition = definitions[id_num - 1]

                def_text = " ".join(definition['definition'].split())  # remove excess spaces
                def_text = def_text[:200]
            except IndexError:
                return 'Not found.'

            url = definition['permalink']

            response = "[{}/{}] {} - {}".format(id_num, len(definitions), def_text, url)

        else:
            definition = random.choice(definitions)

            def_text = " ".join(definition['definition'].split())  # remove excess spaces
            def_text = def_text[:200]

            name = definition['word']
            url = definition['permalink']
            response = "{}: {} - {}".format(name, def_text, url)

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
