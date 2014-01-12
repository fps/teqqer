# teqqer - a simple midi tracker

An ncurses/terminal based midi and CV signal tracker/sequencer.

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

