#   Copyright 2000-2002 Michael Hudson mwh@python.net
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

"""
functions for parsing keyspecs

Support for turning keyspecs into appropriate sequences.

pyrepl uses it's own bastardized keyspec format, which is meant to be
a strict superset of readline's \"KEYSEQ\" format (which is to say
that if you can come up with a spec readline accepts that this
doesn't, you've found a bug and should tell me about it).

Note that this is the `\\C-o' style of readline keyspec, not the
`Control-o' sort.

A keyspec is a string representing a sequence of keypresses that can
be bound to a command.

All characters other than the backslash represent themselves.  In the
traditional manner, a backslash introduces a escape sequence.

The extension to readline is that the sequence \\<KEY> denotes the
sequence of charaters produced by hitting KEY.  This gets a bit messy
because the results of such depend on your terminal.  If your terminal's
terminfo entry doesn't describe KEY, trying to parse any keyspec
containing \\<KEY> will return None.

Examples:

`a'     - what you get when you hit the `a' key
`\\EOA'  - Escape - O - A (up, on my terminal)
`\\<UP>' - the up arrow key
`\\<up>' - ditto (keynames are case insensitive)
`\\C-o', `\\c-o'  - control-o
`\\M-.'  - meta-period
`\\E.'   - ditto (that's how meta works for pyrepl)
`\\<tab>', `\\<TAB>', `\\t', `\\011', '\\x09', '\\X09', '\\C-i', '\\C-I'
   - all of these are the tab character.  Can you think of any more?
"""

# this is where lisp-style special variables would be handy; then we
# could have a *keyset* hash-table or something.

# XXX it's actually possible to test this module, so it should have a
# XXX test suite.

from curses import ascii

_escapes = {
    '\\':'\\',
    "'":"'",
    '"':'"',
    'a':'\a',
    'b':'\h',
    'e':'\033',
    'f':'\f',
    'n':'\n',
    'r':'\r',
    't':'\t',
    'v':'\v'
    }

_keynames = [ # this is only here for doco purposes right now.
    'backspace',
    'delete',
    'down',
    'end',
    'enter',
    'escape',
    'f1',    'f2',    'f3',    'f4',    'f5',
    'f6',    'f7',    'f8',    'f9',    'f10',
    'f11',   'f12',   'f13',   'f14',   'f15',
    'f16',   'f17',   'f18',   'f19',   'f20',
    'home',
    'insert',
    'left',
    'pgdown',   'page down',
    'pgup',     'page up',
    'right',
    'space',
    'tab',
    'up',
    ]

class KeySpecError(Exception):
    pass

def _parse_key1(key, s, keyset):
    ctrl = 0
    meta = 0
    ret = ''
    while not ret and s < len(key):
        if key[s] == '\\':
            c = key[s+1].lower()
            if _escapes.has_key(c):
                ret = _escapes[c]
                s += 2
            elif c == "c":
                if key[s + 2] != '-':
                    raise KeySpecError, \
                              "\\C must be followed by `-' (char %d of %s)"%(
                        s + 2, repr(key))
                if ctrl:
                    raise KeySpecError, "doubled \\C- (char %d of %s)"%(
                        s + 1, repr(key))
                ctrl = 1
                s += 3
            elif c == "m":
                if key[s + 2] != '-':
                    raise KeySpecError, \
                              "\\M must be followed by `-' (char %d of %s)"%(
                        s + 2, repr(key))
                if meta:
                    raise KeySpecError, "doubled \\M- (char %d of %s)"%(
                        s + 1, repr(key))
                meta = 1
                s += 3
            elif c.isdigit():
                n = key[s+1:s+4]
                ret = chr(int(n, 8))
                s += 4
            elif c == 'x':
                n = key[s+2:s+4]
                ret = chr(int(n, 16))
                s += 4
            elif c == '<':
                t = key.find('>', s)
                if t == -1:
                    raise KeySpecError, \
                              "unterminated \\< starting at char %d of %s"%(
                        s + 1, repr(key))                        
                try:
                    ret = keyset[key[s+2:t].lower()]
                    s = t + 1
                except:
                    raise KeySpecError, \
                              "unrecognised keyname `%s' at char %d of %s"%(
                        key[s+2:t], s + 2, repr(key))
                if ret is None:
                    return None, s
            else:
                raise KeySpecError, \
                          "unknown backslash escape %s at char %d of %s"%(
                    `c`, s + 2, repr(key))
        else:
            ret = key[s]
            s += 1
    if meta:
        p = "\033"
    else:
        p = ""
    if ctrl:
        if len(ret) > 2:
            raise KeySpecError, "\\C- must be followed by a character"
        ret = ascii.ctrl(ret)
    return p + ret, s + len(p)

