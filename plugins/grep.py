import re

from sqlalchemy import Table, Column, String, Integer, Float, UniqueConstraint, desc
from sqlalchemy.sql import select

from tautbot.client.slack import slack_client
from tautbot.client.slack import slack_helpers
from tautbot.plugin import PluginBase
from tautbot.util import database
from tautbot.util.events import Observer

table = Table(
    "logs",
    database.metadata,
    Column('id', Integer, primary_key=True),
    Column("ts", Float(20)),
    Column("user_id", String(25)),
    Column("user_name", String(100)),
    Column("channel_id", String(25)),
    Column("channel_name", String(65)),
    Column("line", String(1000)),
    UniqueConstraint('id', 'ts', 'user_id', 'channel_id'),
    sqlite_autoincrement=True
)

database.metadata.create_all()


class Grep(PluginBase, Observer):
    def __init__(self, command='grep'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        self.observe('pre_parse_slack_output', self.add_log_line)
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if 'user' not in output or output['user'] == self.conf['bot_id']:
            return
        if re.match('^grep', text):
            text = text.replace(command, '').strip()
            self.grep(channel, text)

    def add_log_line(self, output, channel):
        if 'user' not in output or output['user'] == self.conf['bot_id']:
            return
        ts = output['ts']
        user_id = output['user']
        #user_name = slack_helpers.get_user(user_id)
        channel_id = output['channel']
        line = output['text']
        query = table.insert().values(
            ts=ts,
            user_id=user_id,
            user_name=user_id,
            channel_id=channel_id,
            channel_name=channel_id,
            line=line,
        )
        database.db.execute(query)
        database.db.commit()

    @staticmethod
    def grep(channel, text):
        query = select([table.c.ts, table.c.user_id, table.c.line]) \
                       .where(table.c.line.like("%{}%".format(text))) \
                       .order_by(desc(table.c.ts)) \
                       .limit(50)
        lines = database.db.execute(query)

        template = '```'
        data = []

        for row in lines:
            if not re.match("^,grep .*", row.line):
                template += '*{}* | {}: {}\n'
                data.append(row.ts)
                data.append(row.user_id)
                data.append(row.line)

        template += '```'

        if data:
            response = template.format(*data)
        else:
            response = "No lines found."

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
