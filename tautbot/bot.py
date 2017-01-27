import re

from tautbot.base import Base
from tautbot.events import Event


class Tautbot(Base):

    def __init__(self, slack_client=None, plugin_registry=None):
        super().__init__()
        self.slack_client = slack_client
        self.plugin_registry = plugin_registry

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

                    patterns = '(?:({}))'.format('|'.join([p[0] for p in self.plugin_registry.patterns]))
                    _matches = re.match(patterns, output['text'])
                    _channel = output['channel']

                    Event('pre_parse_slack_output', output, _channel)

                    self.logger.debug("{}".format(output))

                    if _matches:
                        _pattern = _matches.group(0)
                        Event('channel_pattern_matched', pattern=_pattern, channel=_channel, text=output['text'], output=output)

                    if self.conf['at_bot'] in output['text']:

                        # text after the @ mention, whitespace removed
                        _message = output['text'].split(self.conf['at_bot'])[1].strip().lower()
                        _command = _message.split(" ")[0]

                        self.logger.info('command "{}" called by user: {}'.format(_command, output['user']))

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
