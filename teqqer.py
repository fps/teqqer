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
p = teq_engine.create_pattern(32)
teq_engine.insert_pattern(0, p)


class ui(urwid.Widget):
	def __init__(self):
		urwid.Widget.__init__(self)
		self._sizing = frozenset(['box'])
		self.cursor_tick = 0
		self.cursor_track = 0
		self.cursor_column = 0
		self.center_line_fraction = 0.3
		self.highlighted_rows = 4
	
	def selectable(self):
		return True
	
	def keypress(self, size, key):
		pattern = teq_engine.get_pattern(0)
		if key == "up":
			self.cursor_tick = max(0, self.cursor_tick - 1)
		if key == "down":
			self.cursor_tick = min(pattern.length(), self.cursor_tick + 1)

		self._invalidate()
		
	def render(self, size, focus):
		pattern = teq_engine.get_pattern(0)
		
		text = []
		attr = []
		
		header = "ar tik"
		for n in range(0, teq_engine.number_of_tracks()):
			header = header + " " + '{0:<7.7}'.format(teq_engine.track_name(n))

		text.append(header)
		attr.append([('strong', len(header))])
		
		event_rows = size[1] - 2
		
		split = int(round(event_rows * self.center_line_fraction))
		for n in range(0, event_rows):
			displayed_tick = (self.cursor_tick + n) - split
			if displayed_tick >= 0 and displayed_tick < pattern.length():
				line = "   " + 	"%0.3x" % displayed_tick + " --- -- " * teq_engine.number_of_tracks()
				line_attr = [(None, len(line))]
				if displayed_tick % self.highlighted_rows == 0:
					line_attr = [("weak", len(line))]
				if displayed_tick == self.cursor_tick:
					line_attr = [("strong", len(line))]
				text.append(line)
				attr.append(line_attr)
			else:
				text.append("")
				attr.append([(None, len(""))])
				
		
		menu = "esc: menu>  f1: help  space: play"
		text.append(menu)
		attr.append([("strong", len(menu))])
		
		t = urwid.TextCanvas(text, attr, maxcol = size[0]) 
		return t

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

palette = [
	(None, "dark gray", "black"),
	("weak", "light gray", "black"),
	("strong", "light gray", "dark gray"),
	("mega", "black", "white")
]

loop = urwid.MainLoop(the_ui, palette)
loop.run()