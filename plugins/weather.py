import pyowm
import re

from tautbot.client.slack import slack_client
from tautbot.plugin import PluginBase
from tautbot.util.events import Observer


class Weather(PluginBase, Observer):
    def __init__(self, command='weather'):
        super(self.__class__, self).__init__(command=command)
        Observer.__init__(self)

    def events(self, *args, **kwargs):
        self.observe('channel_command', self.route_event)

    def route_event(self, command, channel, text, output):
        if re.match('^weather', command):
            text = text.replace(command, '').strip()
            self.weather(channel, text)

    def weather(self, channel, text):

        owm = pyowm.OWM(self.conf['weather_api_key'])
        observation = owm.weather_at_place(text)
        l = observation.get_location()
        w = observation.get_weather()
        temp = w.get_temperature('fahrenheit')
        wind = w.get_wind()

        response = "Weather for {} is {}{}. {}. Wind: {}. Humidity: {}".format(l.get_name(), temp['temp'], "F", w.get_detailed_status(), wind['speed'], w.get_humidity())

        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
