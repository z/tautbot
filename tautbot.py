import time

from tautbot.config import conf

from tautbot.bot import Tautbot
from tautbot.plugin import plugin_registry
from tautbot.slack import slack_client
from tautbot.session import Session

session = Session()

if __name__ == "__main__":

    plugin_registry.register_plugin_list(plugins=conf['plugins'])

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
