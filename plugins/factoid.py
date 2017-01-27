import re
from collections import defaultdict

from sqlalchemy import Table, Column, String, PrimaryKeyConstraint

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util import database
from tautbot.util.events import Observer

table = Table(
    "factoid",
    database.metadata,
    Column("word", String(25)),
    Column("data", String(500)),
    Column("nick", String(25)),
    Column("chan", String(65)),
    PrimaryKeyConstraint('word', 'chan')
)

database.metadata.create_all()


class Factoid(PluginBase, Observer):
    def __init__(self, command='factoid',
                       aliases=(
                           ('info', 'info'),
                       )):
        super(self.__class__, self).__init__(command=command, aliases=aliases)
        Observer.__init__(self)
        self.default_dict = {"who": "https://github.com/z"}
        self.factoid_cache = defaultdict(lambda: self.default_dict)
        self.load_cache()

    def events(self, *args, **kwargs):
        self.observe('channel_alias', self.route_event)
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if command == 'factoid':
            text = text.replace(command, '').strip()

            if re.match('^list$', text):
                self.list_factoids(channel)

            elif re.match('^add .+', text):
                _text_parts = text.split(' ')[2:]
                word = _text_parts[0].strip()
                data = ' '.join(_text_parts[1:])
                self.add_factoid(channel, word, data)

            elif re.match('^delete [\w\d]+', text):
                _text_parts = text.split(' ')[2:]
                word = _text_parts[0].strip()
                self.delete_factoid(channel, word)

            elif re.match('^info [\w\d]+', text):
                _text_parts = text.split(' ')
                word = _text_parts[1].strip()
                print('>>>> ' + word)
                self.info(channel, word)

    def load_cache(self):
        for row in self.db.execute(table.select()):
            # assign variables
            chan = row["chan"]
            word = row["word"]
            data = row["data"]
            if chan not in self.factoid_cache:
                self.factoid_cache.update({chan: {word: data}})
            elif word not in self.factoid_cache[chan]:
                self.factoid_cache[chan].update({word: data})
            else:
                self.factoid_cache[chan][word] = data

    def add_factoid(self, channel, word, data, nick="BOT"):
        """
        adds a factoid
        """
        if word in self.factoid_cache[channel]:
            # if we have a set value, update
            self.db.execute(table.update().values(data=data, nick=nick, chan=channel).where(table.c.chan == channel).where(table.c.word == word))
            self.db.commit()
        else:
            # otherwise, insert
            self.db.execute(table.insert().values(word=word, data=data, nick=nick, chan=channel))
            self.db.commit()
        self.load_cache()

    def delete_factoid(self, channel, word):
        self.db.execute(table.delete().where(table.c.word == word).where(table.c.chan == channel))
        self.db.commit()
        self.load_cache()

    def list_factoids(self, channel):
        """- lists all available factoids"""
        reply_text = []
        reply_text_length = 0
        response = ''

        for word in self.factoid_cache[channel].keys():
            added_length = len(word) + 2
            if reply_text_length + added_length > 400:
                response = ", ".join(reply_text)
                reply_text = []
                reply_text_length = 0
            else:
                reply_text.append(word)
                reply_text_length += added_length
                response = ", ".join(reply_text)

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)

    def info(self, channel, word):
        """<factoid> - shows the source of a factoid"""
        if word in self.factoid_cache[channel]:
            response = self.factoid_cache[channel][word]
        else:
            response = "Unknown Factoid."

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
