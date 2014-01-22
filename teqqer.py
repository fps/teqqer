import sys
import urwid
import math
import random
import json
import traceback
import string

import teq
import pyteq

import default_options
import about
import license
import the_help
import history
import ui

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


class TextPopup(urwid.WidgetWrap):
	def __init__(self, text):
		text = urwid.Text(text)
		help_list_box = urwid.ListBox(urwid.SimpleListWalker([text]))

		self.__super.__init__(help_list_box)
		
		urwid.register_signal(TextPopup, 'close')

	def keypress(self, size, key):
		if key == 'esc':
			self._emit('close')
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

	def popup_help(self):
		self.popup_widget = TextPopup(("medium", the_help.get_help_text(self.the_original.options)))
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		self.open_pop_up()

	def popup_text(self, text):
		self.popup_widget = TextPopup(("medium", "Press esc to leave this screen\n\n" + text))
		urwid.connect_signal(self.popup_widget, 'close', lambda x: self.close_pop_up())
		self.popup_parameters = {'left':0, 'top':0, 'overlay_width':200, 'overlay_height':200}
		self.open_pop_up()

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
	

# TODO: merge in user options
options = default_options.options

teq_engine = teq.teq()

the_main = ui.main_window(teq_engine,  options, sys.argv[1])

def handle_alarm(main_loop,  the_main):
	the_main.get_state_info_and_update()
	main_loop.set_alarm_in(the_main.options["ui_update_interval"] - random.random() * 0.5 * the_main.options["ui_update_interval"],  handle_alarm,  the_main)



popup_launcher = PopUpLauncherThing(the_main)
loop = urwid.MainLoop(popup_launcher,  options["palette"], pop_ups=True)
loop.set_alarm_in(the_main.options["ui_update_interval"],  handle_alarm,  the_main)
loop.run()

teq_engine.deactivate()


