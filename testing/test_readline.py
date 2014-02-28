from pyrepl.readline import _ReadlineWrapper
import os
import pty
import sys

if sys.version_info < (3, ):
    bytes_type = str
    unicode_type = unicode
else:
    bytes_type = bytes
    unicode_type = str


def test_readline():
    master, slave = pty.openpty()
    readline_wrapper = _ReadlineWrapper(slave, slave)
    os.write(master, b'input\n')

    result = readline_wrapper.get_reader().readline()
    assert result == b'input'
    assert isinstance(result, bytes_type)


def test_readline_returns_unicode():
    master, slave = pty.openpty()
    readline_wrapper = _ReadlineWrapper(slave, slave)
    os.write(master, b'input\n')

    result = readline_wrapper.get_reader().readline(returns_unicode=True)
    assert result == 'input'
    assert isinstance(result, unicode_type)


def test_raw_input():
    master, slave = pty.openpty()
    readline_wrapper = _ReadlineWrapper(slave, slave)
    os.write(master, b'input\n')

    result = readline_wrapper.raw_input('prompt:')
    assert result == b'input'
    assert isinstance(result, bytes_type)
