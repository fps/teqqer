import sys
import urwid
import random

import teq

import default_options
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

# TODO: merge in user options
options = default_options.options

teq_engine = teq.teq()

the_main = ui.main_window(teq_engine,  options, sys.argv[1])

def handle_alarm(main_loop, the_main):
	the_main.get_state_info_and_update()
	main_loop.set_alarm_in(the_main.options["ui_update_interval"] - random.random() * 0.5 * the_main.options["ui_update_interval"],  handle_alarm,  the_main)

popup_launcher = ui.PopUpLauncherThing(the_main)
loop = urwid.MainLoop(popup_launcher,  options["palette"], pop_ups=True)
loop.set_alarm_in(the_main.options["ui_update_interval"],  handle_alarm,  the_main)
loop.run()

teq_engine.deactivate()


