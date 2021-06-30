import urwid
import history
import math
import string
import json
import teq
import pyteq
import traceback
import the_help
import about
import license
import webbrowser
import tempfile
import errno

class TextPopup(urwid.WidgetWrap):
	def __init__(self, text):
		self.the_text = text
		text = urwid.Text(text)
		help_list_box = urwid.ListBox(urwid.SimpleListWalker([text]))

		self.__super.__init__(help_list_box)
		
		urwid.register_signal(TextPopup, 'close')

	def keypress(self, size, key):
		if key == 'esc':
			self._emit('close')
			return True
		
		if key == 'b':
			t = tempfile.mktemp()
			f = open(t, "w")
			f.write(("<html><head></head><body>" + self.the_text[1] + "</body></html>").replace("\n", "<br>"))
			webbrowser.open("file://" + t)
			return True
		
		self._w.keypress(size, key)

class EditWithEnter(urwid.WidgetWrap):
	def __init__(self, question):
		self.history = []
		self.edit = urwid.Edit(question)
		help_list_box = urwid.ListBox(urwid.SimpleListWalker([self.edit]))
		
		self.__super.__init__(help_list_box)
		urwid.register_signal(EditWithEnter, 'enter')

	def keypress(self, size, key):
		if key == 'enter':
			self._emit('enter')
			return True
		
		self._w.keypress(size, key)

class PopUpLauncherThing(urwid.PopUpLauncher):
	def __init__(self, original):
		self.__super.__init__(original)
		
		self.the_original = original
		
		original.popup_launcher = self
		
		urwid.connect_signal(original, 'popup_about', lambda x: self.popup_about())
		urwid.connect_signal(original, 'popup_license', lambda x: self.popup_license())
		urwid.connect_signal(original, 'popup_help', lambda x: self.popup_help())

	def popup_text(self, text):
		self.popup_widget = TextPopup(("medium", "Press esc to leave this screen. Press b to open display this text in a webbrowser (python's webbrowser.open() will be used on a temp file)\n\n" + text))
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		self.open_pop_up()

	def popup_help(self):
		self.popup_text(the_help.get_help_text(self.the_original.options))

	def popup_license(self):
		self.popup_text(license.text)

	def popup_about(self):
		self.popup_text(about.text)
		
	def popup_line_entry(self, question, popup_parameters, callback):
		self.callback = callback
		self.popup_widget = EditWithEnter(("line-entry", question))
		attr_map = urwid.AttrMap(self.popup_widget, "line-entry")
		urwid.connect_signal(self.popup_widget, 'enter', lambda x: self.close_pop_up_line_entry())
		self.popup_parameters = popup_parameters
		self.open_pop_up()

	def close_pop_up_line_entry(self):
		self.callback(self.popup_widget.edit.edit_text)
		#self.callback("foo")
		self.close_pop_up()

	def get_pop_up_parameters(self):
		return self.popup_parameters
	
	def create_pop_up(self):
		return self.popup_widget
	

class cursor_position():
	def __init__(self, track = 0, pattern = 0, tick = 0):
		self.pattern = pattern
		self.tick = tick
		self.track = track


