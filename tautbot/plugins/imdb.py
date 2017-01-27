import re
import requests

from tautbot.events import Observer
from tautbot.plugin import PluginBase
from tautbot.slack import slack_client


class IMDB(PluginBase, Observer):
    def __init__(self, command='imdb',
                       patterns=(
                           ('(.*:)//(imdb.com|www.imdb.com)(:[0-9]+)?(.*)$', 'imdb_url'),
                           ('.*tt\d+', 'imdb'),
                       )):
        super(self.__class__, self).__init__(command=command, patterns=patterns)
        Observer.__init__(self)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'}
        self.imdb_re = '(.*:)//(imdb.com|www.imdb.com)(:[0-9]+)?(.*)$'
        self.id_re = 'tt\d+'

    def events(self, *args, **kwargs):
        self.observe('channel_pattern_matched', self.route_event)

    def route_event(self, pattern, channel, text, output):
        if re.match(self.imdb_re, text):
            self.imdb_url(channel, text, output)
        if re.match(self.id_re, text):
            self.imdb(channel, text, output)

    def imdb_url(self, channel, text, output):

        match = re.match(self.imdb_re, text)

        imdb_id = match.group(4).split('/')[-1]
        if imdb_id == "":
            imdb_id = match.group(4).split('/')[-2]

        imdb_id = str(imdb_id).replace('>', '')

        self.imdb(channel, imdb_id, output=output)

    def imdb(self, channel, text, output):
        """imdb <movie> - gets information about <movie> from IMDb"""

        if 'user' not in output or output['user'] == self.conf['bot_id']:
            return

        strip = text.strip()
        re.match(self.id_re, text)

        if re.match(self.id_re, strip):
            params = {'i': strip}
        else:
            params = {'t': strip}

        request = requests.get("http://www.omdbapi.com/", params=params, headers=self.headers)
        content = request.json()

        if content.get('Error', None) == 'Movie not found!':
            response = 'Movie not found!'
        elif content['Response'] == 'True':
            content['URL'] = 'http://www.imdb.com/title/{}'.format(content['imdbID'])

            out = '*{Title}* ({Year}) ({Genre}): {Plot}'
            if content['Runtime'] != 'N/A':
                out += ' _{Runtime}_.'
            if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
                out += ' _{imdbRating}_/10 with _{imdbVotes}_' \
                       ' votes.'
            out += ' {URL}'
            response = out.format(**content)
        else:
            response = 'Unknown error.'

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
