from slackclient import SlackClient
from tautbot.config import conf

slack_client = SlackClient(conf['slack_bot_token'])
