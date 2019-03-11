import os
import pty
import sys

import pytest
from pyrepl.readline import _ReadlineWrapper

from .infrastructure import sane_term

if sys.version_info < (3, ):
    bytes_type = str
    unicode_type = unicode  # noqa: F821
else:
    bytes_type = bytes
    unicode_type = str


@pytest.fixture
def readline_wrapper():
    master, slave = pty.openpty()
    return _ReadlineWrapper(slave, slave)


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


@pytest.mark.skipif("os.name != 'posix' or 'darwin' in sys.platform or "
                    "'freebsd' in sys.platform")
def test_raw_input():
    master, slave = pty.openpty()
    readline_wrapper = _ReadlineWrapper(slave, slave)
    os.write(master, b'input\n')

    with sane_term():
        result = readline_wrapper.raw_input('prompt:')
    assert result == 'input'
    assert isinstance(result, unicode_type)


def test_read_history_file(readline_wrapper, tmp_path):
    histfile = tmp_path / "history"
    histfile.touch()

    assert readline_wrapper.reader is None

    readline_wrapper.read_history_file(str(histfile))
    assert readline_wrapper.reader.history == []

    histfile.write_bytes(b"foo\nbar\n")
    readline_wrapper.read_history_file(str(histfile))
    assert readline_wrapper.reader.history == ["foo", "bar"]
