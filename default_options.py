# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song [not implemented yet]
options = {
	# The color palette (see urwid documentation for color
	# codes,  etc.)
	"palette": [
		(None,  "dark gray",  "black"), 
		
		("help-text-default", "white", "black"),

		("transport-indicator-stopped", "light gray", "black"),
		("transport-indicator-playing", "dark green", "black"),

		("header-default", "white", "dark gray"),
		("header-editing", "white", "dark red"),
		
		("track-name-highlight", "black", "light gray"),

		("footer-default", "white", "dark gray"),
		("footer-editing", "white", "dark gray"),
		
		("edit-mode-indicator", "black", "light gray"),

		("menu-entry-default", "black", "white"),
		("menu-entry-exit-menu", "light gray", "dark gray"),
		
		("note-edit-base", "black", "light gray"),
		("cc-edit-base", "black", "light gray"),
		
		("song-properties", "black", "light gray"),
		
		("pattern-list-entry-default", "light gray", "black"),
		
		("cursor-row-highlight", "white", "dark gray"),
		
		("track-events-highlight", "white", "black"),
		
		("loop-range-indicator", "black", "light gray"),
		
		("event-default", "dark gray", "black"),
		("event-highlight", "light gray", "black"),
		("event-selected", "black", "white"),
		
		("note-on-event-default", "white", "dark green"),
		("note-on-event-selected", "dark green", "white"),
		
		("note-off-event-default", "white", "dark green"),
		("note-off-event-selected", "dark green", "white"),
		
		("cc-event-default", "white", "dark green"),
		("cc-event-selected", "dark green", "white"),
		
		("line-entry", "black", "yellow"),
		
		("loop-indicator-enabled", "black", "light gray"),
		("loop-indicator-disabled", "black", "dark gray"),

		("follow-transport-indicator-enabled", "black", "light gray"),
		("follow-transport-indicator-disabled", "black", "dark gray")
	], 

	# The names for the notes. Note that
	# each string is TWO chars long
	"note_names": [
		"C ",  "Db",  "D ", "Eb", 
		"E ",  "F ",  "Gb",  "G ",  
		"Ab",  "A ",  "Bb",  "B "
	],

	"loop_indicator_enabled": "L",
	"loop_indicator_disabled": " ",
	
	"transport_indicator_stopped": "||",
	"transport_indicator_playing": ">>",
	
	"edit_mode_indicator_enabled": "E",
	"edit_mode_indicator_disabled": "V",
	
	"follow_transport_indicator_enabled": "F",
	"follow_transport_indicator_disabled": " ",

	"loop_range_indicator_events": "[",
	"loop_range_indicator_patterns": "]",
	
	# The parameter x will be bound to an instance of
	# the class teqqer.main.
	"global_keys": [
		["N", "decrease the edit step by one", lambda x: x.change_edit_step(-1)],
		["M", "increase the edit step by one", lambda x: x.change_edit_step(1)],
		
		["f1", "set edit step to 1", lambda x: x.set_edit_step(1)],
		["f2", "set edit step to 2", lambda x: x.set_edit_step(2)],
		["f3", "set edit step to 3", lambda x: x.set_edit_step(3)],
		["f4", "set edit step to 4", lambda x: x.set_edit_step(4)],
		["f5", "set edit step to 5", lambda x: x.set_edit_step(5)],
		["f6", "set edit step to 6", lambda x: x.set_edit_step(6)],
		["f7", "set edit step to 7", lambda x: x.set_edit_step(7)],
		["f8", "set edit step to 8", lambda x: x.set_edit_step(8)],
		["f9", "set edit step to 9", lambda x: x.set_edit_step(9)],
		["f10", "set edit step to 10", lambda x: x.set_edit_step(10)],
		["f11", "set edit step to 11", lambda x: x.set_edit_step(11)],
		["f12", "set edit step to 12", lambda x: x.set_edit_step(12)],

		["esc", "toggle the edit mode", lambda x: x.toggle_edit_mode()],
		
		[" ", "toggle playback (start/stop)", lambda x: x.toggle_playback()],
		
		["meta up", "move one event up", lambda x: x.change_cursor_tick(-x.options["edit_step"])],
		["meta down", "move one event  down", lambda x: x.change_cursor_tick(x.options["edit_step"])],
		
		["left", "move to previous track", lambda x: x.change_cursor_track(-1)],
		["right", "move to next track", lambda x: x.change_cursor_track(1)],
		
		["up", "move one edit step up", lambda x: x.change_cursor_tick(-x.options["edit_step"])],
		["down", "move one edit step down", lambda x: x.change_cursor_tick(x.options["edit_step"])],
		
		["ctrl left", "extend selection to previous track", lambda x: x.extend_selection_track(-1)],
		["ctrl right", "extend selection to next track", lambda x: x.extend_selection_track(1)],
		
		["ctrl up", "extend selection one edit step up", lambda x: x.extend_selection_tick(-x.options["edit_step"])],
		["ctrl down", "extend selection one edit step down", lambda x: x.extend_selection_tick(x.options["edit_step"])],
		
		["page up", "move to previous pattern", lambda x: x.change_cursor_pattern(-1)],
		["page down", "move to next pattern", lambda x: x.change_cursor_pattern(1)],

		["delete", "delete an event", lambda x: x.delete_event()],
		
		["ctrl u", "undo", lambda x: x.undo()],
		["ctrl r", "redo", lambda x: x.redo()],
		
		[">", "increase global tempo", lambda x: x.change_tempo(1.0/8.0)],
		["<", "decrease global tempo", lambda x: x.change_tempo(-1.0/8.0)],

		["home", "move cursor to the top of the paatern", lambda x: x.move_to_pattern_top()],
		["end", "move cursor to the bottom of the paatern", lambda x: x.move_to_pattern_end()],
		
		["L", "set loop start", lambda x: x.set_loop_start()],
		[":", "set loop end", lambda x: x.set_loop_end()],
		["meta l", "toggle looping", lambda x: x.toggle_loop()],

		["meta f", "toggle follow transport", lambda x: x.toggle_follow_transport()]
	],
	
	"midi_track_keys": [
		["ctrl page up", "increase base note by an octave", lambda x: x.change_note_edit_base(12)],
		["ctrl page down", "decrease base note by an octave", lambda x: x.change_note_edit_base(-12)],
		
		["meta ctrl page up", "increase base note by a semitone", lambda x: x.change_note_edit_base(1)],
		["meta ctrl page down", "decrease base note by a semitone", lambda x: x.change_note_edit_base(-1)],

		["meta page up", "increase base velocity by one", lambda x: x.change_note_velocity(1)],
		["meta page down", "decrease base velocity by one", lambda x: x.change_note_velocity(-1)]
	],
	
	"global_mouse_events": [
		[("mouse press", 4), "move one event up", lambda x: x.change_cursor_tick(-1)],
		[("mouse press", 5), "move one event down", lambda x: x.change_cursor_tick(1)]
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
		["edit", "ctrl e", lambda x: x.change_menu(x.current_menu[1][3]), [
			["selection", "s", lambda x: x.selection(), []],
			["cut", "t", lambda x: x.cut(), []],
			["copy", "c", lambda x: x.copy(), []],
			["paste", "v", lambda x: x.paste(), []]
		]],
		["props", "ctrl p", lambda x: x.change_menu(x.current_menu[2][3]), [
			["track", "t", lambda x: x.change_menu(x.current_menu[0][3]), [
				["add", "a", lambda x: x.change_menu(x.current_menu[0][3]), [
					["midi", "m", lambda x: x.add_midi_track(), []],
					["control", "c", lambda x: x.add_control_track(), []],
					["cv", "v", lambda x: x.add_cv_track(), []],
				]],
				["name", "n", lambda x: x.rename_track(), []],
				["remove", "r", lambda x: x.remove_track(), []]
			]],
			["pattern", "p", lambda x: x.change_menu(x.current_menu[1][3]), [
				["add", "a", lambda x: x.add_pattern(), []],
				["set length", "l", lambda x: x.set_pattern_length(), []],
				["name", "n", lambda x: x.rename_pattern(), []],
				["remove", "r", lambda x: x.remove_pattern(), []]
			]]
		]],
		["tools", "ctrl t", lambda x: x.change_menu(x.current_menu[3][3]), [
			["eval", "e", lambda x: x.evaluate(), []]
		]],
		["help", "meta h", lambda x: x.change_menu(x.current_menu[4][3]), [
			["about", "a", lambda x: x._emit('popup_about'), []],
			["license", "l", lambda x:x._emit('popup_license'), []],
			["help", "h", lambda x: x._emit('popup_help'), []]
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
	
	"column_separator": "|", 
	
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