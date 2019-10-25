import pytest


def test_eoferror():
    from pyrepl.unix_console import UnixConsole

    console = UnixConsole(f_in=99)
    with pytest.raises(
        EOFError,
        match="^could not prepare fd 99: .*Bad file descriptor"
    ):
        console.prepare()
