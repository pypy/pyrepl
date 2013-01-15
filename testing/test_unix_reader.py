from __future__ import unicode_literals
from pyrepl.unix_eventqueue import EncodedQueue

def test_simple():
    q = EncodedQueue({}, 'utf-8')

    a = u'\u1234'
    b = a.encode('utf-8')
    for c in b:
        q.push(c)

    event = q.get()
    assert q.get() is None
    assert event.data == a
    assert event.raw == b

