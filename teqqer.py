import sys
import urwid
import teq
import pyteq
import math

usage_text = """
Usage: teqqer [filename]

The filename argument is required so the author doesn't have to
implement file selection dialogs. The file will only be written 
when explicitly saved.

A naming convention is to use the extension .teq for teqqer files.
"""

if (len(sys.argv) != 2):
	print(usage_text)
	sys.exit()

# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song [not implemented yet]
default_options = {
	# The color palette (see urwid documentation)
	"palette": [                 
		(None, "dark gray", "black"),
		("weak", "light gray", "black"),
		("strong", "light gray", "dark gray"),
		("mega", "black", "white")
	],
	
	# At what fraction of the screen to display the edit cursor
	"center_line_fraction": 0.3, 
	
	# Highlight every highlight_row'th row
	"highlighted_rows": 4,
	
	# The number of digits used for displaying cv values (integer and fractional part)
	"cv_fraction_precision": 3,
	"cv_integer_precision": 1,
	
	# The number of digits used for displaying control values (integer and fractional part)
	"control_fraction_precision": 3,
	"control_integer_precision": 1,
	
	"column_separator": "  ",
	
	"follow_transport": True,
	
	"mouse_interaction": True,
	
	"ui_update_interval": 0.01,
	
	"cursor_up_key": "up",
	"cursor_down_key": "down",
	"cursor_right_key": "right",
	"cursor_left_key": "left",
	
	"menu_exit_key": "esc",
	
	"menu_yes_key": "y",
	
	"root_menu_key": "esc",
	"root_help_key": "f1",
	"root_menu_play_stop_key": " ",
	
	"menu_file_key": "f",
	"menu_quit_key": "q",
	"menu_song_key": "s",
	
	"menu_file_save_key": "s",
	
	"menu_song_add_midi_track_key": "m",
	"menu_song_add_control_track_key": "c",
	"menu_song_add_cv_track_key": "v"
}

