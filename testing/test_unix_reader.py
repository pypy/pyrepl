from __future__ import unicode_literals
from pyrepl.unix_eventqueue import EncodedQueue

from pyrepl import curses


def test_simple():
    q = EncodedQueue({}, 'utf-8')

    a = u'\u1234'
    b = a.encode('utf-8')
    for c in b:
        q.push(c)

    event = q.get()
    assert q.get() is None

