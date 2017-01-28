import json
import re
import urllib
import urllib.error
import urllib.request

from sqlalchemy import Table, Column, String, Integer, PrimaryKeyConstraint
from sqlalchemy.sql import select

from tautbot.client.slack import slack_client
from tautbot.client.slack import slack_helpers
from tautbot.plugin import PluginBase
from tautbot.util import database
from tautbot.util.events import Observer

table = Table(
    "trivia_score",
    database.metadata,
    Column("id", String(20)),
    Column("score", Integer),
    Column("name", String(25)),
    Column("channel", String(65)),
    PrimaryKeyConstraint('id', 'channel')
)

database.metadata.create_all()


class Trivia(PluginBase, Observer):
    def __init__(self, command='trivia',
                 subcommands=(
                    ('question', 'get_trivia_question'),
                    ('answer', 'get_trivia_answer')
                 ),
                 aliases=(
                    ('question', 'get_trivia_question'),
                    ('answer', 'get_trivia_answer')
                 )):
        super(self.__class__, self).__init__(command=command, aliases=aliases, subcommands=subcommands)
        Observer.__init__(self)
        self.base_url = "http://jservice.io/api"
        self.current = None

    def events(self, *args, **kwargs):
        self.observe('pre_parse_slack_output', self.think)
        self.observe('channel_alias', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^question$', command):
            self.send_new_question(channel)
        if re.match('^answer$', command):
            self.send_trivia_answer(channel)

    def api_request(self, url):
        req = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(req)
            raw_data = response.read()
            data = json.loads(raw_data.decode("utf-8"))
        except urllib.error.HTTPError as err:
            self.logger.error("API Request Error: {0}".format(err))
            raise UserWarning

        return data

    def get_trivia_question(self):
        endpoint = '/random'

        data = self.api_request("{}{}".format(self.base_url, endpoint))
        self.current = data[0]

        answer = self.current['answer']
        answer = re.sub(r'^"|<.*?>|\(.*?\)|"$', '', answer.replace('\"', '').replace("\'", ""))
        self.current['answer'] = answer

        return self.current

    def send_new_question(self, channel):
        q = self.get_trivia_question()

        self.logger.debug('Question JSON: {}'.format(q))
        self.logger.info('Question: {}'.format(q['question']))
        self.logger.info('Answer: {}'.format(q['answer']))

        response = "[{}] {}?".format(q['category']['title'], q['question'])
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def get_trivia_answer(self):
        answer = None

        if self.current:
            answer = self.current['answer']

        self.current = None

        return answer

    def send_trivia_answer(self, channel):
        answer = self.get_trivia_answer()
        response = "The answer was: {}".format(answer)

        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def think(self, output, channel):
        if self.current:
            current_answer = self.current['answer']
            user_id = output['user']

            if current_answer.lower() == output['text'].lower():
                answer = self.get_trivia_answer()
                if answer:

                    name = slack_helpers.get_user(output['user'])

                    score = database.db.execute(select([table.c.score])
                                       .where(table.c.id == user_id)
                                       .where(table.c.channel == channel)).fetchone()

                    if score:
                        score = score[0]
                        score += 1
                        self.db_update(user_id, score, name, channel)
                    else:
                        score = 1
                        self.db_insert(user_id, score, name, channel)

                    response = "Yay! {} (score: *{}*) answered it correctly: {}".format(name, score, answer)
                    slack_client.api_call("chat.postMessage", channel=channel,
                                          text=response, as_user=True)
                    self.send_new_question(channel)

    @staticmethod
    def db_insert(user_id, score, name, channel):
        query = table.insert().values(
            id=user_id,
            score=score,
            name=name,
            channel=channel,
        )
        database.db.execute(query)
        database.db.commit()

    @staticmethod
    def db_update(user_id, score, name, channel):
        query = table.update() \
            .where(table.c.id == user_id) \
            .where(table.c.channel == channel) \
            .where(table.c.name == name) \
            .values(score=score)
        database.db.execute(query)
        database.db.commit()