class main_window(urwid.Widget):
	def __init__(self,  teq_engine,  options, filename):
		self.__super.__init__()
		
		self.options = options

		urwid.register_signal(main_window, ['popup_about', 'popup_license', 'popup_help'])
		
		self.text_to_show = None
		
		self.evaluation_history = []
		self.pattern_length_history = []
		self.cv_value_history = []
		self.control_value_history = []
		
		self.popup_parameters = None
		
		self.filename = filename
		self.teq_engine = teq_engine
		
		self._sizing = frozenset(['box'])
		
		self.cursor = cursor_position()
		
		self.selection_start = None
		
		self.history = history.history()

		self.info = None
		
		self.edit_mode = False
		
		self.current_menu = self.options["menu"]
		for menu in self.current_menu:
			self.fixup_menu(menu)
			
		self.load()
	
	
	def handle_error(f):
		def g(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except urwid.ExitMainLoop as e:
				raise e
			except Exception as e:
				args[0].display_text(str(e) + "\n" + traceback.format_exc())
				args[0].exit_menu()
				
		return g
	
	def state_changed(self, old_info, new_info):
		if old_info.transport_position.tick != new_info.transport_position.tick:
			return True
		
		if old_info.transport_position.pattern != new_info.transport_position.pattern:
			return True
		
		if old_info.transport_state != self.info.transport_state:
			return True
		
		return False
		
	def get_state_info_and_update(self):
		self.handle_text_popups()
		old_info = self.info
		
		try:
			while self.teq_engine.has_state_info():
				self.info = self.teq_engine.get_state_info()
				#self.display_text("yay")
		except Exception as e:
			self.display_text(str(e))
			pass
		
		# Check if the transport position changed
		if old_info and self.info:
			if self.state_changed(old_info, self.info):
				if self.options["follow_transport"] == True:
					self.cursor.tick = self.info.transport_position.tick
					self.cursor.pattern = self.info.transport_position.pattern
				
		self._invalidate()
	
	def handle_text_popups(self):
		if self.text_to_show:
			self.popup_launcher.popup_text(self.text_to_show)
		self.text_to_show = None
	
	@handle_error
	def display_text(self, text):
		# The handle_text_popups method will show it the next time the timer 
		# fires up..
		self.text_to_show = text
	
	@handle_error
	def evaluate(self):
		self.popup_launcher.popup_line_entry("Expression: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.evaluate_string(x))
	
	@handle_error
	def evaluate_string(self, string):
		if self.evaluation_history.count(string) == 0:
			self.evaluation_history.append(string)
		eval(string, { "ui": self, "teq": self.teq_engine })
		self._invalidate()
		#self.display_text(string)
	
	def fixup_menu(self, menu):
		# print ("fixing up", menu)
		if 0 == len(menu[3]):
			l = menu[2]
			menu[2] = lambda x: l(x) or x.exit_menu()
			return
		
		for submenu in menu[3]:
			self.fixup_menu(submenu)

		menu[3].append(["root", "x", lambda x: x.exit_menu(), []])
	
	@handle_error
	def change_menu(self, menu):
		self.current_menu = menu
	
	@handle_error
	def exit_menu(self):
		self.current_menu = self.options["menu"]
	
	@handle_error
	def undo(self):
		self.history.undo()
	
	@handle_error
	def redo(self):
		self.history.redo()
	
	@handle_error
	def toggle_follow_transport(self):
		self.options["follow_transport"] = not self.options["follow_transport"]
		self._invalidate()

	@handle_error
	def toggle_loop(self):
		if self.info:
			loop_range = self.info.loop_range
			loop_range.enabled = not loop_range.enabled
			self.teq_engine.set_loop_range(loop_range)
			self._invalidate()
	
	@handle_error
	def rename_pattern(self):
		self.popup_launcher.popup_line_entry("Pattern Name: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.rename_pattern_with_name(x))
	
	@handle_error
	def rename_pattern_with_name(self, name):
		p = self.teq_engine.get_pattern(self.cursor.pattern)
		p.name = str(name)
		self.teq_engine.set_pattern(self.cursor.pattern, p)
		self._invalidate()
	
	@handle_error
	def rename_track(self):
		self.popup_launcher.popup_line_entry("Track Name: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.rename_track_with_name(x))
	
	@handle_error
	def rename_track_with_name(self, name):
		self.teq_engine.rename_track(self.cursor.track, name)
		self._invalidate()

	@handle_error
	def add_pattern(self):
		self.popup_launcher.popup_line_entry("Patten Length (Ticks): ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.add_pattern_with_length(x))
	
	@handle_error
	def add_pattern_with_length(self, length_text):
		length = int(length_text)
		if self.teq_engine.number_of_patterns() == 0:
			self.teq_engine.insert_pattern(0, self.teq_engine.create_pattern(length))
		else:
			self.teq_engine.insert_pattern(self.cursor.pattern + 1, self.teq_engine.create_pattern(length))
		
		self._invalidate()
		
	
	@handle_error
	def add_midi_track(self):
		self.popup_launcher.popup_line_entry("Track Name: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.add_named_midi_track(x))

	@handle_error
	def add_named_midi_track(self, name):
		self.teq_engine.insert_midi_track(str(name), self.teq_engine.number_of_tracks())
		self.history.reset()
		self._invalidate()
		
	@handle_error
	def add_control_track(self):
		self.popup_launcher.popup_line_entry("Track Name: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.add_named_control_track(x))

	@handle_error
	def add_named_control_track(self, name):
		self.teq_engine.insert_control_track(name, self.teq_engine.number_of_tracks())
		self.history.reset()
		self._invalidate()
		
	@handle_error
	def add_cv_track(self):
		self.popup_launcher.popup_line_entry("Track Name: ", {'left':0, 'top':self.render_size[1] - 1, 'overlay_width':200, 'overlay_height':1}, lambda x: self.add_named_cv_track(x))

	@handle_error
	def add_named_cv_track(self, name):
		self.teq_engine.insert_cv_track(name, self.teq_engine.number_of_tracks())
		self.history.reset()
		self._invalidate()
		
	@handle_error
	def change_tempo(self, amount):
		self.teq_engine.set_global_tempo(self.teq_engine.get_global_tempo() + amount)
	
	@handle_error
	def change_note_edit_base(self, amount):
		self.options["note_edit_base"] += amount
	
	@handle_error
	def set_transport_source(self, source):
		if source == "jack_transport":
			self.teq_engine.set_transport_source(teq.transport_source.JACK_TRANSPORT)
		if source == "internal":
			self.teq_engine.set_transport_source(teq.transport_source.INTERNAL)
	
	@handle_error
	def change_note_velocity(self, amount):
		self.options["note_edit_velocity"] += amount
	
	@handle_error
	def change_edit_step(self, amount):
		self.options["edit_step"] += amount
	
	@handle_error
	def set_edit_step(self, step):
		self.options["edit_step"] = step
	
	# Only the sign of amount is important
	@handle_error
	def change_cursor_tick_by_one(self, amount):
		if not self.info:
			return

		if self.info.transport_state == teq.transport_state.PLAYING and self.options["follow_transport"]:
			return
		
		if 0 == amount:
			return
		
		if amount > 0:
			self.cursor.tick += 1
		else:
			self.cursor.tick -= 1
		
		pattern = self.teq_engine.get_pattern(self.cursor.pattern)
		
		if self.cursor.tick < 0:
			if self.options["cursor_wrap_mode"] == "pattern":
				self.cursor.tick = pattern.length() - 1
			if self.options["cursor_wrap_mode"] == "song":
				self.cursor.pattern -= 1
				if self.cursor.pattern < 0:
					self.cursor.pattern = self.teq_engine.number_of_patterns() - 1
				new_pattern = self.teq_engine.get_pattern(self.cursor.pattern)
				self.cursor.tick = new_pattern.length() - 1
				
		if self.cursor.tick >= pattern.length():
			if self.options["cursor_wrap_mode"] == "pattern":
				self.cursor.tick = 0
			if self.options["cursor_wrap_mode"] == "song":
				self.cursor.tick = 0
				self.cursor.pattern += 1
				if self.cursor.pattern >= self.teq_engine.number_of_patterns():
					self.cursor.pattern = 0
	
	@handle_error
	def change_cursor_tick(self, amount):
		for n in range(abs(amount)):
			self.change_cursor_tick_by_one(amount)
		
	@handle_error
	def change_cursor_track(self, amount):
		self.cursor.track += amount
		self.cursor.track = self.cursor.track % self.teq_engine.number_of_tracks()
	
	@handle_error
	def change_cursor_pattern(self, amount):
		if self.teq_engine.number_of_patterns() == 0:
			return
		
		self.cursor.pattern += amount
		
		self.cursor.pattern = self.cursor.pattern % self.teq_engine.number_of_patterns()

	@handle_error
	def set_loop_start(self):
		if not self.info:
			return
		
		loop_range = self.info.loop_range
		loop_range.start.pattern = self.cursor.pattern
		loop_range.start.tick = self.cursor.tick
		
		self.teq_engine.set_loop_range(loop_range)
		self._invalidate()

	@handle_error
	def set_loop_end(self):
		if not self.info:
			return
		
		loop_range = self.info.loop_range
		loop_range.end.pattern = self.cursor.pattern
		loop_range.end.tick = self.cursor.tick
		
		self.teq_engine.set_loop_range(loop_range)
		self._invalidate()

	@handle_error
	def move_to_pattern_top(self):
		self.cursor.tick = 0
	
	@handle_error
	def move_to_pattern_end(self):
		pattern = self.teq_engine.get_pattern(self.cursor.pattern)
		self.cursor.tick = pattern.length() - 1
	
	@handle_error
	def delete_event(self):
		if False == self.edit_mode:
			return

		self.set_midi_event_action(self.cursor.track, self.cursor.pattern, self.cursor.tick, teq.midi_event_type.NONE, 0, 127)
		self._invalidate()
		return	
	
	def quit(self):
		raise urwid.ExitMainLoop()
	
	@handle_error
	def toggle_edit_mode(self):
		self.edit_mode = not self.edit_mode
		self._invalidate()
	
	@handle_error
	def toggle_playback(self):
		if self.info == None:
			print(":(")
			return
		
		if self.info.transport_state == teq.transport_state.PLAYING:
			pyteq.stop(self.teq_engine)
		else:
			pyteq.set_transport_position(self.teq_engine,  self.cursor.pattern,  self.cursor.tick)
			pyteq.play(self.teq_engine)
		
		self._invalidate()
	
	def selectable(self):
		return True
	
	@handle_error
	def create_cv_constant_event(self):
		if not self.edit_mode:
			return
		
		pattern = self.teq_engine.get_pattern(self.cursor.pattern)
		pattern.set_cv_event(self.cursor.track, self.cursor.tick, teq.cv_event(teq.cv_event_type.CONSTANT, 0, 0))
		self.teq_engine.set_pattern(self.cursor.pattern, pattern)
		self.teq_engine.gc()
		
	
	@handle_error
	def set_midi_event(self, track_index, pattern_index, tick_index, event_type, value1, value2):
		pattern = self.teq_engine.get_pattern(pattern_index)
		pattern.set_midi_event(track_index, tick_index, teq.midi_event(event_type, value1, value2))
		self.teq_engine.set_pattern(self.cursor.pattern, pattern)
		self.teq_engine.gc()
		
	@handle_error
	def set_midi_event_action(self, track_index, pattern_index, tick_index, event_type, value1, value2):
		pattern = self.teq_engine.get_pattern(pattern_index)
		event = pattern.get_midi_event(track_index, tick_index)
		self.history.add(
			lambda: self.set_midi_event(track_index, pattern_index, tick_index, event_type, value1, value2), 
			lambda: self.set_midi_event(track_index, pattern_index, tick_index, event.type, event.value1, event.value2)
		)
	
	@handle_error
	def mouse_event(self,  size,  event,  button,  col,  row,  focus):
		if self.teq_engine.number_of_patterns() == 0:
			return 
		
		for entry in self.options["global_mouse_events"]:
			if entry[0][0] == event and entry[0][1] == button:
				entry[2](self)
				self._invalidate()
				return True
	
	@handle_error
	def keypress(self,  size,  key):
		#self.display_text(key)
		#return
	
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
			
		if self.teq_engine.track_type(self.cursor.track) == teq.track_type.MIDI:
			for k in self.options["midi_track_keys"]:
				if k[0] == key:
					k[2](self)
					self._invalidate()
					return
			
		if self.teq_engine.track_type(self.cursor.track) == teq.track_type.CV:
			for k in self.options["cv_track_keys"]:
				if k[0] == key:
					k[2](self)
					self._invalidate()
					return
			
		if self.teq_engine.track_type(self.cursor.track) == teq.track_type.CONTROL:
			for k in self.options["control_track_keys"]:
				if k[0] == key:
					k[2](self)
					self._invalidate()
					return
			
		track_type = self.teq_engine.track_type(self.cursor.track)
		
		if track_type == teq.track_type.MIDI:
			if key == self.options["note_off_key"]:
				if True == self.edit_mode:
					self.set_midi_event_action(self.cursor.track, self.cursor.pattern, self.cursor.tick, teq.midi_event_type.OFF, 0, 127)
					self._invalidate()
					return
				
			for k in self.options["note_keys"]:
				if k[0] == key and True == self.edit_mode:
					self.set_midi_event_action(self.cursor.track, self.cursor.pattern, self.cursor.tick, teq.midi_event_type.ON, self.options["note_edit_base"] + k[1], self.options["note_edit_velocity"])
					self.change_cursor_tick(self.options["edit_step"])
					self._invalidate()
					return
	
	def fill_line(self,  line,  n):
		return (line + " " * n)[0:n]
	
	def render_key(self, key):
		if key == " ":
			return "space"
		
		ret = key
		ret = ret.replace("ctrl", "C")
		ret = ret.replace("meta", "M")
		
		return ret
	
	def render_note_on(self, value1, value2):
		octave = math.floor(value1 / 12)
		note = self.options["note_names"][value1 % 12]
		return note + "%0.1x" % octave + " " + "%0.2x" % value2
	
	def render_menu(self, default_style):
		text = []
		attr = []
		
		for n in range(len(self.current_menu)):
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
		return 3 + 2 * (self.options["cv_integer_precision"] + 1 + self.options["cv_fraction_precision"])
	
	def track_render_size(self, track_index):
		if self.teq_engine.track_type(track_index) == teq.track_type.MIDI:
			return self.midi_track_render_size()
		
		if self.teq_engine.track_type(track_index) == teq.track_type.CV:
			return self.cv_track_render_size()
		
		if self.teq_engine.track_type(track_index) == teq.track_type.CONTROL:
			return self.control_track_render_size()
		
		return 0
	
	def render_midi_event(self,  event):
		if event.type == teq.midi_event_type.ON:
			return self.render_note_on(event.value1, event.value2)
		
		if event.type == teq.midi_event_type.OFF:
			return "OFF --"
		
		if event.type == teq.midi_event_type.CC:
			return "%0.2x" % event.value1 + "  " + "%0.2x" % event.value2
		
		return "--- --"
	
	def render_number(self, integer_precision, fractional_precision, number):
		return ("{0:" + str(integer_precision + 1 + fractional_precision) + "." + str(fractional_precision) + "f}").format(number)
	
	def render_cv_event(self,  event):
		if event.type == teq.cv_event_type.CONSTANT:
			return "C" + " " + self.render_number(self.options["control_integer_precision"], self.options["control_fraction_precision"], event.value1) + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"]
		if event.type == teq.cv_event_type.INTERVAL:
			return "I" + " " + self.render_number(self.options["control_integer_precision"], self.options["control_fraction_precision"], event.value1) + " " + self.render_number(self.options["control_integer_precision"], self.options["control_fraction_precision"], event.value2)

		return "-" + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"] + " " + "-" * self.options["cv_integer_precision"] + "." + "-" * self.options["cv_fraction_precision"]
	
	def render_control_event(self,  event):
		if event.type == teq.control_event_type.GLOBAL_TEMPO:
			return "G" + " " + self.render_number(self.options["control_integer_precision"], self.options["control_fraction_precision"], event.value)
		
		if event.type == teq.control_event_type.RELATIVE_TEMPO:
			return "R" + " " + self.render_number(self.options["control_integer_precision"], self.options["control_fraction_precision"], event.value)
		
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
				
		for n in range(self.teq_engine.number_of_tracks()):
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
			if self.cursor.track == n:
				attr.append(("track-name-highlight",  render_size))
			else:
				attr.append((default_style,  render_size))

		return (''.join(text),  attr)
	
	@handle_error
	def cursor_pattern_in_loop_range(self, cursor_pattern):
		if self.info == None:
			return False
		
		if cursor_pattern == self.info.loop_range.end.pattern and self.info.loop_range.end.tick == 0:
			return False
		
		if cursor_pattern >= self.info.loop_range.start.pattern and cursor_pattern <= self.info.loop_range.end.pattern:
			return True

		return False
	
	@handle_error
	def cursor_in_loop_range(self, cursor_pattern, cursor_tick):
		if self.info == None:
			return False
		
		if not self.cursor_pattern_in_loop_range(cursor_pattern):
			return False
		
		if cursor_pattern == self.info.loop_range.start.pattern:
			if cursor_tick < self.info.loop_range.start.tick:
				return False
			
		if cursor_pattern == self.info.loop_range.end.pattern:
			if cursor_tick >= self.info.loop_range.end.tick:
				return False

		return True
	
	def render_pattern(self):
		pattern = self.teq_engine.get_pattern(self.cursor.pattern)
		
		column_separator = self.options["column_separator"]
		column_separator_len = len(column_separator)
		highlighted_rows = self.options["highlighted_rows"]
		
		text = []
		attr = []
		
		for tick_index in range(pattern.length()):
			events = []
			event_attrs = []
			
			if self.cursor_in_loop_range(self.cursor.pattern, tick_index):
				events.append(self.options["loop_range_indicator_events"])
				event_attrs.append(("loop-range-indicator", len(events[-1])))
			else:
				events.append(" ")
				if self.info and self.info.transport_position.tick == tick_index and self.info.transport_position.pattern == self.cursor.pattern:
					event_attrs.append(("cursor-row-highlight", len(events[-1])))
				else:
					event_attrs.append((None, len(events[-1])))
			
			events.append("%0.4x" % tick_index)
			
			if self.info and tick_index == self.info.transport_position.tick and self.cursor.pattern == self.info.transport_position.pattern:
					event_attrs.append(("cursor-row-highlight", len(events[-1])))			
			else:
				if 0 == tick_index % highlighted_rows:
					event_attrs.append(("event-highlight", len(events[-1])))
				else:
					event_attrs.append(("event-default", len(events[-1])))
			
			for track_index in range(self.teq_engine.number_of_tracks()):
				events.append(column_separator)
				
				# Column separator
				if self.info and self.info.transport_position.tick == tick_index and self.cursor.pattern == self.info.transport_position.pattern:
					event_attrs.append(("cursor-row-highlight", column_separator_len))
				else:
					event_attrs.append((None, column_separator_len))

				event = None
				
				if self.teq_engine.track_type(track_index) == teq.track_type.MIDI:
					event = self.render_midi_event(pattern.get_midi_event(track_index,  tick_index))
				if self.teq_engine.track_type(track_index) == teq.track_type.CONTROL:
					event = self.render_control_event(pattern.get_control_event(track_index,  tick_index))
				if self.teq_engine.track_type(track_index) == teq.track_type.CV:
					event = self.render_cv_event(pattern.get_cv_event(track_index,  tick_index))
				
				# The event itself
				events.append(event)
				event_attr = (None, len(event))
				
				if tick_index % highlighted_rows == 0:
					event_attr = ("event-highlight", len(event))

				if self.cursor.track == track_index:
					event_attr = ("track-events-highlight",  len(event))
					
				if self.info and self.cursor.pattern == self.info.transport_position.pattern:
					if self.info.transport_position.tick == tick_index:
						event_attr = ("cursor-row-highlight",  len(event))
							
				if self.cursor.track == track_index and self.cursor.tick == tick_index:
					event_attr = ("event-selected",  len(event))

					
				event_attrs.append(event_attr)
				
			text.append(''.join(events))
			attr.append(event_attrs)
			
		return (text,  attr)

	def render_patterns_list(self):
		text = []
		attr = []
		
		for n in range(self.teq_engine.number_of_patterns()):
			line = []
			line_attr = []
			
			pattern_name = self.teq_engine.get_pattern(n).name
			if pattern_name == "":
				pattern_name = "-" * 8
			else:
				pattern_name = self.render_name(pattern_name,  len("patterns"))

			line.append(pattern_name)
			
			name_attr = ("pattern-list-entry-default", len(line[-1]))
			if self.info:
				if n == self.info.transport_position.pattern:
					name_attr = ("cursor-row-highlight", len(line[-1]))
				if n == self.cursor.pattern:
					name_attr = ("event-selected", len(line[-1]))
			line_attr.append(name_attr)
				
			if self.cursor_pattern_in_loop_range(n):
				line.append(self.options["loop_range_indicator_patterns"])
				line_attr.append(("loop-range-indicator", len(line[-1])))
			else:
				line.append(" ")
				line_attr.append(("pattern-list-entry-default", len(line[-1])))
				
				
			text.append("".join(line))
			attr.append(line_attr)
			
		return (text, attr)
	
	def render_footer(self, size, default_style):
		text = []
		attr = []
		
		if True == self.edit_mode:
			text.append(self.options["edit_mode_indicator_enabled"])
		else:
			text.append(self.options["edit_mode_indicator_disabled"])
		
		attr.append(("edit-mode-indicator", len(text[-1])))
		
		if self.teq_engine.get_transport_source() == teq.transport_source.JACK_TRANSPORT:
			text.append(self.options["transport_source_indicator_jack_transport"])
			attr.append(("transport-source-indicator", len(text[-1])))
			
		if self.teq_engine.get_transport_source() == teq.transport_source.INTERNAL:
			text.append(self.options["transport_source_indicator_internal"])
			attr.append(("transport-source-indicator", len(text[-1])))
			
		
		if self.options["follow_transport"]:
			text.append(self.options["follow_transport_indicator_enabled"])
			attr.append(("follow-transport-indicator-enabled", len(text[-1])))
		else:
			text.append(self.options["follow_transport_indicator_disabled"])
			attr.append(("follow-transport-indicator-disabled", len(text[-1])))
			
		
		if self.info:
			if self.info.loop_range.enabled:
				text.append(self.options["loop_indicator_enabled"])
				attr.append(("loop-indicator-enabled", len(text[-1])))
			else:
				text.append(self.options["loop_indicator_disabled"])
				attr.append(("loop-indicator-disabled", len(text[-1])))
		
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
		self.render_size = size
			
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

		split = int(round(event_rows * self.options["center_line_fraction"]))
		
		if self.cursor.pattern < self.teq_engine.number_of_patterns():
			pattern = self.teq_engine.get_pattern(self.cursor.pattern)
			
			
			rendered_patterns_list = self.render_patterns_list()
			
			if len(rendered_patterns_list):
				patterns_list_len = len(rendered_patterns_list[0][0])
			
			rendered_pattern = self.render_pattern()

			for n in range(event_rows):
				displayed_tick = (self.cursor.tick + n) - split
				displayed_pattern = (self.cursor.pattern + n) - split

				# Initialize with an empty line and attributes
				line = []
				line_attr = []

				if displayed_pattern >= 0 and displayed_pattern < self.teq_engine.number_of_patterns():
					line.append(rendered_patterns_list[0][displayed_pattern])
					line_attr.extend(rendered_patterns_list[1][displayed_pattern])
				else:
					line.append(" " * len("patterns "))
					line_attr.append((None, len(line[-1])))
				
				line.append(column_separator)
				line_attr.append((None, len(line[-1])))
				
				if displayed_tick >= 0 and displayed_tick < pattern.length():
					line.append(rendered_pattern[0][displayed_tick])
					line_attr.extend(rendered_pattern[1][displayed_tick])
				
					
				text.append("".join(line))
				attr.append(line_attr)	
		else:
			for n in range(event_rows):
				text.append("~" * size[0])
				attr.append([(None, len(text[-1]))])
		
		footer_style = None
		if True == self.edit_mode:
			footer_style = "footer-editing"
		else:
			footer_style = "footer-default"
		
		footer = self.render_footer(size[0], footer_style)
		
		text.append(footer[0])
		attr.append(footer[1])
		
		# Sanity checks against small displays
		if len(max(text, key=len)) > size[0] or 3 > size[1]:
			text = []
			attr = []
			
			for n in range(size[1]):
				text_line = []
				line_attr = []
				if n == 0:
					text_line.append("terminal too small - please make it wider or taller!"[0:size[0]])
				else:
					text_line.append(".")

				line_attr.append((None, len(text_line[-1])))
				
				remainder = size[0] - len(text_line[-1])
				if remainder > 0:
					text_line.append(" " * remainder)
					line_attr.append((None, len(text_line[-1])))
				
				text.append("".join(text_line))
				attr.append(line_attr)
			
		
		cursor = self.get_cursor_coords(size)
		
		t = urwid.TextCanvas(list(map(lambda x: x.encode(), text)),  attr,  maxcol = size[0], cursor = self.get_cursor_coords(size)) 

		return t

	def get_split(self, size):
		event_rows = size[1] - 2
		return int(round(event_rows * self.options["center_line_fraction"]))
		
	def get_cursor_coords(self, size):
		return (int(self.cursor_x_pos(self.cursor.track)), self.get_split(size) + 1)

	@handle_error
	def cursor_x_pos(self, track_index):
		column_separator = self.options["column_separator"]
		x_pos = len("patterns " + column_separator + " tick" + column_separator)

		for n in range(0, self.cursor.track):
			x_pos += self.track_render_size(n)
			x_pos += len(column_separator)

		return int(x_pos)
		

	@handle_error	
	def load(self):
		try:
			print("loading " + self.filename)
			with open(self.filename, "r") as textfile:
				text = textfile.read()
				json_object = json.loads(text)
				
				for track in json_object["tracks"]:
					print("track ", track["name"])
					if track["type"] == "CONTROL":
						self.teq_engine.insert_control_track(str(track["name"]), self.teq_engine.number_of_tracks())
					if track["type"] == "CV":
						self.teq_engine.insert_cv_track(str(track["name"]), self.teq_engine.number_of_tracks())
					if track["type"] == "MIDI":
						self.teq_engine.insert_midi_track(str(track["name"]), self.teq_engine.number_of_tracks())
		
				pyteq.set_loop_range(self.teq_engine, json_object["loop-range-start-pattern"], json_object["loop-range-start-tick"], json_object["loop-range-end-pattern"], json_object["loop-range-end-tick"], json_object["loop-range-enabled"])
				
				self.cursor.pattern = json_object["cursor-position-pattern"]
				self.cursor.tick = json_object["cursor-position-tick"]
				self.cursor.track = json_object["cursor-position-track"]
				
				self.options["edit_step"] = json_object["edit-step"]
				self.options["follow_transport"] = json_object["follow-transport"]
				
				self.teq_engine.set_global_tempo(json_object["global-tempo"])
				
				if "transport-source" in json_object:
					if json_object["transport-source"] == "jack_transport":
						self.set_transport_source("jack_transport")
				
					if json_object["transport-source"] == "internal":
						self.set_transport_source("internal")
				
				for pattern in json_object["patterns"]:
					print("pattern ", str(pattern[0]))
					new_pattern = self.teq_engine.create_pattern(int(pattern[1]))
					new_pattern.name = str(pattern[0])
					for track in range(self.teq_engine.number_of_tracks()):
						for event in pattern[track + 2]:
							if self.teq_engine.track_type(track) == teq.track_type.MIDI:
								if event[1] == "ON":
									new_pattern.set_midi_event(int(track), int(event[0]), teq.midi_event(teq.midi_event_type.ON, event[2], event[3]))
								if event[1] == "OFF":
									new_pattern.set_midi_event(int(track), int(event[0]), teq.midi_event(teq.midi_event_type.OFF, event[2], event[3]))
								if event[1] == "CC":
									new_pattern.set_midi_event(int(track), int(event[0]), teq.midi_event(teq.midi_event_type.CC, event[2], event[3]))

							if self.teq_engine.track_type(track) == teq.track_type.CONTROL:
								if event[1] == "GLOBAL_TEMPO":
									new_pattern.set_control_event(int(track), int(event[0]), teq.control_event(teq.control_event_type.GLOBAL_TEMPO, event[2]))
								if event[1] == "RELATIVE_TEMPO":
									new_pattern.set_control_event(int(track), int(event[0]), teq.control_event(teq.control_event_type.RELATIVE_TEMPO, event[2]))
									
							if self.teq_engine.track_type(track) == teq.track_type.CV:
								if event[1] == "INTERVAL":
									new_pattern.set_cv_event(int(track), int(event[0]), teq.cv_event(teq.cv_event_type.INTERVAL, event[2], event[3]))
								if event[1] == "CONSTANT":
									new_pattern.set_cv_event(int(track), int(event[0]), teq.cv_event(teq.cv_event_type.CONSTANT, event[2], event[3]))
								
					self.teq_engine.insert_pattern(self.teq_engine.number_of_patterns(), new_pattern)
			print("done")
		except IOError as e:
			if e.errno == errno.ENOENT:
				pass
			else:
				raise e
		
	@handle_error
	def save(self):
		if self.info == None:
			self.display_text("Oh oh, couldn't save :( Try again later")
			return
		
		loop_range = self
		json_object = {
			"global-tempo": self.teq_engine.get_global_tempo(),
			
			"loop-range-start-pattern": self.info.loop_range.start.pattern,
			"loop-range-start-tick": self.info.loop_range.start.tick,
			"loop-range-end-pattern": self.info.loop_range.end.pattern,
			"loop-range-end-tick": self.info.loop_range.end.tick,
			"loop-range-enabled": self.info.loop_range.enabled,
			
			"cursor-position-pattern": self.cursor.pattern,
			"cursor-position-tick": self.cursor.tick,
			"cursor-position-track": self.cursor.track,
			
			"follow-transport": self.options["follow_transport"],
			
			"edit-step": self.options["edit_step"],
		}
		
		if self.teq_engine.get_transport_source() == teq.transport_source.JACK_TRANSPORT:
			json_object["transport-source"] = "jack_transport"
		
		if self.teq_engine.get_transport_source() == teq.transport_source.INTERNAL:
			json_object["transport-source"] = "internal"
		
		tracks_json_object = []
		for n in range(self.teq_engine.number_of_tracks()):
			track_type_name = ""
			if self.teq_engine.track_type(n) == teq.track_type.MIDI:
				track_type_name = "MIDI"
			if self.teq_engine.track_type(n) == teq.track_type.CV:
				track_type_name = "CV"
			if self.teq_engine.track_type(n) == teq.track_type.CONTROL:
				track_type_name = "CONTROL"
			tracks_json_object.append({ "name": self.teq_engine.track_name(n), "type": track_type_name})
			
		json_object["tracks"] = tracks_json_object
		
		patterns_json_object = []
		for n in range(self.teq_engine.number_of_patterns()):
			pattern_json_object = []
			pattern = self.teq_engine.get_pattern(n)
			pattern_json_object.append(pattern.name)
			pattern_json_object.append(pattern.length())
			for m in range(self.teq_engine.number_of_tracks()):
				track_json_object = []
				for tick in range(pattern.length()):
					if self.teq_engine.track_type(m) == teq.track_type.MIDI:
						event = pattern.get_midi_event(m, tick)
						if event.type == teq.midi_event_type.ON:
							track_json_object.append([tick, "ON", event.value1, event.value2])
						if event.type == teq.midi_event_type.OFF:
							track_json_object.append([tick, "OFF", event.value1, event.value2])
						if event.type == teq.midi_event_type.CC:
							track_json_object.append([tick, "CC", event.value1, event.value2])
							
					if self.teq_engine.track_type(m) == teq.track_type.CONTROL:
						event = pattern.get_control_event(m, tick)
						if event.type == teq.control_event_type.GLOBAL_TEMPO:
							track_json_object.append([tick, "GLOBAL_TEMPO", event.value])
						if event.type == teq.control_event_type.RELATIVE_TEMPO:
							track_json_object.append([tick, "RELATIVE_TEMPO", event.value])
							
					if self.teq_engine.track_type(m) == teq.track_type.CV:
						event = pattern.get_cv_event(m, tick)
						if event.type == teq.cv_event_type.CONSTANT:
							track_json_object.append([tick, "CONSTANT", event.value1, event.value2])
						if event.type == teq.cv_event_type.INTERVAL:
							track_json_object.append([tick, "INTERVAL", event.value1, event.value2])
							
				pattern_json_object.append(track_json_object)
			patterns_json_object.append(pattern_json_object)
		
		json_object["patterns"] = patterns_json_object
		
		with open(self.filename, "w") as textfile:
			textfile.write(json.dumps(json_object, indent=4, separators=(',', ': ')))
