import json
import urllib
import urllib.request
import urllib.error
import re

from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Trivia(PluginBase, Observer):
    def __init__(self, command='trivia',
                       subcommands=(
                          ('question', 'get_trivia_question'),
                          ('answer', 'get_trivia_answer')
                       )):
        super(self.__class__, self).__init__(command=command, subcommands=subcommands)
        Observer.__init__(self)
        self.base_url = "http://jservice.io/api"
        self.current = None

    def events(self, *args, **kwargs):
        self.observe('pre_parse_slack_output', self.think)
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

    def send_new_question(self, channel):
        q = self.get_trivia_question()
        print(q)
        print(q['answer'])
        response = "[{}] {}?".format(q['category']['title'], q['question'])

        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def think(self, output, channel):
        if self.current:
            current_answer = self.current['answer']

            if re.match('({}?)'.format(current_answer), output):
                answer = self.get_trivia_answer()
                if answer:
                    response = "Yay! You answered it correctly: {}".format(answer)
                    slack_client.api_call("chat.postMessage", channel=channel,
                                          text=response, as_user=True)
                    self.send_new_question(channel)

