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

conf = {
    'bot_id': bot_id,
    'slack_bot_token': slack_bot_token,
    'at_bot': "<@{}>".format(bot_id),
    'tickrate': int(config['tautbot']['tickrate']),
    'data_dir': config.get('tautbot', 'data', fallback='data'),
}

logging.config.fileConfig(logging_config_file, defaults={
    'log_filename': os.path.expanduser('tautbot.log')
})
