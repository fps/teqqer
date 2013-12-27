import sys

if (len(sys.argv) > 2):
	print("Usage: teqqer [filename]")
	sys.exit()

if (len(sys.argv) == 2):
	filename = sys.argv[1]
else:
	filename = "new.teq"

import urwid
import teq

#import carla_backend

#carla_host = carla_backend.Host("/usr/local/lib/carla/libcarla_standalone.so")
#print (carla_host.get_engine_driver_count())

teq_engine = teq.teq()
teq_engine.insert_midi_track("bd", 0)
teq_engine.insert_midi_track("snare", 0)
p = teq_engine.create_pattern(16)
teq_engine.insert_pattern(0, p)

class ui(urwid.Widget):
	def __init__(self):
		 self._sizing = frozenset(['box'])
		 
	def render(self, size, focus):
		pass

#header_prefix_text = u"ar tk"
#header_text = ""
#for n in range(0, teq_engine.number_of_tracks()):
#	print(teq_engine.track_name(n))
#	header_text = header_text + " " + teq_engine.track_name(n) 

#print(header_text)

#header = urwid.Text(header_prefix_text + header_text)
#body = urwid.Filler(urwid.Text(u"00 00 c-4"), 'top')
#footer = urwid.Text(u"ESC menu F1 help")

#frame = urwid.Frame(body, header, footer)

the_ui = ui()

loop = urwid.MainLoop(the_ui)
loop.run()