from tautbot.plugin import plugin_registry
import re

plugin_registry.register_plugin_list(['Trivia', 'Hello'])

# print(plugin_registry.plugins)
# print(plugin_registry.commands)
# print(plugin_registry.patterns)
# print([p[0] for p in plugin_registry.patterns])


command = "ni!"

patterns = '(?:({}))'.format('|'.join([p[0] for p in plugin_registry.patterns]))
print(patterns)
_matches = re.match(patterns, command)

if _matches:
    print('we here')
    print(_matches.group(0))
    print(_matches.group(1))

_pattern = _matches.group(0)

for pat in plugin_registry.patterns:
    if pat[0] == _pattern:
        print('1---1')
        print(pat[1])
        print('1---1')


# trivia = plugin_registry.commands[0]['trivia']()
# print(trivia.subcommands)
# print(trivia.aliases)

# print(trivia.get_trivia_question())
# print(trivia.get_trivia_answer())

from tautbot.events import Event
from tautbot.events import Observer

from tautbot.plugins.hello import Hello

hello = Hello()

print('---')
instance = plugin_registry.instances['Hello']
#instance.observe('channel_pattern_matched', instance.route_message)

Event('channel_pattern_matched', _pattern, 'fake', 'ni!', 'ni!')
#Event('channel_pattern_matched', _pattern, 'fake', 'ni!', 'ni!')

#
#
# class Room(Observer):
#     def __init__(self):
#         print("Room is ready.")
#         Observer.__init__(self) # DON'T FORGET THIS
#     def someone_arrived(self, who):
#         print(who + " has arrived!")
#     def someone_farted(self, who):
#         print(who + " has farted!")
#
# # Observe for specific event
# room = Room()
# room.observe('someone arrived',  room.someone_arrived)
# room.observe('someone Farted',  room.someone_farted)
#
# # Fire some events
# Event('someone left',    'John')
# Event('someone arrived', 'Lenard')  # will output "Lenard has arrived!"
# Event('someone Farted',  'Andy')

