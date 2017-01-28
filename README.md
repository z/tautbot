# tautbot

A bot for Slack

Create a `tautbot.ini` file with the following content, substituting the placeholders for their real values:

```
[tautbot]

bot_prefix = ,
plugins = Trivia Hello Google Urban Cat Flip Joke List DWI IMDB Giphy Factoid Fight Ask Calc Weather
tickrate = 1

bot_id = xxxxxxxxx
slack_bot_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
giphy_api_key = xxxxxxxxx
weather_api_key = xxxxxxxxxxxxxxxxxxxxxxxxxx
```

Run the bot out of this directory:

```
python tautbot.py
```

These values can be passed as environment variables as well: 

```
BOT_ID=xxxxxx; SLACK_BOT_TOKEN=xxxxxxxxxxxxxxxxx; python tautbot.py
```

## Writing Plugins

Take a look at `PluginBase` in `tautbot/plugin.py` to see what current options are available.

### Example

```
import re
from tautbot.plugin import PluginBase
from tautbot.events import Observer
from tautbot.slack import slack_client


class Hello(PluginBase, Observer):
    def __init__(self, command='hello',
                       patterns=(
                          ('^hello!$', 'say_hello_world'),
                       )):
        super(self.__class__, self).__init__(command=command, patterns=patterns)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        print('registered events for: {}'.format(self.name))
        self.observe('channel_pattern_matched', self.route_event)

    @staticmethod
    def say_hello_world(channel):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Hello World!", as_user=True)
```

## Credits

Many ideas, and plugins adapted from CloudBot