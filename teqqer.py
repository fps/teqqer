import sys
import urwid
import teq
import pyteq
import math
import default_options

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

class history:
	def __init__(self):
		# A list of tuples of lambdas where the first
		# entry in each tuple is the action and the second
		# is the action with the inverse effect.
		self.actions = []
		self.last = -1
		
	def add(self, action, inverse_action):
		self.actions.append((action, inverse_action))
		self.last += 1
		action()
		
	def undo(self):
		try:
			action = self.actions.pop()[1]
			self.last -= 1
			action()
		except:
			pass
	
	def redo(self):
		pass

class main(urwid.Widget):
	def __init__(self,  teq_engine,  options):
		urwid.Widget.__init__(self)
		self.options = options
		self.teq_engine = teq_engine
		
		self._sizing = frozenset(['box'])
		
		self.cursor_pattern = 0
		self.cursor_tick = 0
		self.cursor_track = 0
		self.cursor_column = 0
		
		self.note_edit_base = self.options["note_edit_base"]
		self.note_edit_velocity = self.options["note_edit_velocity"]
		
		self.edit_step = self.options["edit_step"]
		
		self.history = history()

		self.info = None
		
		self.edit_mode = False
		
		self.root_menu = [ 
			(options["root_menu_key"],  "menu",  self.show_menu), 
			(options["root_help_key"],  "help",  self.show_help), 
			(options["root_menu_play_stop_key"],  "play/stop",  self.toggle_playback),
			(options["undo_key"], "undo", self.undo)
		]
		
		self.menu = [
			(options["menu_file_key"],  "file",  self.show_file_menu), 
			(options["menu_quit_key"],  "quit",  self.show_quit_menu), 
			(options["menu_song_key"],  "song",  self.show_song_menu)
		]
		
		self.quit_menu = [
			(options["menu_yes_key"],  "yes,  really quit",  self.quit)
		]
			
		self.current_menu = self.root_menu
	
	def undo(self):
		self.history.undo()
	
	def get_state_info_and_update(self):
		# The first time we get some info we are in the game
		if self.info == None:
			try:
				self.info = teq_engine.get_state_info()
				self._invalidate()
			except Exception as e:
				# print(e)
				pass
			
			return
		
		try:
			info = teq_engine.get_state_info()
			
			# Check if the transport position changed
			if info.transport_position.tick != self.info.transport_position.tick or info.transport_position.pattern != self.info.transport_position.pattern:
				if self.options["follow_transport"] == True:
					self.cursor_tick = info.transport_position.tick
					self.cursor_pattern = info.transport_position.pattern
				
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
		raise urwid.ExitMainLoop()
	
	def show_file_menu(self):
		pass
	
	def toggle_edit_mode(self):
		self.edit_mode = not self.edit_mode
		self._invalidate()
	
	def toggle_playback(self):
		if self.info == None:
			print(":(")
			return
		
		if self.info.transport_state == teq.transport_state.PLAYING:
			pyteq.stop(self.teq_engine)
		else:
			pyteq.set_transport_position(self.teq_engine,  self.cursor_pattern,  self.cursor_tick)
			pyteq.play(self.teq_engine)
		pass
	
	def selectable(self):
		return True
	
	def mouse_event(self,  size,  event,  button,  col,  row,  focus):
		pass
	
	def handle_menu_key(self,  key):
		for entry in self.current_menu:
			if key == entry[0]:
				entry[2]()
				self._invalidate()
				return
		
		if self.current_menu != self.root_menu and key == self.options["menu_exit_key"]:
			self.current_menu = self.root_menu
			self._invalidate()
			return
	
	def set_midi_event(self, track_index, pattern_index, tick_index, event_type, value1, value2):
		pattern = self.teq_engine.get_pattern(pattern_index)
		pattern.set_midi_event(track_index, tick_index, teq.midi_event(event_type, value1, value2))
		self.teq_engine.set_pattern(self.cursor_pattern, pattern)
		self.teq_engine.gc()
		
	
	def set_midi_event_action(self, track_index, pattern_index, tick_index, event_type, value1, value2):
		pattern = self.teq_engine.get_pattern(pattern_index)
		event = pattern.get_midi_event(track_index, tick_index)
		self.history.add(
			lambda: self.set_midi_event(track_index, pattern_index, tick_index, event_type, value1, value2), 
			lambda: self.set_midi_event(track_index, pattern_index, tick_index, event.type, event.value1, event.value2)
		)
	
	def keypress(self,  size,  key):
		if key == self.options["edit_mode_key"]:
			self.toggle_edit_mode()
			return
		
		if key == self.options["increase_edit_step_key"]:
			self.edit_step += 1
			self._invalidate()
			return

		if key == self.options["decrease_edit_step_key"]:
			self.edit_step -= 1
			self._invalidate()
			return
		
		if key == self.options["increase_octave_key"]:
			self.note_edit_base += 12
			self._invalidate()
			return

		if key == self.options["decrease_octave_key"]:
			self.note_edit_base -= 12
			self._invalidate()
			return
		
		if key == self.options["increase_velocity_key"]:
			self.note_edit_velocity += 1
			self._invalidate()
			return

		if key == self.options["decrease_velocity_key"]:
			self.note_edit_velocity -= 1
			self._invalidate()
			return

		if key == self.options["increase_tempo_key"]:
			self.teq_engine.set_global_tempo(self.teq_engine.get_global_tempo() + self.options["tempo_increment"])
			self._invalidate()
			return

		if key == self.options["decrease_tempo_key"]:
			self.teq_engine.set_global_tempo(self.teq_engine.get_global_tempo() - self.options["tempo_increment"])
			self._invalidate()
			return
		

		# If we are in the root menu we have to do some extra key
		# processing
		track_type = self.teq_engine.track_type(self.cursor_track)
		
		if track_type == teq.track_type.MIDI:
			if key == self.options["delete_event_key"]:
				if True == self.edit_mode:
					self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.NONE, 0, 127)
					self._invalidate()
					return

			if key == self.options["note_off_key"]:
				if True == self.edit_mode:
					self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.OFF, 0, 127)
					self._invalidate()
					return
				
			if key in self.options["note_keys"]:
				if True == self.edit_mode:
					self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.ON, self.note_edit_base + self.options["note_keys"][key], self.note_edit_velocity)
					self._invalidate()
					return
				
			
		if self.teq_engine.number_of_patterns  > 0:
			pattern = self.teq_engine.get_pattern(0)
		
			if key == self.options["cursor_up_key"]:
				self.cursor_tick -= 1
				if self.cursor_tick < 0:
					if self.options["cursor_wrap_mode"] == "pattern":
						self.cursor_tick = pattern.length() - 1
					if self.options["cursor_wrap_mode"] == "song":
						self.cursor_pattern -= 1
						if self.cursor_pattern < 0:
							self.cursor_pattern = self.teq_engine.number_of_patterns() - 1
						new_pattern = self.teq_engine.get_pattern(self.cursor_pattern)
						self.cursor_tick = new_pattern.length() - 1
				self._invalidate()
				return
			
			if key == self.options["cursor_down_key"]:
				self.cursor_tick += 1
				if self.cursor_tick >= pattern.length():
					if self.options["cursor_wrap_mode"] == "pattern":
						self.cursor_tick = 0
					if self.options["cursor_wrap_mode"] == "song":
						self.cursor_tick = 0
						self.cursor_pattern += 1
						if self.cursor_pattern >= self.teq_engine.number_of_patterns():
							self.cursor_pattern = 0
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
		
	def fill_line(self,  line,  n):
		return (line + " " * n)[0:n]
	
	def render_key(self,  key):
		if key == " ":
			return "space"
		else:
			return key
	
	def render_note_on(self, value1, value2):
		octave = math.floor(value1 / 12)
		note = self.options["note_names"][value1 % 12]
		return note + "%0.1x" % octave + " " + "%0.2x" % value2
	
	def render_menu(self):
		ret =  ((self.info.transport_state == teq.transport_state.PLAYING) and "PLAY" or "STOP") + " " + (self.edit_mode and "EDIT" or "    ") + " " + self.render_note_on(self.note_edit_base, self.note_edit_velocity) + " " + str(self.teq_engine.get_global_tempo()) + " " + str(self.edit_step) + " "
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
		return 4 + self.options["cv_integer_precision"] + 1 + self.options["cv_fraction_precision"]
		pass
	
	def render_midi_event(self,  event):
		if event.type == teq.midi_event_type.ON:
			return self.render_note_on(event.value1, event.value2)
		
		if event.type == teq.midi_event_type.OFF:
			return "OFF --"
		
		return "--- --"
	
	def render_cv_event(self,  event):
		return "---" + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"]
	
	def render_control_event(self,  event):
		return "---" + " " + "-" * self.options["control_integer_precision"] + "." + "-" * self.options["control_fraction_precision"]
	
	def render_name(self,  name,  maxlength):
		if len(name) > maxlength:
			return name[0:maxlength - 2] + ".."
		
		return name + " " * (maxlength - len(name))
	
	def render_pattern_line(self,  pattern,  tick):
		column_separator = self.options["column_separator"]

		line = "%0.4x" % tick
		
		for n in range(0,  self.teq_engine.number_of_tracks()):
			event = None
			
			if self.teq_engine.track_type(n) == teq.track_type.MIDI:
				event = self.render_midi_event(pattern.get_midi_event(n,  tick))
			if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
				event = self.render_control_event(pattern.get_control_event(n,  tick))
			if self.teq_engine.track_type(n) == teq.track_type.CV:
				event = self.render_cv_event(pattern.get_cv_event(n,  tick))
				
			line = line + column_separator + event
		
		return line

	def render_header(self):
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		
		text = []
		attr = []
	
		text.append("patterns")
		attr.append(("strong",  len("patterns")))
		
		text.append(column_separator)
		attr.append(("strong",  column_separator_len))
		
		text.append("tick")
		attr.append(("strong",  len("tick")))
		
		header = "patterns" + column_separator + "tick"
		
		for n in xrange(self.teq_engine.number_of_tracks()):
			text.append(column_separator)
			attr.append(("strong",  column_separator_len))
			
			render_size = None
			
			if self.teq_engine.track_type(n) == teq.track_type.MIDI:
				render_size = self.midi_track_render_size()
			if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
				render_size = self.control_track_render_size()
			if self.teq_engine.track_type(n) == teq.track_type.CV:
				render_size = self.cv_track_render_size()
			
			track_name = self.teq_engine.track_name(n)

			text.append(self.render_name(track_name,  render_size))
			if self.cursor_track == n:
				attr.append(("stronger",  render_size))
			else:
				attr.append(("strong",  render_size))

		return (''.join(text),  attr)
	
	def render_pattern_view(self):
		pattern = self.teq_engine.get_pattern(self.cursor_pattern)
		
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		
		text = []
		attr =[]
		
		for tick_index in xrange(pattern.length()):
			events = []
			event_attrs = []
			for track_index in xrange(self.teq_engine.number_of_tracks()):
				event = None
				
				if self.teq_engine.track_type(n) == teq.track_type.MIDI:
					event = self.render_midi_event(pattern.get_midi_event(track_index,  tick_index))
				if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
					event = self.render_control_event(pattern.get_control_event(track_index,  tick_index))
				if self.teq_engine.track_type(n) == teq.track_type.CV:
					event = self.render_cv_event(pattern.get_cv_event(track_index,  tick_index))
				
				events.append(column_separator)
				events.append(event)
				
				if self.cursor_tick == tick_index:
					event_attrs.append(("strong",  column_separator_len))
					if self.cursor_track == track_index:
						event_attrs.append(("mega",  len(event)))
					else:
						event_attrs.append(("strong",  len(event)))
				else:
					event_attrs.append(("strong",  column_separator_len))
					event_attrs.append((None,  len(event)))
			
			text.append(''.join(events))
			attr.append(event_attrs)
			
		return (text,  attr)
	
	def render(self,  size,  focus):
		if self.info == None:
			text = [" " * size[0]] * size[1]
			t = urwid.TextCanvas(text) 

			return t

			
		text = []
		attr = []
		
		column_separator = self.options["column_separator"]
		
		header = self.render_header()
		
		header_text = header[0]
		header_attr = header[1]
		
		# Find out how much space to fill after the header
		remainder_len = size[0] - len(header_text)
	
		if remainder_len > 0:
			# And fill it
			header_text += " " * (remainder_len)
			header_attr.append(("strong", remainder_len))
		
		text.append(header_text)
		attr.append(header_attr)
		
		pattern = self.teq_engine.get_pattern(self.cursor_pattern)
		
		event_rows = size[1] - 2
		
		split = int(round(event_rows * self.options["center_line_fraction"]))
		
		for n in range(0,  event_rows):
			displayed_tick = (self.cursor_tick + n) - split
			displayed_pattern = (self.cursor_pattern + n) - split

			# Initialize with an empty line and attributes
			line = ""
			line_attr = []
			
			pattern_line = " " * len("patterns")
			pattern_line_attr = (None,  len(pattern_line))
			
			if displayed_pattern >= 0 and displayed_pattern < self.teq_engine.number_of_patterns():
				pattern_name = self.teq_engine.get_pattern(displayed_pattern).name
				if pattern_name == "":
					pattern_name = "." * 3
				pattern_line = self.render_name(pattern_name,  8)
				if displayed_pattern == self.cursor_pattern:
					pattern_line_attr = ("strong",  len(pattern_line))

			line = line + pattern_line
			line_attr.append(pattern_line_attr)
			
			line = line + column_separator
			if displayed_pattern == self.cursor_pattern:
				line_attr.append(("strong",  len(column_separator)))
			else:
				line_attr.append((None,  len(column_separator)))
			
			if displayed_tick >= 0 and displayed_tick < pattern.length():
				pattern_line = self.render_pattern_line(pattern,  displayed_tick)
				pattern_line_attr = (None,  len(pattern_line))
				if displayed_tick % self.options["highlighted_rows"] == 0:
					pattern_line_attr = ("weak",  len(pattern_line))
				if displayed_tick == self.cursor_tick:
					pattern_line_attr = ("strong",  len(pattern_line))
				line = line + pattern_line
				line_attr.append(pattern_line_attr)

			if len(line) < size[0]:
				remainder_line = " " * (size[0] - len(line))
				remainder_attr = (None,  size[0] - len(line))
				
				line = line + remainder_line
				line_attr.append(remainder_attr)
			
			text.append(line)
			attr.append(line_attr)
		
		menu = self.fill_line(self.render_menu(),  size[0])
		text.append(menu)
		
		if self.edit_mode == True:
			attr.append([("editing", len(menu))])
		else:
			attr.append([("strong",  len(menu))])
		
		t = urwid.TextCanvas(text,  attr,  maxcol = size[0]) 

		return t

