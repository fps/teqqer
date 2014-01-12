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
		("editing", "black", "light red")
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
	
	"column_separator": "  ", 
	
	# Whether the cursor follows transport 
	"follow_transport": True, 
	
	# Whether to allow some mouse interaction to move the cursor around,  etc..
	"mouse_interaction": True, 
	
	# Reduce this time to make the UI more smooth at the expense of cpu power
	"ui_update_interval": 0.1, 
	
	"note_edit_base": 48,
	"note_edit_velocity": 127,
	
	"increase_octave_key": "+",
	"decrease_octave_key": "-",
	
	"increase_velocity_key": "meta +",
	"decrease_velocity_key": "meta -",
	
	"increase_tempo_key": ">",
	"decrease_tempo_key": "<",
	
	"tempo_increment": 1.0/32,
	
	"increase_edit_step_key": "M",
	"decrease_edit_step_key": "N",
	
	# The numbers are relative to the C of the current octave. This layout
	# needs to be changed for non US keyboards.
	"note_keys": {
		'z': 0, 's': 1, 'x': 2, 'd': 3, 'c': 4, 'v': 5, 'g': 6,
		'b': 7, 'h': 8, 'n': 9, 'j': 10, 'm': 11, ',': 12,
		'l': 13, '.': 14, ';': 15, '/': 16, 'q': 12, '2': 13, 'w': 14,
		'3': 15, 'e': 16, 'r': 17, '5': 18, 't': 19, '6': 20,
		'y': 21, '7': 22, 'u': 23, 'i': 24, '9': 25,
		'o': 26, '0': 27, 'p':  28, '[': 29, '=': 30, ']': 31
	},
	
	"note_off_key": '`',
	
	"delete_event_key": "delete",
	
	"undo_key": "ctrl u",
	
	"cursor_up_key": "up",
	"cursor_down_key": "down", 
	"cursor_right_key": "right", 
	"cursor_left_key": "left", 
	
	# These can be either "pattern" or "song"
	"cursor_wrap_mode": "song", 
	
	# How many ticks to skip down after editing an event
	"edit_step": 4, 
	
	# What key to press with the cursor keys to select stuff
	"selection_modifier": "meta", 
	
	"next_pattern_key": "ctrl down", 
	"previous_pattern_key": "ctrl up", 
	
	"next_track_key": "ctrl right", 
	"previous_track_key": "ctrl left", 
	
	"edit_mode_key": "esc",
	
	"menu_exit_key": "esc", 
	
	"menu_yes_key": "y", 
	
	"root_menu_key": "esc", 
	"root_help_key": "f1", 
	"root_menu_play_stop_key": " ", 
	
	"menu_file_key": "f", 
	"menu_quit_key": "q", 
	"menu_song_key": "s", 
	
	"menu_file_save_key": "s", 
	
	"menu_song_add_midi_track_key": "m", 
	"menu_song_add_control_track_key": "c", 
	"menu_song_add_cv_track_key": "v",
	
	"note_names": [
		"C ",  "Db",  "D ", "Eb", 
		"E ",  "F ",  "Gb",  "G ",  
		"Ab",  "A ",  "Bb",  "B "
	]
}