class main(urwid.Widget):
	def __init__(self, teq_engine, options):
		urwid.Widget.__init__(self)
		self.options = options
		self.teq_engine = teq_engine
		
		self._sizing = frozenset(['box'])
		
		self.cursort_pattern = 0
		self.cursor_tick = 0
		self.cursor_track = 0
		self.cursor_column = 0
		self.center_line_fraction = 0.3
		self.highlighted_rows = 4

		self.info = None
		
		self.root_menu = [ 
			(options["root_menu_key"], "menu", self.show_menu),
			(options["root_help_key"], "help", self.show_help),
			(options["root_menu_play_stop_key"], "play/stop", self.toggle_playback)
		]
		
		self.menu = [
			(options["menu_file_key"], "file", self.show_file_menu),
			(options["menu_quit_key"], "quit", self.show_quit_menu),
			(options["menu_song_key"], "song", self.show_song_menu)
		]
		
		self.quit_menu = [
			(options["menu_yes_key"], "yes, really quit", self.quit)
		]
			
		self.current_menu = self.root_menu
	
	def get_state_info_and_update(self):
		if self.info == None:
			try:
				self.info = teq_engine.get_state_info()
			except:
				pass
		else:
			try:
				info = teq_engine.get_state_info()
				
				if info.transport_position.tick != self.info.transport_position.tick:
					self.cursor_tick = info.transport_position.tick
					self._invalidate()
				
				self.info = info
			except:
				pass
	
	def show_help(self):
		pass
	
	def show_root_menu(self):
		self.current_menu = self.root_menu
	
	def show_menu(self):
		self.current_menu = self.menu
	
	def show_quit_menu(self):
		self.current_menu = self.quit_menu

	def show_song_menu(self):
		pass
	
	def quit(self):
		sys.exit(0)
	
	def show_file_menu(self):
		pass
	
	def toggle_playback(self):
		if self.info == None:
			return
		
		if self.info.transport_state == teq.transport_state.PLAYING:
			pyteq.stop(self.teq_engine)
		else:
			pyteq.play(self.teq_engine)
		pass
	
	def selectable(self):
		return True
	
	def mouse_event(self, size, event, button, col, row, focus):
		pass
	
	def handle_menu_key(self, key):
		for entry in self.current_menu:
			if key == entry[0]:
				entry[2]()
				self._invalidate()
				return
		
		if self.current_menu != self.root_menu and key == self.options["menu_exit_key"]:
			self.current_menu = self.root_menu
			self._invalidate()
			return
	
	def keypress(self, size, key):
		# If we are in the root menu we have to do some extra key
		# processing
		if (self.current_menu == self.root_menu):
			if self.teq_engine.number_of_patterns  > 0:
				pattern = self.teq_engine.get_pattern(0)
			
				if key == self.options["cursor_up_key"]:
					self.cursor_tick = (self.cursor_tick - 1) % pattern.length()
					self._invalidate()
					return
				if key == self.options["cursor_down_key"]:
					self.cursor_tick = (self.cursor_tick + 1) % pattern.length()
					self._invalidate()
					return
				if key == self.options["cursor_left_key"]:
					self.cursor_track = (self.cursor_track - 1) % self.teq_engine.number_of_tracks()
					self._invalidate()
					return
				if key == self.options["cursor_right_key"]:
					self.cursor_track = (self.cursor_track + 1) % self.teq_engine.number_of_tracks() 
					self._invalidate()
					return
			
				
		self.handle_menu_key(key)
		
	def fill_line(self, line, n):
		return (line + " " * n)[0:n]
	
	def render_key(self, key):
		if key == " ":
			return "space"
		else:
			return key
	
	def render_menu(self):
		ret = ""
		if self.current_menu != self.root_menu:
			ret = ret + self.options["menu_exit_key"] + ":exit menu "
		for item in self.current_menu:
			ret = ret + self.render_key(item[0]) + ":" + item[1] + " "
		return ret
	
	def midi_track_render_size(self):
		return 6
	
	def control_track_render_size(self):
		return 4 + self.options["control_integer_precision"] + 1 + self.options["control_fraction_precision"]
	
	def cv_track_render_size(self):
		return 4 + self.options["control_integer_precision"] + 1 + self.options["control_fraction_precision"]
		pass
	
	def render_midi_event(self, event):
		if event.type == teq.midi_event_type.ON:
			octave = math.floor(event.value1 / 12)
			note = ["C ", "Db", "E ", "F ", "Gb", "G ", "Ab", "A ", "Bb", "B "][event.value1 % 12]
			return note + "%0.1x" % octave + " " + "%0.2x" % event.value2
		
		if event.type == teq.midi_event_type.OFF:
			return "OFF --"
		
		return "--- --"
	
	def render_cv_event(self, event):
		return "---" + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"]
	
	def render_control_event(self, event):
		return "---" + " " + "-" * self.options["control_integer_precision"] + "." + "-" * self.options["control_fraction_precision"]
	
	def render_track_name(self, name, maxlength):
		if len(name) > maxlength:
			return name[0:maxlength - 2] + ".."
		
		return name + " " * (maxlength - len(name))
	
	def render_pattern_line(self, pattern, tick):
		column_separator = self.options["column_separator"]

		line = "    " + "%0.3x" % tick
		
		for n in range(0, self.teq_engine.number_of_tracks()):
			event = None
			
			if self.teq_engine.track_type(n) == teq.track_type.MIDI:
				event = self.render_midi_event(pattern.get_midi_event(n, tick))
			if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
				event = self.render_control_event(pattern.get_control_event(n, tick))
			if self.teq_engine.track_type(n) == teq.track_type.CV:
				event = self.render_cv_event(pattern.get_cv_event(n, tick))
				
			line = line + column_separator + event
		
		return line

	
	def render(self, size, focus):
		text = []
		attr = []
		
		column_separator = self.options["column_separator"]
		
		header = "ar" + column_separator + "tik"
		
		for n in range(0, self.teq_engine.number_of_tracks()):
			track_name = self.teq_engine.track_name(n)
			render_size = None
			
			if self.teq_engine.track_type(n) == teq.track_type.MIDI:
				render_size = self.midi_track_render_size()
			if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
				render_size = self.control_track_render_size()
			if self.teq_engine.track_type(n) == teq.track_type.CV:
				render_size = self.cv_track_render_size()
				
			header = header + column_separator + self.render_track_name(track_name, render_size)

		header = self.fill_line(header, size[0])
		
		text.append(header)
		attr.append([('strong', len(header))])
		
		pattern = self.teq_engine.get_pattern(0)
		
		event_rows = size[1] - 2
		
		split = int(round(event_rows * self.options["center_line_fraction"]))
		
		for n in range(0, event_rows):
			# Note: This might be negative
			displayed_tick = (self.cursor_tick + n) - split
			if displayed_tick >= 0 and displayed_tick < pattern.length():
				#line = "    " + "%0.3x" % displayed_tick + column_separator + "--- --"
				line = self.render_pattern_line(pattern, displayed_tick)
				line = self.fill_line(line, size[0])
				line_attr = [(None, len(line))]
				if displayed_tick % self.options["highlighted_rows"] == 0:
					line_attr = [("weak", len(line))]
				if displayed_tick == self.cursor_tick:
					line_attr = [("strong", len(line))]
				text.append(line)
				attr.append(line_attr)
			else:
				text.append("")
				attr.append([(None, len(""))])
		
		menu = self.fill_line(self.render_menu(), size[0])
		text.append(menu)
		if self.current_menu != self.root_menu:
			attr.append([("mega", len(menu))])
		else:
			attr.append([("strong", len(menu))])
		
		t = urwid.TextCanvas(text, attr, maxcol = size[0]) 

		return t

teq_engine = teq.teq()
teq_engine.insert_midi_track("bd", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare", teq_engine.number_of_tracks())
teq_engine.insert_control_track("control", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd2", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare2", teq_engine.number_of_tracks())
teq_engine.insert_cv_track("cv", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd3", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare3", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd4", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare4", teq_engine.number_of_tracks())
p = teq_engine.create_pattern(64)
p.set_midi_event(0, 0, teq.midi_event(teq.midi_event_type.ON, 64, 127))
p.set_midi_event(0, 4, teq.midi_event(teq.midi_event_type.OFF, 64, 127))
teq_engine.insert_pattern(0, p)
teq_engine.set_global_tempo(16)
pyteq.set_loop_range(teq_engine, 0, 0, 1, 0, True)

# TODO: merge in user options
options = default_options

def handle_alarm(main_loop, the_main):
	the_main.get_state_info_and_update()
	main_loop.set_alarm_in(the_main.options["ui_update_interval"], handle_alarm, the_main)

the_main = main(teq_engine, options)

loop = urwid.MainLoop(the_main, options["palette"])

loop.set_alarm_in(the_main.options["ui_update_interval"], handle_alarm, the_main)

loop.run()