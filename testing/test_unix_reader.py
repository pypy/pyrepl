from pyrepl.unix_eventqueue import EventQueue

from pyrepl import curses


@pytest.mark.xfail(run=False, reason='wtf segfault')
def test_simple():
    q = EventQueue(0, 'utf-8')

