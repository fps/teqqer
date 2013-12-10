import sys
import urwid
import teq

#import carla_backend

#carla_host = carla_backend.Host("/usr/local/lib/carla/libcarla_standalone.so")
#print (carla_host.get_engine_driver_count())

#teq_engine = teq.teq()
#teq_engine.insert_midi_track("midi0", 0)
#teq_engine.insert_midi_track("midi1", 1)
#teq_engine.insert_midi_track("midi2", 2)
#teq_engine.insert_pattern(0, 128)
#

help_text = u"""teqqer - a simple midi tracker

F1 - Show this help

ESC - Enter global menu | Leave global menu | Leave this help | 

TAB - Next sequence | Go to arrangement (if on last sequence)

SHIFT-TAB - Previous sequence | Go to arrangement (if on first equence)

UP/DOWN - Move up/down in arrangement | move to next/previous tick in sequence






































































LEFT/RIGHT - Move left/right in arrangement | Move from note to octave/from octave to note
"""

help_text_widget = urwid.Text(help_text)
help_text_fill = urwid.Filler(help_text_widget, 'top')
loop = urwid.MainLoop(help_text_fill)
loop.run()
