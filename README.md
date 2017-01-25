# tautbot

A bot for Slack

Create a `tautbot.ini` file with the following content, substituting the placeholders for their real values:

```
[tautbot]

bot_id = xxxxxxxx
slack_bot_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Run the bot out of this directory:

```
python tautbot.py
```

These values can be passed as environment variables as well: 

```
BOT_ID=xxxxxx; SLACK_BOT_TOKEN=xxxxxxxxxxxxxxxxx; python tautbot.py
```