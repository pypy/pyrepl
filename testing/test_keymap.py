import pytest
from pyrepl.keymap import compile_keymap


@pytest.mark.skip('completely wrong')
def test_compile_keymap():
    k = compile_keymap({
        b'a': 'test',
        b'bc': 'test2',
    })

    assert k == {b'a': 'test', b'b': { b'c': 'test2'}}
