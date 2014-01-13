# teqqer - a simple midi tracker

An ncurses/terminal based midi and CV signal tracker/sequencer.

# TODOs

This project is not in a usable state yet. Here's some of the key 
TODOs (those done are marked [check]):

* Midi note insertion, deletion [check]
* Undo [check]
* Redo [check 50%]
* Main view [check 50%]
* Menu infrastructure [check]
* Input handling infrastructure [check]
* Changing midi event parameters for editing (base octave, velocity) [check]
* Song saving/loading
* Selection of sequence data
* Copy and paste for selection
* Copy and paste for patterns
* Muting patterns/sequences infrastructure
* Muting patterns/sequences via UI
* jack transport 
* Editing of control and cv events
* Loop support infrastructure [check]
* Editing loop start/end
* Display loop range
* Loading options overridden by the user

# Requirements

* libteq and its python bindings - submodule, see below.
* urwid (e.g. python-urwid on ubuntu 13.130)

# Building

First initialize the teq submodule:

<pre>
git submodule init
git submodule update
</pre>

Then you can build teq:

<pre>
cd teq
mkdir bld
cd bld
cmake ..
make
cd ../..
</pre>

# Running

Run teqqer from the root of the source tree with the 
provided script <code>teqqer</code>:

<pre>
./teqqer foo.teq
</pre>

# Installation

Not yet..

# Author

Florian Paul Schmidt (fps.io)

