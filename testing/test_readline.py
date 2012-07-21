from pyrepl.readline import _ReadlineWrapper
import os, pty

def test_raw_input():
    readline_wrapper = _ReadlineWrapper()
    master, slave = pty.openpty()
    readline_wrapper.f_in = slave
    os.write(master, 'input\n')
    result = readline_wrapper.raw_input('prompt:')
    assert result == 'input'
    # A bytes string on python2, a unicode string on python3.
    assert isinstance(result, str)

