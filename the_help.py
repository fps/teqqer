 
def get_help_text(options):
	text = []
	text.append(u"""Press esc to leave this screen.

# The Basics

teqqer is a tracker style midi sequencer. 
Tracks are represented horizontally. Tracks can have one of 
three types:

* MIDI
* CV
* Control

Events are presented 
such that time flows from the top of the screen to the bottom.
I.e. musical data is arranged in columns (which we will also
call "sequences").

Sequences are arranged in patterns. All sequences in a pattern
have the same length. 

All patterns share the same number of sequences and also their 
types. 

# The Keyboard

The primary means of editing note data is by using the 
computer's keyboard. Most of the keyboard is used up for this
purpose.

To enter the editing mode press:

""")
	text.append("edit_mode_key: " + options["edit_mode_key"])
	
	text.append(u"""

To enter a note press on of the following keys (the numbers 
indicate the interval (in semitones) above the note_edit_base.:

""")
	
	for key in options["note_keys"]:
		text.append(key + ": " + str(options["note_keys"][key]) + " ")
		
	return "".join(text)

