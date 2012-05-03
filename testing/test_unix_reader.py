from pyrepl.unix_eventqueue import EncodedQueue

from pyrepl import curses


def test_simple():
    q = EncodedQueue({}, 'utf-8')

