import time
from slackclient import SlackClient
from tautbot.trivia import Trivia
from tautbot.config import conf

EXAMPLE_COMMAND = "do"

TRIVIA_COMMAND = "question"
ANSWER_COMMAND = "answer"


class Tautbot:

    def __init__(self, slack_client, trivia):
        self.slack_client = slack_client
        self.trivia = trivia

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot, and determines if they
            are valid commands.
        """
        new_question = None
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
                   "* command with numbers, delimited by spaces."
        print("{}: {}".format(channel, command))

        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"

        elif command.startswith(TRIVIA_COMMAND):

            self.send_new_question(channel)
            return

        elif command.startswith(ANSWER_COMMAND):

            answer = self.trivia.get_trivia_answer()
            if answer:
                response = answer
            else:
                response = "Please ask another question first"

        elif command.startswith('GOTIT'):

            answer = self.trivia.get_trivia_answer()
            if answer:
                response = "Yay! You answered it correctly: {}".format(answer)
                new_question = True

        self.slack_client.api_call("chat.postMessage", channel=channel,
                                   text=response, as_user=True)

        if new_question:
            self.send_new_question(channel)

    def send_new_question(self, channel):
        q = self.trivia.get_trivia_question()
        print(q)
        print(q['answer'])
        response = "[{}] {}?".format(q['category']['title'], q['question'])

        self.slack_client.api_call("chat.postMessage", channel=channel,
                                   text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output

        current_answer = None

        if self.trivia.current:
            current_answer = self.trivia.current['answer']

        # raw
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and conf['at_bot'] in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(conf['at_bot'])[1].strip().lower(), \
                           output['channel']
                elif output and 'text' in output and current_answer and current_answer in output['text']:
                    return 'GOTIT', output['channel']

        return None, None

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None


if __name__ == "__main__":

    # instantiate Slack & Twilio clients
    slack_client = SlackClient(conf['slack_bot_token'])
    trivia = Trivia()
    tautbot = Tautbot(slack_client=slack_client, trivia=trivia)

    channels = tautbot.list_channels()

    if channels:
        print("Channels: ")
        for c in channels:
            print(c['name'] + " (" + c['id'] + ")")

    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = tautbot.parse_slack_output(slack_client.rtm_read())
            if command and channel:
                tautbot.handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
