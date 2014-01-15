import sys
import urwid
import math
import random
import json

import teq
import pyteq

import default_options
import about
import license
import the_help

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
		if self.last > -1:
			self.actions = self.actions[0:self.last+1]
		
		self.actions.append((action, inverse_action))
		self.last += 1
		
		action()
		
	def undo(self):
		if self.last > -1:
			self.actions[self.last][1]()
			self.last -= 1
	
	def redo(self):
		if self.last + 1 < len(self.actions):
			self.actions[self.last + 1][0]()
			self.last += 1

class TextPopup(urwid.WidgetWrap):
	def __init__(self, text):
		text = urwid.Text(text)
		help_list_box = urwid.ListBox(urwid.SimpleListWalker([text]))

		self.__super.__init__(help_list_box)
		
		urwid.register_signal(TextPopup, 'close')

	
	def keypress(self, size, key):
		if key == 'esc':
			self._emit('close')
			return
		
		self._w.keypress(size, key)
		
class PopUpLauncherThing(urwid.PopUpLauncher):
	def __init__(self, original):
		self.__super.__init__(original)
		
		self.the_original = original
		
		urwid.connect_signal(original, 'popup_about', lambda x: self.popup_about())
		urwid.connect_signal(original, 'popup_license', lambda x: self.popup_license())
		urwid.connect_signal(original, 'popup_help', lambda x: self.popup_help())

	def popup_license(self):
		self.popup_widget = TextPopup(("medium", license.text))
		
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		
		self.open_pop_up()

	def popup_help(self):
		self.popup_widget = TextPopup(("medium", the_help.get_help_text(self.the_original.options)))
		
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		
		self.open_pop_up()

	def popup_about(self):
		self.popup_widget = TextPopup(("medium", about.text))
		
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		
		self.open_pop_up()

	def get_pop_up_parameters(self):
		return self.popup_parameters
	
	def create_pop_up(self):
		return self.popup_widget
	

