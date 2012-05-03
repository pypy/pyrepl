pyrepl
======

For ages now, I've been working on and off on a replacement for
readline for use from Python.  readline is undoubtedly great, but a
couple of things irritate me about it.  One is the inability to do
sane multi-line editing.  Have you ever typed something like::

  >>> for i in range(10):
  ...     for i in range(10):
  ...         print i*j

into a Python top-level?  Grr, that "i" on the second line should have
been a "j".  Wouldn't it be nice if you could just press "up" on your
keyboard and fix it?  This was one of the aims I kept in mind when
writing pyrepl (or pyrl as I used to call it, but that name's 
`taken <http://www.algonet.se/~jsjogren/oscar/cython/>`_).

Another irritation of readline is the GPL.  I'm not even nearly as
anti-GPL as some, but I don't want to have to GPL my program just so I
can use readline.

0.7 adds to the version that runs an a terminal an experimental
version that runs in a pygame surface.  A long term goal is
Mathematica-like notebooks, but that's a loong way off...

Anyway, after many months of intermittent toil I present:


Dependencies: Python 2.7 with the termios and curses modules built (I
don't really use curses, but I need the terminfo functions that live
in the curses module), or pygame installed (if you want to live on the
bleeding edge).

There are probably portability gremlins in some of the ioctl using
code.  Fixes gratefully received!

Features:
 * sane multi-line editing
 * history, with incremental search
 * completion, including displaying of available options
 * a fairly large subset of the readline emacs-mode key bindings (adding
   more is mostly just a matter of typing)
 * Deliberately liberal, Python-style license
 * a new python top-level that I really like; possibly my favourite
   feature I've yet added is the ability to type::

     ->> from __f

   and hit TAB to get::

     ->> from __future__

   then you type " import n" and hit tab again to get::

     ->> from __future__ import nested_scopes

   (this is very addictive!).

 * no global variables, so you can run two independent
   readers without having their histories interfering.
 * An experimental version that runs in a pygame surface.

pyrepl currently consists of four major classes::

  Reader - HistoricalReader - CompletingReader - PythonReader


There's also a **UnixConsole** class that handles the low-level
details.

Each of these lives in it's own file, and there are a bunch of support
files (including a C module that just provides a bit of a speed up -
building it is strictly optional).

IMHO, the best way to get a feel for how it works is to type::

  $ python pythoni

and just play around.  If you're used to readline's emacs-mode, you
should feel right at home.  One point that might confuse: because the
arrow keys are used to move up and down in the command currently being
edited, you need to use ^P and ^N to move through the history.

