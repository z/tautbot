from slackclient import SlackClient

from tautbot.config import conf

slack_client = SlackClient(conf['slack_bot_token'])


class SlackHelpers:

    def __init__(self):
        self.user_list = {}
        self.channel_list = {}

    def get_users(self):
        if slack_client:
            if len(self.user_list) == 0:
                data = slack_client.api_call("users.list")
                if data['ok']:
                    self.user_list = data['members']
            return self.user_list
        return None

    def get_user(self, user_id):
        if len(self.user_list) == 0:
            self.user_list = self.get_users()
        try:
            index = next(index for (index, d) in enumerate(self.user_list) if d['id'] == user_id)
            return self.user_list[index]['name']
        except StopIteration:
            return user_id

    def get_channels(self):
        if slack_client:
            data = slack_client.api_call("channels.list")
            if data['ok']:
                self.channel_list = data['channels']
            return self.channel_list
        return None

    def get_channel(self, channel_id):
        if len(self.channel_list) == 0:
            self.channel_list = self.get_channels()
        try:
            index = next(index for (index, d) in enumerate(self.channel_list) if d['id'] == channel_id)
            return self.channel_list[index]['name']
        except StopIteration:
            return channel_id

slack_helpers = SlackHelpers()
