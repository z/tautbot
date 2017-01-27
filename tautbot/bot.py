import re

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData

from tautbot.base import Base
from tautbot.client import slack
from tautbot.util import database
from tautbot.util.events import Event


class Tautbot(Base):

    def __init__(self, slack_client=None, plugin_registry=None):
        super().__init__()
        self.slack_client = slack_client
        self.plugin_registry = plugin_registry
        self.userlist = []

        # setup db
        db_path = self.conf.get('database', 'sqlite:///tautbot.db')
        self.db_engine = create_engine(db_path)
        self.db_factory = sessionmaker(bind=self.db_engine)
        self.db_session = scoped_session(self.db_factory)
        self.db_metadata = MetaData()
        self.db_base = declarative_base(metadata=self.db_metadata, bind=self.db_engine)
        self.db = self.db_session()

        # set botvars so plugins can access when loading
        database.metadata = self.db_metadata
        database.base = self.db_base

        if slack_client:
            slack.slack_client = slack_client

        self.logger.debug("Database system initialised.")

    def parse_slack_output(self, output_lines):
        """
          Find command or pattern
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        if output_lines and len(output_lines) > 0:
            for output in output_lines:

                if output and 'text' in output:

                    _prefix_matches = re.match('^{}'.format(self.conf['bot_prefix']), output['text'])
                    _bot_matches = re.match('^{}'.format(self.conf['at_bot']), output['text'])
                    patterns = '(?:({}))'.format('|'.join([p[0] for p in self.plugin_registry.patterns]))
                    _pattern_matches = re.match(patterns, output['text'])
                    _channel = output['channel']

                    Event('pre_parse_slack_output', output, _channel)

                    self.logger.debug("{}".format(output))

                    if _pattern_matches:
                        _pattern = _pattern_matches.group(0)
                        Event('channel_pattern_matched', pattern=_pattern, channel=_channel, text=output['text'], output=output)

                    if _bot_matches or _prefix_matches:

                        if _bot_matches:
                            # text after the @ mention, whitespace removed
                            _message = output['text'].split(self.conf['at_bot'])[1].strip().lower()
                            _command = _message.split(" ")[0]

                        elif _prefix_matches:
                            # text after the @ mention, whitespace removed
                            _message = output['text'].split(self.conf['bot_prefix'])[1].strip().lower()
                            _command = _message.split(" ")[0]
                        else:
                            self.logger.error('The impossible happened')
                            raise Warning("I have no idea what happened")

                        self.logger.info('command "{}" called by user: {}'.format(_command, output['user']))
                        self.route_command(_channel, _command, _message, output)

    def route_command(self, _channel, _command, _message, output):
        """
          Figure out what type of command it is
        """
        if _command in {k for d in self.plugin_registry.commands for k in d}:

            _message_parts = _message.split(" ")

            if len(_message_parts) > 1 and _message_parts[1] in self.plugin_registry.subcommands:
                Event('channel_subcommand', command=_command, channel=_channel, text=_message, output=output)
            else:
                Event('channel_command', command=_command, channel=_channel, text=_message, output=output)

        elif _command in [p[0] for p in self.plugin_registry.aliases]:
            self.logger.info('command "{}" recognized as alias'.format(_command))
            Event('channel_alias', command=_command, channel=_channel, text=_message, output=output)

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None

    @staticmethod
    def get_users():
        if slack.slack_client:
            data = slack.slack_client.api_call("users.list")
            return data['members']

    def get_user(self, user_id):
        slack.slack_userlist = self.get_users()
        index = next(index for (index, d) in enumerate(slack.slack_userlist) if d['id'] == user_id)

        return slack.slack_userlist[index]['real_name']
