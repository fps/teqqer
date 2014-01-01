import sys
import urwid
import teq
import pyteq

usage_text = """
Usage: teqqer [filename]

The filename argument is required so the author doesn't have to
implement file selection dialogs. The file will only be written 
when explicitly saved.

The naming convention is to use the extension .teq for teqqer files.
"""

if (len(sys.argv) != 2):
	print(usage_text)
	sys.exit()

# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song.
default_options = {
	"palette": [                 # The color palette (see urwid documentation)
		(None, "dark gray", "black"),
		("weak", "light gray", "black"),
		("strong", "light gray", "dark gray"),
		("mega", "black", "white")
	],
	
	"center_line_fraction": 0.3, # At what fraction of the screen to display the edit cursor
	"highlighted_rows": 4,       # Highlight every highlight_row'th row
	
	"cv_precision": 3,           # The number of digits used for displaying cv values
	"control_precision": 3,      # The number of digits used for displaying control values
	
	"follow_transport": True,
	
	"mouse_interaction": True,
	
	"cursor_up_key": "up",
	"cursor_down_key": "down",
	
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
		
		self.playing = False
		
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
		if self.playing == True:
			pyteq.stop(self.teq_engine)
		else:
			pyteq.start(self.teq_engine)
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
					self.cursor_tick = max(0, self.cursor_tick - 1)
					self._invalidate()
					return
				if key == self.options["cursor_down_key"]:
					self.cursor_tick = min(pattern.length() - 1, self.cursor_tick + 1)
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
	
	def render(self, size, focus):
		text = []
		attr = []
		
		header = "ar tik"
		for n in range(0, self.teq_engine.number_of_tracks()):
			header = header + " " + '{0:<7.7}'.format(self.teq_engine.track_name(n))

		header = self.fill_line(header, size[0])
		
		text.append(header)
		attr.append([('strong', len(header))])
		
		pattern = self.teq_engine.get_pattern(0)
		
		event_rows = size[1] - 2
		
		split = int(round(event_rows * self.options["center_line_fraction"]))
		
		for n in range(0, event_rows):
			displayed_tick = (self.cursor_tick + n) - split
			if displayed_tick >= 0 and displayed_tick < pattern.length():
				line = "   " + 	"%0.3x" % displayed_tick + " --- -- " * self.teq_engine.number_of_tracks()
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
teq_engine.insert_midi_track("bd2", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare2", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd3", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare3", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd4", teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare4", teq_engine.number_of_tracks())
p = teq_engine.create_pattern(64)
teq_engine.insert_pattern(0, p)


loop = urwid.MainLoop(main(teq_engine, default_options), default_options["palette"])
loop.run()