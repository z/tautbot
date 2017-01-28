import random
import re
from collections import defaultdict

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer
from tautbot.util.formatters import multi_replace


class Flip(PluginBase, Observer):
    def __init__(self, command='flip',
                 aliases=(
                     ('fix', 'fix'),
                 )):
        super(self.__class__, self).__init__(command=command, aliases=aliases)
        Observer.__init__(self)
        self.table_status = defaultdict(lambda: None)
        self.use_flippers = True
        self.replacements = {
            'a': 'ɐ',
            'b': 'q',
            'c': 'ɔ',
            'd': 'p',
            'e': 'ǝ',
            'f': 'ɟ',
            'g': 'ƃ',
            'h': 'ɥ',
            'i': 'ᴉ',
            'j': 'ɾ',
            'k': 'ʞ',
            'l': 'ן',
            'm': 'ɯ',
            'n': 'u',
            'o': 'o',
            'p': 'd',
            'q': 'b',
            'r': 'ɹ',
            's': 's',
            't': 'ʇ',
            'u': 'n',
            'v': 'ʌ',
            'w': 'ʍ',
            'x': 'x',
            'y': 'ʎ',
            'z': 'z',
            '?': '¿',
            '.': '˙',
            ',': '\'',
            '(': ')',
            '<': '>',
            '[': ']',
            '{': '}',
            '\'': ',',
            '_': '‾'}

        # append an inverted form of replacements to itself, so flipping works both ways
        self.replacements.update(dict((v, k) for k, v in self.replacements.items()))

        self.flippers = ["( ﾉ⊙︵⊙）ﾉ", "(╯°□°）╯", "( ﾉ♉︵♉ ）ﾉ"]
        self.table_flipper = "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻"

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)
        self.observe('channel_alias', self.route_event)

    def route_event(self, command, channel, text, output):
        text = text.replace(command, '').strip()
        if re.match('^flip', command):
            self.flip(channel, text)
        if re.match('^fix', command):
            self.fix(channel, text)

    def flip(self, channel, text):
        """<text> -- Flips <text> over."""
        self.table_status = defaultdict(None)

        if self.use_flippers:
            if text in ['table', 'tables']:
                response = random.choice([random.choice(self.flippers) + " ︵ " + "\u253B\u2501\u253B", self.table_flipper])
                self.table_status[channel] = True
            elif text == "5318008":
                out = "BOOBIES"
                response = random.choice(self.flippers) + " ︵ " + out
            elif text == "BOOBIES":
                out = "5318008"
                response = random.choice(self.flippers) + " ︵ " + out
            else:
                response = random.choice(self.flippers) + " ︵ " + multi_replace(text[::-1], self.replacements)
        else:
            response = multi_replace(text[::-1], self.replacements)

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)

    def fix(self, channel, text):
        """fixes a flipped over table. ┬─┬ノ(ಠ_ಠノ)"""
        response = "no tables have been turned over here, thanks for checking!"
        if text in ['table', 'tables']:
            if self.table_status[channel]:
                response = "┬─┬ノ(ಠ_ಠノ)"
                self.table_status[channel] = False
        else:
            self.flip(channel, text)

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
