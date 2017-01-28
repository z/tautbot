import random
import re

from tautbot.client.slack import slack_client
from tautbot.client.slack import slack_helpers
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Fight(PluginBase, Observer):
    def __init__(self, command='fight'):
        super(self.__class__, self).__init__(command=command)
        super().__init__()
        Observer.__init__(self)
        self.bang = ["BANG", "POW", "SLAM", "WHACK", "SLAP", "KAPOW", "ZAM", "BOOM"]
        self.blow_type = ["devastating", "destructive", "ruthless", "damaging", "ruinous", "catastrophic", "traumatic", "shattering", "overwhelming", "crushing", "fierce", "deadly", "lethal", "fatal", "savage", "violent"]
        self.victory = ["wins", "stands victorious", "triumphs", "conquers", "is the champion", "is the victor" ]
        self.blow = ["uppercut", "hammerfist", "elbow strike", "shoulder strike", "front kick", "side kick", "roundhouse kick", "knee strike", "butt strike", "headbutt", "haymaker punch", "palm strike", "pocket bees"]

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        text = text.replace(command, '').strip()
        if re.match('^fight$', command):
            self.fight(channel, text, output['user'])

    def fight(self, channel, text, user_id):
        """<nick>, makes you fight <nick> and generates a winner."""

        fighter1 = slack_helpers.get_user(user_id)
        dirty = text.strip()
        fighter2 = re.sub('[^0-9a-zA-Z_-]+', '', dirty)
        if random.random() < .5:
            response = "{}! {}! {}! {} {} over {} with a {} {}.".format(random.choice(self.bang), random.choice(self.bang), random.choice(self.bang), fighter1, random.choice(self.victory), fighter2, random.choice(self.blow_type), random.choice(self.blow))
        else:
            response = "{}! {}! {}! {} {} over {} with a {} {}.".format(random.choice(self.bang), random.choice(self.bang), random.choice(self.bang), fighter2, random.choice(self.victory), fighter1, random.choice(self.blow_type), random.choice(self.blow))

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
