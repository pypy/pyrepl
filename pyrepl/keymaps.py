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

emacs_keymap = tuple(
    [('\\C-a', 'beginning-of-line'),
     ('\\C-b', 'left'),
     ('\\C-c', 'interrupt'),
     ('\\C-d', 'delete'),
     ('\\C-e', 'end-of-line'),
     ('\\C-f', 'right'),
     ('\\C-g', 'cancel'),
     ('\\C-h', 'backspace'),
     ('\\C-j', 'accept'),
     ('\\C-k', 'kill-line'),
     ('\\C-l', 'clear-screen'),
     ('\\C-m', 'accept'),
     ('\\C-q', 'quoted-insert'),
     ('\\C-t', 'transpose-characters'),
     ('\\C-u', 'unix-line-discard'),
     ('\\C-v', 'quoted-insert'),
     ('\\C-w', 'unix-word-rubout'),
     ('\\C-y', 'yank'),
     ('\\C-z', 'suspend'),
     
     ('\\M-b', 'backward-word'),
     ('\\M-c', 'capitalize-word'),
     ('\\M-d', 'kill-word'),
     ('\\M-f', 'forward-word'),
     ('\\M-l', 'downcase-word'),
     ('\\M-t', 'transpose-words'),
     ('\\M-u', 'upcase-word'),
     ('\\M-y', 'yank-pop'),
     ('\\M--', 'digit-arg'),
     ('\\M-0', 'digit-arg'),
     ('\\M-1', 'digit-arg'),
     ('\\M-2', 'digit-arg'),
     ('\\M-3', 'digit-arg'),
     ('\\M-4', 'digit-arg'),
     ('\\M-5', 'digit-arg'),
     ('\\M-6', 'digit-arg'),
     ('\\M-7', 'digit-arg'),
     ('\\M-8', 'digit-arg'),
     ('\\M-9', 'digit-arg'),
     ('\\M-\\n', 'self-insert'),
     ('\\\\', 'self-insert')] + \
    [(c, 'self-insert')
     for c in map(chr, range(32, 127)) if c <> '\\'] + \
    [(c, 'self-insert')
     for c in map(chr, range(128, 256)) if c.isalpha()] + \
    [('up', 'up'),
     ('down', 'down'),
     ('left', 'left'),
     ('right', 'right'),
     ('insert', 'quoted-insert'),
     ('delete', 'delete'),
     ('backspace', 'backspace'),
     ('\\M-backspace', 'backward-kill-word'),
     ('end', 'end'),
     ('home', 'home'),
     ('\\EOF', 'end'),  # the entries in the terminfo database for xterms
     ('\\EOH', 'home'), # seem to be wrong.  this is a less than ideal
                        # workaround
     ])

vi_insert_keymap = tuple(
    [(c, 'self-insert')
     for c in map(chr, range(32, 127)) if c <> '\\'] + \
    [(c, 'self-insert')
     for c in map(chr, range(128, 256)) if c.isalpha()] + \
    [('\\C-d', 'delete'),
     ('backspace', 'backspace'),
     ('')])

del c # from the listcomps
