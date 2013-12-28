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

teq_engine = teq.teq()
teq_engine.insert_midi_track("bd", 0)
teq_engine.insert_midi_track("snare", 0)
teq_engine.insert_midi_track("bd2", 0)
teq_engine.insert_midi_track("snare2", 0)
teq_engine.insert_midi_track("bd3", 0)
teq_engine.insert_midi_track("snare3", 0)
teq_engine.insert_midi_track("bd4", 0)
teq_engine.insert_midi_track("snare4", 0)
p = teq_engine.create_pattern(64)
teq_engine.insert_pattern(0, p)

# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song.
options = {
	"center_line_fraction": 0.3, # At what fraction of the screen to display the edit cursor
	"highlighted_rows": 4,       # Highlight every highlight_row'th row
	"palette": [                 # The color palette (see urwid documentation)
		(None, "dark gray", "black"),
		("weak", "light gray", "black"),
		("strong", "light gray", "dark gray"),
		("mega", "black", "white")
	],
	"cv_precision": 3,           # The number of digits used for displaying cv values
	"control_precision": 3       # The number of digits used for displaying control values
}

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
		
	def fill_line(self, line, n):
		return (line + " " * n)[0:n]
	
	def render(self, size, focus):
		pattern = teq_engine.get_pattern(0)
		
		text = []
		attr = []
		
		header = "ar tik"
		for n in range(0, teq_engine.number_of_tracks()):
			header = header + " " + '{0:<7.7}'.format(teq_engine.track_name(n))

		header = self.fill_line(header, size[0])
		
		text.append(header)
		attr.append([('strong', len(header))])
		
		event_rows = size[1] - 2
		
		split = int(round(event_rows * options["center_line_fraction"]))
		
		for n in range(0, event_rows):
			displayed_tick = (self.cursor_tick + n) - split
			if displayed_tick >= 0 and displayed_tick < pattern.length():
				line = "   " + 	"%0.3x" % displayed_tick + " --- -- " * teq_engine.number_of_tracks()
				line = self.fill_line(line, size[0])
				line_attr = [(None, len(line))]
				if displayed_tick % options["highlighted_rows"] == 0:
					line_attr = [("weak", len(line))]
				if displayed_tick == self.cursor_tick:
					line_attr = [("strong", len(line))]
				text.append(line)
				attr.append(line_attr)
			else:
				text.append("")
				attr.append([(None, len(""))])
				
		
		menu = self.fill_line("esc: menu>  f1: help  space: play", size[0])
		text.append(menu)
		attr.append([("strong", len(menu))])
		
		t = urwid.TextCanvas(text, attr, maxcol = size[0]) 
		return t

loop = urwid.MainLoop(ui(), options["palette"])
loop.run()