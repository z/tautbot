import random
import re
import requests

from bs4 import BeautifulSoup

from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Google(PluginBase, Observer):
    def __init__(self, command='google',
                 aliases=(
                     ('google', 'google_search'),
                     ('gis', 'google_image_search')
                 )):
        super(self.__class__, self).__init__(command=command, aliases=aliases)
        Observer.__init__(self)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'}
        self.base_url = 'http://dogpile.com/search'

    def events(self, *args, **kwargs):
        print('registered events for: {}'.format(self.name))
        self.observe('channel_command', self.route_event)
        self.observe('channel_alias', self.route_event)

    def route_event(self, command, channel, text, output):
        text = text.replace(command, '').strip()
        if re.match('^gis', command):
            self.google_image_search(channel, text)
        if re.match('^google$', command):
            self.google_search(channel, text)

    def google_image_search(self, channel, text):
        image_url = self.base_url + "/images"
        params = {'q': " ".join(text.split())}
        r = requests.get(image_url, params=params, headers=self.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        web_results = soup.find('div', id="webResults")

        if web_results:
            linklist = web_results.find_all('a', {'class': 'resultThumbnailLink'})
            image = requests.get(random.choice(linklist)['href'], headers=self.headers).url

            slack_client.api_call("chat.postMessage", channel=channel,
                                  text=image, as_user=True)
        else:
            slack_client.api_call("chat.postMessage", channel=channel,
                                  text='No results found.', as_user=True)

    def google_search(self, channel, text):
        web_url = self.base_url + "/web"
        params = {'q': " ".join(text.split())}
        r = requests.get(web_url, params=params, headers=self.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        web_results = soup.find('div', id="webResults")

        if web_results:
            result_url = requests.get(web_results.find_all('a', {'class': 'resultDisplayUrl'})[0]['href'], headers=self.headers).url
            result_description = soup.find('div', id="webResults").find_all('div', {'class': 'resultDescription'})[0].text
            print(result_url, result_description)
            response = "{} -- {}".format(result_url, result_description)

            slack_client.api_call("chat.postMessage", channel=channel,
                                  text=response, as_user=True)
        else:
            slack_client.api_call("chat.postMessage", channel=channel,
                                  text='No results found.', as_user=True)