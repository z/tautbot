import time

from tautbot.bot import Tautbot
from tautbot.client import slack
from tautbot.config import conf
from tautbot.plugin import plugin_registry
from tautbot.util.session import Session

session = Session()

if __name__ == "__main__":

    if slack.slack_client.rtm_connect():
        tautbot = Tautbot(slack_client=slack.slack_client, plugin_registry=plugin_registry)
        session.tautbot = tautbot
        print("tautbot connected and running!")

        channels = slack.slack_helpers.get_channels()

        if channels:
            print("Channels: ")
            for c in channels:
                print(c['name'] + " (" + c['id'] + ")")

        slack.slack_user_list = slack.slack_helpers.get_users()

        plugin_registry.register_plugin_list(plugins=conf['plugins'])

        while True:
            tautbot.parse_slack_output(slack.slack_client.rtm_read())
            time.sleep(conf['tickrate'])
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
