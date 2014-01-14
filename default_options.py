# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song [not implemented yet]
options = {
	# The color palette (see urwid documentation for color
	# codes,  etc.)
	"palette": [
		(None,  "dark gray",  "black"), 
		("weak",  "light gray",  "black"), 
		("medium", "white", "black"),
		("strong",  "light gray",  "dark gray"), 
		("stronger", "white", "dark gray"),
		("mega",  "black",  "white"),
		("editing", "black", "dark red"),
		("midi-event", "white", "dark green"),
		("control-event", "black", "dark red"),
		("cv-event", "black", "dark blue"),
		("transport-stopped", "light gray", "black"),
		("transport-playing", "dark green", "black"),
		("note-base", "black", "light gray"),
		("menu", "black", "white")
	], 

	# The names for the notes. Note that
	# each string is TWO chars long
	"note_names": [
		"C ",  "Db",  "D ", "Eb", 
		"E ",  "F ",  "Gb",  "G ",  
		"Ab",  "A ",  "Bb",  "B "
	],
	
	"transport_indicator_stopped": "||",
	"transport_indicator_playing": ">>",
	
	"edit_mode_indicator_enabled": "EDIT",
	"edit_mode_indicator_disabled": "    ",
	
	# The parameter x will be bound to an instance of
	# the class teqqer.main.
	"global_keys": [
		["N", "decrease the edit step by one", lambda x: x.change_edit_step(-1)],
		["M", "increase the edit step by one", lambda x: x.change_edit_step(1)],

		["esc", "toggle the edit mode", lambda x: x.toggle_edit_mode()],
		
		[" ", "toggle playback (start/stop)", lambda x: x.toggle_playback()],
		
		["up", "move one event up", lambda x: x.change_cursor_tick(-1)],
		["down", "move one event down", lambda x: x.change_cursor_tick(1)],
		
		["ctrl up", "move one edit step up", lambda x: x.change_cursor_tick(-x.options["edit_step"])],
		["ctrl down", "move one edit step down", lambda x: x.change_cursor_tick(x.options["edit_step"])],
		
		["shift tab", "move to previous track", lambda x: x.change_cursor_track(-1)],
		["tab", "move to next track", lambda x: x.change_cursor_track(1)],
		
		["page up", "move to previous pattern", lambda x: x.change_cursor_pattern(-1)],
		["page down", "move to next pattern", lambda x: x.change_cursor_pattern(1)],

		["delete", "delete an event", lambda x: x.delete_event()],
		
		["ctrl u", "undo", lambda x: x.undo()],
		["ctrl r", "undo", lambda x: x.redo()],
		
		[">", "increase global tempo", lambda x: x.change_tempo(1.0/8.0)],
		["<", "decrease global tempo", lambda x: x.change_tempo(-1.0/8.0)],

		["home", "move one event up", lambda x: x.move_to_pattern_top()],
		["end", "move one event down", lambda x: x.move_to_pattern_end()],
	],
	
	"midi_track_keys": [
		["ctrl page up", "increase base note by an octave", lambda x: x.change_note_edit_base(12)],
		["ctrl page down", "decrease base note by an octave", lambda x: x.change_note_edit_base(-12)],
		
		["meta page up", "increase base note by a semitone", lambda x: x.change_note_edit_base(1)],
		["meta page down", "decrease base note by a semitone", lambda x: x.change_note_edit_base(-1)]		
	],

	# The numbers are relative to the C of the current octave. This layout
	# needs to be changed for non US keyboards.
	"note_keys": [
		# C to E lower octave
		['z', 0], ['s', 1], ['x', 2], ['d', 3], ['c', 4],
		# F to B lower octave
		['v', 5], ['g', 6], ['b', 7], ['h', 8], ['n', 9], ['j', 10], ['m', 11], 
		# C to E lower octave plus one
		[',', 12], ['l', 13], ['.', 14], [';', 15], ['/', 16],
		# C to E upper octave
		['q', 12], ['2', 13], ['w', 14], ['3', 15], ['e', 16],
		# F to B upper octave
		['r', 17], ['5', 18], ['t', 19], ['6', 20], ['y', 21], ['7', 22], ['u', 23],
		# C to E upper octave plus one
		['i', 24], ['9', 25], ['o', 26], ['0', 27], ['p',  28],
		# F to G upper octave plus one
		['[', 29], ['=', 30], [']', 31]
	],
	

	"menu_exit_key": "esc",
	
	# Aach submenu gets an additional entry: exit_menu_key, "exit menu".
	# Also each action without a submenu is modified to exit the menu after
	# performing it.
	"menu": [
		["file", "ctrl f", lambda x: x.change_menu(x.current_menu[0][3]), [
			["save", "s", lambda x: x.save(), []],
			["quit", "q", lambda x: x.quit(), []]
		]],
		["properties", "ctrl p", lambda x: x.change_menu(x.current_menu[1][3]), [
			["track", "t", lambda x: x.change_menu(x.current_menu[0][3]), [
				["add track", "a", lambda x: x.change_menu(x.current_menu[0][3]), [
					["midi", "m", lambda x: x.add_midi_track(), []],
					["control", "c", lambda x: x.add_control_track(), []],
					["cv", "v", lambda x: x.add_cv_track(), []],
				]],
				["rename track", "n", lambda x: x.rename_track(), []],
				["remove track", "r", lambda x: x.remove_track(), []]
			]],
			["pattern", "p", lambda x: x.change_menu(x.current_menu[1][3]), [
				["add pattern", "a", lambda x: x.remove_track(), []],
				["set pattern length", "l", lambda x: x.remove_track(), []],
				["remove pattern", "r", lambda x: x.remove_track(), []]
			]]
		]],
		["help", "f1", lambda x: x.change_menu(x.current_menu[2][3]), [
			["about", "a", lambda x: x._emit('popup_about'), []],
			["license", "l", lambda x:x._emit('popup_license'), []],
			["help", "f1", lambda x: x._emit('popup_help'), []]
		]]
	],
	
	# At what fraction of the screen to display the edit cursor
	"center_line_fraction": 0.3,  
	
	# Highlight every highlight_row'th row
	"highlighted_rows": 4, 
	
	# The number of digits used for displaying cv values (integer and fractional part)
	"cv_fraction_precision": 3, 
	"cv_integer_precision": 1, 
	
	# The number of digits used for displaying control values (integer and fractional part)
	"control_fraction_precision": 3, 
	"control_integer_precision": 1, 
	
	"column_separator": " | ", 
	
	# Whether the cursor follows transport 
	"follow_transport": True, 
	
	# Whether to allow some mouse interaction to move the cursor around,  etc..
	"mouse_interaction": True, 
	
	# Reduce this time to make the UI more smooth at the expense of cpu power
	"ui_update_interval": 0.1, 
	
	"note_edit_base": 48,
	"note_edit_velocity": 127,
	
	"note_off_key": '`',
	
	# These can be either "pattern" or "song"
	"cursor_wrap_mode": "song", 
	
	# How many ticks to skip down after editing an event
	"edit_step": 4, 
	
	# What key to press with the cursor keys to select stuff
	"selection_modifier": "meta"
}