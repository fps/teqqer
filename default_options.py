# These are the default options that can be overriden by a user's config
# file and/or specific settings in a song [not implemented yet]
default_options = {
	# The color palette (see urwid documentation for color
	# codes,  etc.)
	"palette": [
		(None,  "dark gray",  "black"), 
		("weak",  "light gray",  "black"), 
		("strong",  "light gray",  "dark gray"), 
		("mega",  "black",  "white")
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
	
	# The numbers are relative to the C of the current octave. This layout
	# needs to be changed for non US keyboards.
	"note_keys": {'z': 0, 's': 1, 'x': 2, 'd': 3, 'c': 4, 'v': 5, 'g': 6, 'b': 7, 'h': 8, 'n': 9, 'j': 10, 'm': 11, ': ': 12, 'l': 13, '.': 14, '/': 15, 'q': 12, '2': 13, 'w': 14, '3': 15, 'e': 16, 'r': 17, '5': 18, 't': 19, '6': 20, 'y': 21, '7': 22, 'u': 23, '8': 24, 'i': 25, '9': 26, 'o': 27, 'p': 28, '[':  29}, 
	
	"cursor_up_key": "up", 
	"cursor_down_key": "down", 
	"cursor_right_key": "right", 
	"cursor_left_key": "left", 
	
	# These can be either "pattern" or "song"
	"cursor_wrap_mode": "song", 
	
	# What key to press with the cursor keys to select stuff
	"selection_modifier": "meta", 
	
	"next_pattern_key": "ctrl down", 
	"previous_pattern_key": "ctrl up", 
	
	"next_track_key": "ctrl right", 
	"previous_track_key": "ctrl left", 
	
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
	"menu_song_add_cv_track_key": "v"
}