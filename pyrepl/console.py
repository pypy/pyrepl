#   Copyright 2000-2003 Michael Hudson mwh@python.net
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

class Event:
    """An Event.  Attributes include:

      * name:
        the assigned name for this event (e.g. 'self-insert' or
        'prefix-arg')
      * chars:
        a string containing the characters read leading up to this
        event (e.g. 'a' or '\\x1b0').
      * _con_desc:
        a console specific description of what caused this event
        (used for producing 'M-foo not bound' messages)."""

    def __init__(self, name, chars='', con_desc=None):
        self.name = name
        self.chars = chars
        self._con_desc = con_desc

class Console:
    """Attributes:

    (keymap),
    (fd),
    screen,
    height,
    width,
    """
    
    def install_keymap(self, keymap):
        """Install a given keymap.

        keymap is a tuple of 2-element tuples; each small tuple is a
        pair (keyspec, event-name).  The format for keyspec is
        modelled on that used by readline (so read that manual for
        now!)."""
        pass

    def describe_event(self, event):
        """Return a description of an event, suitable for error messages.

        This method should..."""

    def refresh(self, screen, xy):
        pass

    def prepare(self):
        pass

    def restore(self):
        pass

    def move_cursor(self, x, y):
        pass

    def set_cursor_vis(self, vis):
        pass

    def getheightwidth(self):
        """Return (height, width) where height and width are the height
        and width of the terminal window in characters."""
        pass

    def get_event(self, block=1):
        """Return an Event instance.  Returns None if |block| is false
        and there is no event pending, otherwise waits for the
        completion of an event."""
        pass

    def beep(self):
        pass

    def clear(self):
        """Wipe the screen"""
        pass

    def finish(self):
        """Move the cursor to the end of the display and otherwise get
        ready for end.  XXX could be merged with restore?  Hmm."""
        pass

    def flushoutput(self):
        """Flush all output to the screen (assuming there's some
        buffering going on somewhere)"""
        pass

    def forgetinput(self):
        """Forget all pending, but not yet processed input."""
        pass

    def getpending(self):
        """Return the characters that have been typed but not yet
        processed."""
        pass

    def wait(self):
        """Wait for an event."""
        pass
