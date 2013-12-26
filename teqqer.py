import sys

if (len(sys.argv)!= 2):
	print("Usage: teqqer [filename]")
	sys.exit()

import urwid
import teq

#import carla_backend

#carla_host = carla_backend.Host("/usr/local/lib/carla/libcarla_standalone.so")
#print (carla_host.get_engine_driver_count())

teq_engine = teq.teq()
teq_engine.insert_midi_track("midi0", 0)
#teq_engine.insert_midi_track("midi1", 1)
#teq_engine.insert_midi_track("midi2", 2)
#teq_engine.insert_pattern(0, 128)
#

help_text = u"""teqqer - a simple midi tracker

Help:
b
  F1          - Show this help
  ESC         - Leave help and return to main screen
  UP/DOWN     - Scroll the help view
  PGUP/PGDOWN - Scroll the help view by a page

Navigating Menus:

  Menus are shown at the bottom of the screen. Press ESC to activate them. Menus 
  that have submenus are shown with a trailing ">" (e.g. "0 help>"). Items that
  do not have such a trailing ">" will be items that perform an action.

  ESC - Show the global menu | Leave the global menu 
  0-9 - Select a menu item | Select a submenu item 

Navigating the pattern and arrangement:

  TAB        - Next sequence | Go to arrangement (if on last sequence)
  SHIFT-TAB  - Previous sequence | Go to arrangement (if on first equence)
  UP/DOWN    - Move up/down in arrangement | move to next/previous tick in sequence
  LEFT/RIGHT - Move left/right in arrangement | Move from note to octave/from octave to note
"""

def help_input_handler(key):
	if key == "esc":
		raise urwid.ExitMainLoop()

help_text_widget = urwid.Text(help_text)
#help_text_fill = urwid.Filler(help_text_widget, 'top')
help_list_box = urwid.ListBox(urwid.SimpleListWalker([help_text_widget]))
loop = urwid.MainLoop(help_list_box, unhandled_input=help_input_handler)
loop.run()

header = urwid.Text(u"teqqer")
body = urwid.Filler(urwid.Text(u"00 00 c-4"), 'top')
footer = urwid.Text(u"0 help> 1 file> 2 song> 3 pattern> 4 sequence>")

frame = urwid.Frame(body, header, footer)
loop = urwid.MainLoop(frame)
loop.run()