class main(urwid.Widget):
	def __init__(self,  teq_engine,  options):
		self.__super.__init__()
				
		urwid.register_signal(main, ['popup_about', 'popup_license', 'popup_help'])
		
		self.options = options
		self.teq_engine = teq_engine
		
		self._sizing = frozenset(['box'])
		
		self.cursor_pattern = 0
		self.cursor_tick = 0
		self.cursor_track = 0
		self.cursor_column = 0
		
		self.history = history()

		self.info = None
		
		self.edit_mode = False
		
		self.current_menu = self.options["menu"]
		for menu in self.current_menu:
			self.fixup_menu(menu)
			
	def show_about(self):
		self._emit('popup_about')
	
	def fixup_menu(self, menu):
		# print ("fixing up", menu)
		if 0 == len(menu[3]):
			l = menu[2]
			menu[2] = lambda x: l(x) or x.exit_menu()
			return
		
		for submenu in menu[3]:
			self.fixup_menu(submenu)

		menu[3].append(["root", "x", lambda x: x.exit_menu(), []])
		
	
	def change_menu(self, menu):
		self.current_menu = menu
	
	def exit_menu(self):
		self.current_menu = self.options["menu"]
	
	def undo(self):
		self.history.undo()
	
	def redo(self):
		self.history.redo()
	
	def state_changed(self, old_info, new_info):
		if not old_info.transport_position.tick == new_info.transport_position.tick:
			return True
		if not old_info.transport_position.pattern == new_info.transport_position.pattern:
			return True
		if not old_info.transport_state == self.info.transport_state:
			return True
		
	def get_state_info_and_update(self):
		old_info = self.info
		
		try:
			while True:
				self.info = teq_engine.get_state_info()
		except Exception as e:
			pass
		
		if self.info == None:
			
			self._invalidate()
			return
		
		if old_info == None and self.info != None:
			self._invalidate()
		
		# Check if the transport position changed
		if old_info and self.info:
			if self.state_changed(old_info, self.info):
				if self.options["follow_transport"] == True:
					self.cursor_tick = self.info.transport_position.tick
					self.cursor_pattern = self.info.transport_position.pattern
				
				self._invalidate()
	
	def change_tempo(self, amount):
		self.teq_engine.set_global_tempo(self.teq_engine.get_global_tempo() + amount)
	
	def change_note_edit_base(self, amount):
		self.options["note_edit_base"] += amount
	
	def change_note_velocity(self, amount):
		self.options["note_edit_velocity"] += amount
	
	def change_edit_step(self, amount):
		self.options["edit_step"] += amount
	
	# Only the sign of amount is important
	def change_cursor_tick_by_one(self, amount):
		if 0 == amount:
			return
		
		if amount > 0:
			self.cursor_tick += 1
		else:
			self.cursor_tick -= 1
		
		pattern = self.teq_engine.get_pattern(self.cursor_pattern)
		
		if self.cursor_tick < 0:
			if self.options["cursor_wrap_mode"] == "pattern":
				self.cursor_tick = pattern.length() - 1
			if self.options["cursor_wrap_mode"] == "song":
				self.cursor_pattern -= 1
				if self.cursor_pattern < 0:
					self.cursor_pattern = self.teq_engine.number_of_patterns() - 1
				new_pattern = self.teq_engine.get_pattern(self.cursor_pattern)
				self.cursor_tick = new_pattern.length() - 1
				
		if self.cursor_tick >= pattern.length():
			if self.options["cursor_wrap_mode"] == "pattern":
				self.cursor_tick = 0
			if self.options["cursor_wrap_mode"] == "song":
				self.cursor_tick = 0
				self.cursor_pattern += 1
				if self.cursor_pattern >= self.teq_engine.number_of_patterns():
					self.cursor_pattern = 0
	
	def change_cursor_tick(self, amount):
		for n in xrange(abs(amount)):
			self.change_cursor_tick_by_one(amount)
		
	
	def change_cursor_track(self, amount):
		self.cursor_track += amount
		self.cursor_track = self.cursor_track % self.teq_engine.number_of_tracks()
	
	def change_cursor_pattern(self, amount):
		pass

	def move_to_pattern_top(self):
		self.cursor_tick = 0
		
	def move_to_pattern_end(self):
		pattern = self.teq_engine.get_pattern(self.cursor_pattern)
		self.cursor_tick = pattern.length() - 1
	
	def delete_event(self):
		if False == self.edit_mode:
			return

		self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.NONE, 0, 127)
		self._invalidate()
		return	
		
	def show_help(self):
		pass
	
	def quit(self):
		raise urwid.ExitMainLoop()
	
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
		
		self._invalidate()
	
	def selectable(self):
		return True
	
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
	
	def mouse_event(self,  size,  event,  button,  col,  row,  focus):
		if self.teq_engine.number_of_patterns() == 0:
			return 
		
		for entry in self.options["global_mouse_events"]:
			if entry[0][0] == event and entry[0][1] == button:
				entry[2](self)
				self._invalidate()
				return True
	
	def keypress(self,  size,  key):
		# The menu MUST be processed first. This way even
		# submenu entries without modifiers get priority.
		for entry in self.current_menu:
			if entry[1] ==  key:
				entry[2](self)
				
				self._invalidate()
				return
		
		if self.teq_engine.number_of_patterns() == 0:
			return 
		

		for k in self.options["global_keys"]:
			if k[0] == key:
				k[2](self)
				self._invalidate()
				return
			
		if self.teq_engine.track_type(self.cursor_track) == teq.track_type.MIDI:
			for k in self.options["midi_track_keys"]:
				if k[0] == key:
					k[2](self)
					self._invalidate()
					return
			
			

		# If we are in the root menu we have to do some extra key
		# processing
		track_type = self.teq_engine.track_type(self.cursor_track)
		
		if track_type == teq.track_type.MIDI:
			if key == self.options["note_off_key"]:
				if True == self.edit_mode:
					self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.OFF, 0, 127)
					self._invalidate()
					return
				
			for k in self.options["note_keys"]:
				if k[0] == key and True == self.edit_mode:
					self.set_midi_event_action(self.cursor_track, self.cursor_pattern, self.cursor_tick, teq.midi_event_type.ON, self.options["note_edit_base"] + k[1], self.options["note_edit_velocity"])
					self.change_cursor_tick(self.options["edit_step"])
					self._invalidate()
					return
	
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
	
	def render_menu(self, default_style):
		text = []
		attr = []
		
		for n in xrange(len(self.current_menu)):
			entry = self.current_menu[n]
			text.append(self.render_key(entry[1]) + ":" + entry[0])
			attr.append(("menu-entry-default", len(text[-1])))
			if n < len(self.current_menu):
				text.append(" ")
				attr.append((default_style, 1))

		return ("".join(text), attr)

	

	def midi_track_render_size(self):
		return 6
	
	def control_track_render_size(self):
		return 2 + self.options["control_integer_precision"] + 1 + self.options["control_fraction_precision"]
	
	def cv_track_render_size(self):
		return 2 + self.options["cv_integer_precision"] + 1 + self.options["cv_fraction_precision"]
		pass
	
	def render_midi_event(self,  event):
		if event.type == teq.midi_event_type.ON:
			return self.render_note_on(event.value1, event.value2)
		
		if event.type == teq.midi_event_type.OFF:
			return "OFF --"
		
		if event.type == teq.midi_event_type.CC:
			return "%0.2x" % event.value1 + "  " + "%0.2x" % event.value2
		
		return "--- --"
	
	def render_cv_event(self,  event):
		return "-" + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"]
	
	def render_control_event(self,  event):
		if event.type == teq.control_event_type.GLOBAL_TEMPO:
			return "G" + " " + "-" * self.options["control_integer_precision"] + "." + "-" * self.options["control_fraction_precision"]
		return "-" + " " + "-" * self.options["control_integer_precision"] + "." + "-" * self.options["control_fraction_precision"]
	
	def render_name(self,  name,  maxlength):
		if len(name) > maxlength:
			return name[0:maxlength - 2] + ".."
		
		return name + " " * (maxlength - len(name))
	
	def render_header(self, default_style):
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		
		text = []
		attr = []
	
		text.append("patterns ")
		attr.append((default_style,  len("patterns ")))
		
		text.append(column_separator)
		attr.append((default_style,  column_separator_len))
		
		text.append(" tick")
		attr.append((default_style,  len(" tick")))
		
		header = "patterns" + column_separator + "tick"
		
		for n in xrange(self.teq_engine.number_of_tracks()):
			text.append(column_separator)
			attr.append((default_style,  column_separator_len))
			
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
				attr.append(("track-name-highlight",  render_size))
			else:
				attr.append((default_style,  render_size))

		return (''.join(text),  attr)
	
	def cursor_pattern_in_loop_range(self, cursor_pattern):
		if self.info == None:
			return False
		
		if cursor_pattern < self.info.loop_range.end.pattern:
			return True
			
		if cursor_pattern >= self.info.loop_range.start.pattern:
			return True

		return False
	
	def cursor_in_loop_range(self, cursor_pattern, cursor_tick):
		if self.info == None:
			return False
		
		if not self.cursor_pattern_in_loop_range(cursor_pattern):
			return False
		
		if cursor_pattern == self.info.loop_range.start.pattern:
			if cursor_tick >= self.info.loop_range.start.tick:
				return True
			else:
				return False
			
		if cursor_pattern == self.info.loop_range.end.pattern:
			if cursor_tick < self.info.loop_range.end.tick:
				return True
			else:
				return False

		if cursor_pattern > self.info.loop_range.start.pattern and cursor_pattern < self.info.loop_range.end.pattern:
			return True

		return False
	
	def render_pattern(self):
		pattern = self.teq_engine.get_pattern(self.cursor_pattern)
		
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		highlighted_rows = self.options["highlighted_rows"]
		
		text = []
		attr = []
		
		for tick_index in xrange(pattern.length()):
			events = []
			event_attrs = []
			
			if self.cursor_in_loop_range(self.cursor_pattern, tick_index):
				events.append(self.options["loop_range_indicator_events"])
				event_attrs.append(("loop-range-indicator", len(events[-1])))
			else:
				events.append(" ")
				event_attrs.append((None, len(events[-1])))
			
			events.append("%0.4x" % tick_index)
			
			if tick_index == self.cursor_tick:
					event_attrs.append(("cursor-row-highlight", len(events[-1])))			
			else:
				if 0 == tick_index % highlighted_rows:
					event_attrs.append(("event-highligh", len(events[-1])))
				else:
					event_attrs.append(("event-default", len(events[-1])))
			
			for track_index in xrange(self.teq_engine.number_of_tracks()):
				event = None
				
				if self.teq_engine.track_type(track_index) == teq.track_type.MIDI:
					event = self.render_midi_event(pattern.get_midi_event(track_index,  tick_index))
				if self.teq_engine.track_type(track_index) == teq.track_type.CONTROL:
					event = self.render_control_event(pattern.get_control_event(track_index,  tick_index))
				if self.teq_engine.track_type(track_index) == teq.track_type.CV:
					event = self.render_cv_event(pattern.get_cv_event(track_index,  tick_index))
				
				events.append(column_separator)
				events.append(event)
				
				# Column separator
				if self.cursor_tick == tick_index:
					event_attrs.append(("cursor-row-highlight", column_separator_len))
				else:
					event_attrs.append((None, column_separator_len))

				# The event itself
				event_attr = (None, len(event))
				
				if tick_index % highlighted_rows == 0:
					event_attr = ("event-highlight", len(event))
				
				if self.cursor_track == track_index and self.cursor_tick == tick_index:
					event_attr = ("event-selected",  len(event))
				
				if self.cursor_track == track_index and not self.cursor_tick == tick_index:
					event_attr = ("track-events-highlight",  len(event))
						
				if not self.cursor_track == track_index and self.cursor_tick == tick_index:
					event_attr = ("cursor-row-highlight",  len(event))
						
				event_attrs.append(event_attr)
				
			text.append(''.join(events))
			attr.append(event_attrs)
			
		return (text,  attr)

	def render_patterns_list(self):
		text = []
		attr = []
		for n in xrange(0, self.teq_engine.number_of_patterns()):
			pattern_name = self.teq_engine.get_pattern(n).name
			if pattern_name == "":
				pattern_name = "." * 3
				
			text.append(self.render_name(pattern_name,  8))
			attr.append(("pattern-list-entry-default", len(text[-1])))
			
			#text.append(" ")
			#attr.append((None, len(text[-1])))
			
		return (text, attr)
	
	def render_footer(self, size, default_style):
		text = []
		attr = []
		
		if True == self.edit_mode:
			text.append(self.options["edit_mode_indicator_enabled"])
		else:
			text.append(self.options["edit_mode_indicator_disabled"])
		
		attr.append(("edit-mode-indicator", len(text[-1])))
		
		text.append(" ")
		attr.append((default_style, len(text[-1])))

		if None != self.info:
			if self.info.transport_state == teq.transport_state.PLAYING:
				text.append(self.options["transport_indicator_playing"])
				attr.append(("transport-playing", len(text[-1])))
			else:
				text.append(self.options["transport_indicator_stopped"])
				attr.append(("transport-stopped", len(text[-1])))

		text.append(" ")
		attr.append((default_style, len(text[-1])))

		text.append(self.render_note_on(self.options["note_edit_base"], self.options["note_edit_velocity"]))
		attr.append(("note-edit-base", len(text[-1])))

		text.append(" ")
		attr.append((default_style, len(text[-1])))

		menu = self.render_menu(default_style)
		text.append(menu[0])
		attr.extend(menu[1])

		text.append(str(self.teq_engine.get_global_tempo()) + " " + str(self.options["edit_step"]))
		attr.append(("song-properties", len(text[-1])))

		text.append(" ")
		attr.append((default_style, len(text[-1])))
		
		remainder = size - len(''.join(text))
		
		if remainder > 0:
			text.append(" " * remainder)
			attr.append((default_style, len(text[-1])))
		
		return (''.join(text), attr)
	
	def render(self,  size,  focus):
		if 1 == 0:
			if self.info == None:
				text = [" " * size[0]] * size[1]
				t = urwid.TextCanvas(text) 

				return t
			
		text = []
		attr = []
		
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		
		header_style = None
		if True == self.edit_mode:
			header_style = "header-editing"
		else:
			header_style = "header-default"
		
		header = self.render_header(header_style)
		
		header_text = header[0]
		header_attr = header[1]
		
		# Find out how much space to fill after the header
		remainder_len = size[0] - len(header_text)
	
		if remainder_len > 0:
			# And fill it
			header_text += " " * (remainder_len)
			header_attr.append((header_style, remainder_len))
		
		text.append(header_text)
		attr.append(header_attr)

		event_rows = size[1] - 2

		if self.cursor_pattern < self.teq_engine.number_of_patterns():
			pattern = self.teq_engine.get_pattern(self.cursor_pattern)
			
			
			split = int(round(event_rows * self.options["center_line_fraction"]))
			
			rendered_pattern = self.render_pattern()
			rendered_patterns_list = self.render_patterns_list()
			
			for n in range(0,  event_rows):
				displayed_tick = (self.cursor_tick + n) - split
				displayed_pattern = (self.cursor_pattern + n) - split

				# Initialize with an empty line and attributes
				line = ""
				line_attr = []

				if displayed_pattern >= 0 and displayed_pattern < self.teq_engine.number_of_patterns():
					line = rendered_patterns_list[0][displayed_pattern]
					if displayed_pattern == self.cursor_pattern:
						line_attr.append((header_style, rendered_patterns_list[1][displayed_pattern][1]))
					else:
						line_attr.append(rendered_patterns_list[1][displayed_pattern])
				else:
					line = " " * len("patterns")
					line_attr.append((None, len("patterns")))
				
				line += column_separator
				if displayed_pattern == self.cursor_pattern:
					line_attr.append((header_style, column_separator_len))
				else:
					line_attr.append((None, column_separator_len))
				
				if displayed_tick >= 0 and displayed_tick < pattern.length():
					line += rendered_pattern[0][displayed_tick]
					line_attr.extend(rendered_pattern[1][displayed_tick])
				
				remainder = size[0] - len(line)
				if remainder > 0:
					line += " " * remainder
					if displayed_tick == self.cursor_tick:
						line_attr.append((header_style, remainder))
					else:
						line_attr.append((None, remainder))
				
				text.append(line)
				attr.append(line_attr)	
		else:
			for n in xrange(0, event_rows):
				text.append(" " * size[0])
				attr.append([(None, len(text[-1]))])
		
		footer_style = None
		if True == self.edit_mode:
			footer_style = "footer-editing"
		else:
			footer_style = "footer-default"
		
		footer = self.render_footer(size[0], footer_style)
		
		text.append(footer[0])
		attr.append(footer[1])
		
		t = urwid.TextCanvas(text,  attr,  maxcol = size[0]) 

		return t
	
	def save(self):
		pass

