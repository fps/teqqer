# TEQQER - The Console MIDI Tracker for the Nerdy Music Hacker

An ncurses/terminal based midi and CV signal tracker/sequencer.

# Status

This project is in a semi-usable state. Check the issue tracker for open problems :D

# Requirements

* Check the requirements for teq: http://github.com/fps/teq
* Python 2 (Python 3 support is not planned)
* libteq and its python bindings - submodule, see below.
* urwid (e.g. python-urwid on ubuntu 13.10)

# Building

First initialize the teq submodule:

<pre>
git submodule init
git submodule update
</pre>

Then you can build teq:

<pre>
cd teq
mkdir build
cd build
cmake ..
make
cd ../..
</pre>

If you want to update the source tree of teqqer as well as the teq submodule, use the <code>git_pull.sh</code> script.

<pre>
./git_pull.sh
</pre>

# Running

Run teqqer from the root of the source tree with the provided script <code>teqqer</code>:

<pre>
./teqqer example.teq
</pre>

# Getting Help

The help menu is reachable in the app by pressing meta-h h (in the default configuration). On linux this amounts to pressing alt-h and then h again. This should display a help text with some general documentation and a list of the keybindings. 

# Installation

Not yet..

# Author

Florian Paul Schmidt (fps.io)