teq_engine = teq.teq()
teq_engine.insert_midi_track("bd",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare",  teq_engine.number_of_tracks())
teq_engine.insert_control_track("control",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd2",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare2",  teq_engine.number_of_tracks())
teq_engine.insert_cv_track("cv",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd3",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare3",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("bd4",  teq_engine.number_of_tracks())
teq_engine.insert_midi_track("snare4",  teq_engine.number_of_tracks())

p = teq_engine.create_pattern(32)
p.name = "intro"
p.set_midi_event(0,  0,  teq.midi_event(teq.midi_event_type.ON,  63,  127))
p.set_midi_event(0,  4,  teq.midi_event(teq.midi_event_type.OFF,  60,  127))
teq_engine.insert_pattern(0,  p)

p = teq_engine.create_pattern(32)
p.set_midi_event(0,  0,  teq.midi_event(teq.midi_event_type.ON,  60,  127))
p.set_midi_event(0,  4,  teq.midi_event(teq.midi_event_type.OFF,  62,  127))
teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

p = teq_engine.create_pattern(32)
p.name = "something"
p.set_midi_event(0,  0,  teq.midi_event(teq.midi_event_type.ON,  60,  127))
p.set_midi_event(0,  4,  teq.midi_event(teq.midi_event_type.OFF,  62,  127))
teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

teq_engine.set_global_tempo(16)
pyteq.set_transport_position(teq_engine,  0,  0)
pyteq.set_loop_range(teq_engine,  0,  0,  2,  0,  True)

# TODO: merge in user options
options = default_options.options

def handle_alarm(main_loop,  the_main):
	#print("alarm")
	the_main.get_state_info_and_update()
	main_loop.set_alarm_in(the_main.options["ui_update_interval"],  handle_alarm,  the_main)

the_main = main(teq_engine,  options)

loop = urwid.MainLoop(the_main,  options["palette"])

loop.set_alarm_in(the_main.options["ui_update_interval"],  handle_alarm,  the_main)

print("Starting up...")
loop.run()
