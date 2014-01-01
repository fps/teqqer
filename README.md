# teqqer - a simple midi tracker

An ncurses/terminal based midi and CV signal tracker/sequencer.

# Requirements

* libteq and its python bindings
* urwid

# Hacking

## The Application States

### Main

This is the state that the application enters once it was started. This state has its own state machine for handling the menu state.

#### Menu 

The menu is a hierarchical state machine. There is a root state that represents the "entry point" into the menu.

##### Root

### Help

This state shows the help text and returns to Main when pressing esc.

### File Open

This state presents a dialog to select a file for opening.

### File Save

This state presents a dialog to select a filename for writing.

# Author

Florian Paul Schmidt (fps.io)