def parse_keys(key, keyset=None):
    if keyset is None:
        from pyrepl import unix_console
        keyset = unix_console.keyset()    
    s = 0
    r = []
    while s < len(key):
        k, s = _parse_key1(key, s, keyset)
        if k is None:
            return None
        r.append(k)
    return ''.join(r)

def _compile_keymap(keymap):
    r = {}
    for key, value in keymap.items():
        r.setdefault(key[0], {})[key[1:]] = value
    for key, value in r.items():
        if value.has_key(''):
            if len(value) <> 1:
                raise KeySpecError, \
                          "key definitions for %s clash"%(value.values(),)
            else:
                r[key] = value['']
        else:
            r[key] = _compile_keymap(value)
    return r

def compile_keymap(keymap, keyset=None):
    if keyset is None:
        from pyrepl import unix_console
        keyset = unix_console.keyset()    
    r = {}
    for key, value in keymap:
        k = parse_keys(key, keyset)
        if value is None and r.has_key(k):
            del r[k]
        if k is not None:
            r[k] = value
    return _compile_keymap(r)

def keyname(key, keyset=None):
    if keyset is None:
        from pyrepl import unix_console
        keyset = unix_console.keyset()
    longest_match = ''
    longest_match_name = ''
    for name, keyseq in keyset.items():
        if keyseq and key.startswith(keyseq) and \
               len(keyseq) > len(longest_match):
            longest_match = keyseq
            longest_match_name = name
    if len(longest_match) > 0:
        return longest_match_name, len(longest_match)
    else:
        return None, 0

_unescapes = {'\r':'\\r', '\n':'\\n', '\177':'^?'}

#for k,v in _escapes.items():
#    _unescapes[v] = k

def unparse_key(keyseq, keyset=None):
    if keyset is None:
        from pyrepl import unix_console
        keyset = unix_console.keyset()
    if not keyseq:
        return ''
    name, s = keyname(keyseq, keyset)
    if name:
        if name <> 'escape' or s == len(keyseq):
            return '\\<' + name + '>' + unparse_key(keyseq[s:], keyset)
        else:
            return '\\M-' + unparse_key(keyseq[1:], keyset)
    else:
        c = keyseq[0]
        r = keyseq[1:]
        if c == '\\':
            p = '\\\\'
        elif _unescapes.has_key(c):
            p = _unescapes[c]
        elif ord(c) < ord(' '):
            p = '\\C-%s'%(chr(ord(c)+96),)
        elif ord(' ') <= ord(c) <= ord('~'):
            p = c
        else:
            p = '\\%03o'%(ord(c),)
        return p + unparse_key(r, keyset)

def _unparse_keyf(keyseq, keyset=None):
    if keyset is None:
        from pyrepl import unix_console
        keyset = unix_console.keyset()
    if not keyseq:
        return []
    name, s = keyname(keyseq, keyset)
    if name:
        if name <> 'escape' or s == len(keyseq):
            return [name] + _unparse_keyf(keyseq[s:], keyset)
        else:
            rest = _unparse_keyf(keyseq[1:], keyset)
            return ['M-'+rest[0]] + rest[1:]
    else:
        c = keyseq[0]
        r = keyseq[1:]
        if c == '\\':
            p = '\\'
        elif _unescapes.has_key(c):
            p = _unescapes[c]
        elif ord(c) < ord(' '):
            p = 'C-%s'%(chr(ord(c)+96),)
        elif ord(' ') <= ord(c) <= ord('~'):
            p = c
        else:
            p = '\\%03o'%(ord(c),)
        return [p] + _unparse_keyf(r, keyset)

def unparse_keyf(keyseq, keyset=None):
    return " ".join(_unparse_keyf(keyseq, keyset))

