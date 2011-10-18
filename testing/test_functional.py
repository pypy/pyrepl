#   Copyright 2000-2007 Michael Hudson-Doyle <micahel@gmail.com>
#                       Maciek Fijalkowski
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# some functional tests, to see if this is really working

import pytest
import sys

def pytest_funcarg__child(request):
    pexpect = pytest.importorskip('pexpect')
    child = pexpect.spawn(sys.executable, ['-S'], timeout=10)
    child.logfile = sys.stdout
    child.sendline('from pyrepl.python_reader import main')
    child.sendline('main()')
    return child

def test_basic(child):
    child.sendline('a = 3')
    child.sendline('a')
    child.expect('3')

