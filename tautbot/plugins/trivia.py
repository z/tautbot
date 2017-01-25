import json
import urllib
import urllib.request
import urllib.error
import re

from tautbot.plugin import PluginBase


class Trivia(PluginBase):
    def __init__(self, command='trivia',
                       subcommands=(
                          ('question', 'get_trivia_question'),
                          ('answer', 'get_trivia_answer')
                       ), aliases=None):
        super(self.__class__, self).__init__(command=command, subcommands=subcommands, aliases=aliases)
        self.base_url = "http://jservice.io/api"
        self.current = None

    def foo(self):
        pass

    @staticmethod
    def api_request(url):
        req = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(req)
            raw_data = response.read()
            data = json.loads(raw_data.decode("utf-8"))
        except urllib.error.HTTPError as err:
            print("API Request Error: {0}".format(err))
            raise UserWarning

        return data

    def get_trivia_question(self):
        endpoint = '/random'

        data = self.api_request("{}{}".format(self.base_url, endpoint))
        self.current = data[0]

        answer = self.current['answer']
        answer = re.sub(r'^"|<.*?>|"$', '', answer.replace('\"', '').replace("\'", ""))
        self.current['answer'] = answer

        return self.current

    def get_trivia_answer(self):
        answer = None

        if self.current:
            answer = self.current['answer']

        self.current = None

        return answer
