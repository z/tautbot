from slackclient import SlackClient

from tautbot.config import conf

slack_client = SlackClient(conf['slack_bot_token'])

slack_userlist = {}


class SlackHelpers:
    @staticmethod
    def list_channels():
        channels_call = slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None

    @staticmethod
    def get_users():
        if slack_client:
            data = slack_client.api_call("users.list")
            return data['members']
        return None

    def get_user(self, user_id):
        slack_userlist = self.get_users()
        index = next(index for (index, d) in enumerate(slack_userlist) if d['id'] == user_id)

        return slack_userlist[index]['real_name']

slack_helpers = SlackHelpers()
