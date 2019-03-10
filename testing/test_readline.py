import sys

import pytest

from .infrastructure import sane_term

if sys.version_info < (3, ):
    bytes_type = str
    unicode_type = unicode  # noqa: F821
else:
    bytes_type = bytes
    unicode_type = str


@pytest.mark.skipif("os.name != 'posix' or 'darwin' in sys.platform or "
                    "'freebsd' in sys.platform")
def test_raw_input():
    import os
    import pty
    from pyrepl.readline import _ReadlineWrapper

    master, slave = pty.openpty()
    readline_wrapper = _ReadlineWrapper(slave, slave)
    os.write(master, b'input\n')

    with sane_term():
        result = readline_wrapper.raw_input('prompt:')
    assert result == 'input'
    # A bytes string on python2, a unicode string on python3.
    assert isinstance(result, unicode_type)
