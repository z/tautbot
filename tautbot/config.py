import configparser
import logging.config
import os

config_file = 'tautbot.ini'
logging_config_file = 'tautbot.logging.ini'

if not os.path.isfile(config_file):
    SystemExit('Config not found.')

config = configparser.ConfigParser()
config.read(config_file)

if os.environ.get("BOT_ID"):
    bot_id = os.environ.get("BOT_ID")
else:
    bot_id = config['tautbot']['bot_id']

if os.environ.get("SLACK_BOT_TOKEN"):
    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
else:
    slack_bot_token = config['tautbot']['slack_bot_token']

plugins_str = config.get('tautbot', 'plugins', fallback='Hello Google Urban Cat Flip Joke List')
plugins = plugins_str.split(' ')

conf = {
    'bot_prefix': config.get('tautbot', 'bot_prefix', fallback=','),
    'plugins': plugins,
    'bot_id': bot_id,
    'slack_bot_token': slack_bot_token,
    'at_bot': "<@{}>".format(bot_id),
    'tickrate': int(config['tautbot']['tickrate']),
    'data_dir': config.get('tautbot', 'data', fallback='data'),
    'giphy_api_key': config.get('tautbot', 'giphy_api_key', fallback='dc6zaTOxFJmzC'),  # Public beta test key
    'weather_api_key': config.get('tautbot', 'weather_api_key', fallback=None),
}

logging.config.fileConfig(logging_config_file, defaults={
    'log_filename': os.path.expanduser('tautbot.log')
})
