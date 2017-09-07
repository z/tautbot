# tautbot

A bot for Slack.

Get your ID and Token here by creating a new app: https://api.slack.com/apps

Create a `tautbot.ini` file with the following content, substituting the placeholders for their real values:

```ini
[tautbot]

bot_prefix = ,
plugins = Trivia Hello Google Urban Cat Flip Joke List DWI IMDB Giphy Factoid Fight Ask Calc Weather
tickrate = 1

bot_id = xxxxxxxxx
slack_bot_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# https://developers.giphy.com/
giphy_api_key = xxxxxxxxx
# https://openweathermap.org/
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

### Examples

#### Command

```python
import re

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Hello(PluginBase, Observer):
    def __init__(self, command='hello'):
        super(self.__class__, self).__init__(command=command, patterns=patterns)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.say_hello_world)

    def say_hello_world(self, pattern, channel, text, output):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Hello World!", as_user=True)
```

Triggered by `,hello`

#### Pattern

```python
import re

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Hello(PluginBase, Observer):
    def __init__(self, command='hello',
                       patterns=(
                          ('^hello!$', 'say_hello_world'),
                       )):
        super(self.__class__, self).__init__(command=command, patterns=patterns)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        self.observe('channel_pattern_matched', self.say_hello_world)

    def say_hello_world(self, pattern, channel, text, output):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Hello World!", as_user=True)
```

Triggered by `hello!`

Reference other plugins for more examples.

## Credits

Many ideas, and plugins adapted from [CloudBot](https://github.com/CloudBotIRC/CloudBot)

## License

GNU GENERAL PUBLIC LICENSE, Version 3