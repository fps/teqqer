 
def get_help_text(options):
	text = []
	text.append(u"""Press esc to leave this screen.

# The Basics

Teqqer is a tracker style midi sequencer. 

Tracks are layed out horizontally. Tracks can have one of three types:

* MIDI
* CV
* Control

Events are presented such that time flows from the top of the screen to the bottom.I.e. musical data is arranged in columns (which we will also call "sequences").

Sequences are arranged in patterns. All sequences in a pattern have the same length. 

All patterns share the same number of sequences and also their types (being that of their corresponding tracks). 

# Track Types

## MIDI Tracks

MIDI tracks can hold note-on, explicit note-off and CC events. Every MIDI track has an associated jack midi output port which is used to send the midi events. See the midi track key bindings below for help on how to edit events from the keyboard. 

## CV Tracks

CV tracks produce their output on a jack audio port. This can be used to e.g. automate parameters in instruments that expose control ports via jack audio ports. Every CV track has an associated jack audio output port. See the cv track key bindings below for help on how to edit events from the keyboard. 

## Control Tracks

Control tracks can be used to control the song playback. Event types include setting the global tempo or the relative tempo. Control tracks have no associated output ports. See the control track key bindings below for help on how to edit events from the keyboard. 

# The Keyboard

The primary means of editing data is by using the computer's keyboard. Most of the keyboard is used up for this purpose.

Here's a list of the key global key bindings (note that uppercase characters imply pressing shift):

""")
	
	for item in options["global_keys"]:
		text.append(item[0] + ": " + item[1] + "\n")

	text.append("""
The key bindings for midi tracks:

""")
	
	for item in options["midi_track_keys"]:
		text.append(item[0] + ": " + item[1] + "\n")


	text.append("""
To enter a note press on of the following keys (the numbers indicate the interval (in semitones) above the note_edit_base.:

""")
	
	text.append("""
To enter a note press on of the following keys (the numbers indicate the interval (in semitones) above the note_edit_base.:

""")
	
	for k in options["note_keys"]:
		text.append(k[0] + ": " + str(k[1]) + " ")
		
	text.append("""
The key bindings for control tracks:

""")
	
	for item in options["control_track_keys"]:
		text.append(item[0] + ": " + item[1] + "\n")

	text.append("""
The key bindings for cv tracks:

""")
	
	for item in options["cv_track_keys"]:
		text.append(item[0] + ": " + item[1] + "\n")


	return "".join(text)