teq_engine = teq.teq()

def test_state():
	teq_engine.insert_control_track("control",  teq_engine.number_of_tracks())
	teq_engine.insert_midi_track("bd",  teq_engine.number_of_tracks())
	teq_engine.insert_midi_track("snare",  teq_engine.number_of_tracks())
	if 1 == 1:
		teq_engine.insert_midi_track("bd2",  teq_engine.number_of_tracks())
		teq_engine.insert_midi_track("snare2",  teq_engine.number_of_tracks())
		teq_engine.insert_cv_track("cv",  teq_engine.number_of_tracks())
		teq_engine.insert_midi_track("bd3",  teq_engine.number_of_tracks())
		teq_engine.insert_midi_track("snare3",  teq_engine.number_of_tracks())
		teq_engine.insert_midi_track("bd4",  teq_engine.number_of_tracks())
		teq_engine.insert_midi_track("snare4",  teq_engine.number_of_tracks())

	for n in xrange(4):
		p = teq_engine.create_pattern(32)
		p.name = "part" + str(n)
		p.set_midi_event(1,  0,  teq.midi_event(teq.midi_event_type.ON,  63,  127))
		p.set_midi_event(1,  4,  teq.midi_event(teq.midi_event_type.OFF,  60,  127))
		p.set_midi_event(1,  2,  teq.midi_event(teq.midi_event_type.CC,  60,  127))
		p.set_control_event(0, 0, teq.control_event(teq.control_event_type.GLOBAL_TEMPO, 8))
		teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

		p = teq_engine.create_pattern(32)
		p.set_midi_event(1,  0,  teq.midi_event(teq.midi_event_type.ON,  60,  127))
		p.set_midi_event(1,  4,  teq.midi_event(teq.midi_event_type.OFF,  62,  127))
		teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

		p = teq_engine.create_pattern(32)
		p.set_midi_event(1,  0,  teq.midi_event(teq.midi_event_type.ON,  60,  127))
		p.set_midi_event(1,  4,  teq.midi_event(teq.midi_event_type.OFF,  62,  127))
		teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

		p = teq_engine.create_pattern(32)
		p.set_midi_event(1,  0,  teq.midi_event(teq.midi_event_type.ON,  60,  127))
		p.set_midi_event(1,  4,  teq.midi_event(teq.midi_event_type.OFF,  62,  127))
		teq_engine.insert_pattern(teq_engine.number_of_patterns(),  p)

	teq_engine.set_global_tempo(16)
	pyteq.set_transport_position(teq_engine,  0,  0)
	pyteq.set_loop_range(teq_engine,  0,  8,  2,  16,  True)

if 1 == 1:
	test_state()
	

# TODO: merge in user options
options = default_options.options

def handle_alarm(main_loop,  the_main):
	#print("alarm")
	the_main.get_state_info_and_update()
	main_loop.set_alarm_in(the_main.options["ui_update_interval"] - random.random() * 0.5 * the_main.options["ui_update_interval"],  handle_alarm,  the_main)

the_main = main(teq_engine,  options)

popup_launcher = PopUpLauncherThing(the_main)

loop = urwid.MainLoop(popup_launcher,  options["palette"], pop_ups=True)

loop.set_alarm_in(the_main.options["ui_update_interval"],  handle_alarm,  the_main)

loop.run()
