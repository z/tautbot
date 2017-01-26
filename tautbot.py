import re
import time

from tautbot.config import conf
from tautbot.events import Event
from tautbot.plugin import plugin_registry
from tautbot.slack import slack_client
from tautbot.session import Session

session = Session()


class Tautbot:

    def __init__(self, slack_client=slack_client, plugin_registry=plugin_registry):
        self.slack_client = slack_client
        self.plugin_registry = plugin_registry

    @staticmethod
    def parse_slack_output(output_lines):
        """
          Find command or pattern
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        if output_lines and len(output_lines) > 0:
            for output in output_lines:

                if output and 'text' in output:
                    patterns = '(?:({}))'.format('|'.join([p[0] for p in plugin_registry.patterns]))
                    _matches = re.match(patterns, output['text'])
                    _channel = output['channel']

                    Event('pre_parse_slack_output', output, _channel)

                    if _matches:
                        _pattern = _matches.group(0)
                        Event('channel_pattern_matched', pattern=_pattern, channel=_channel, text=output['text'], output=output)

                    elif conf['at_bot'] in output['text']:
                        # text after the @ mention, whitespace removed
                        _command = output['text'].split(conf['at_bot'])[1].strip().lower()
                        if _command in plugin_registry.commands:
                            Event('channel_command', command=_command, channel=_channel, text=output['text'], output=output)
                        elif _command in [p[0] for p in plugin_registry.aliases]:
                            Event('channel_alias', command=_command, channel=_channel, text=output['text'], output=output)

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None


if __name__ == "__main__":

    plugin_registry.register_plugin_list(['Trivia', 'Hello'])

    if slack_client.rtm_connect():
        tautbot = Tautbot(slack_client=slack_client, plugin_registry=plugin_registry)
        session.tautbot = tautbot
        print("tautbot connected and running!")

        channels = tautbot.list_channels()

        if channels:
            print("Channels: ")
            for c in channels:
                print(c['name'] + " (" + c['id'] + ")")

        while True:
            tautbot.parse_slack_output(slack_client.rtm_read())
            time.sleep(conf['tickrate'])
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
