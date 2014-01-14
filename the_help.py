 
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

# The Keyboard

The primary means of editing note data is by using the computer's keyboard. Most of the keyboard is used up for this purpose.

Here's a list of the key global key bindings (note that uppercase characters imply pressing shift):

""")
	for item in options["global_keys"]:
		text.append(item[0] + ": " + item[1] + "\n")

	text.append("""
To enter a note press on of the following keys (the numbers indicate the interval (in semitones) above the note_edit_base.:

""")
	
	for k in options["note_keys"]:
		text.append(k[0] + ": " + str(k[1]) + " ")
		
	return "".join(text)

