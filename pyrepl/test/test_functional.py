# some functional tests, to see if this is really working

import py
import sys

class TestTerminal(object):
    def _spawn(self, *args, **kwds):
        try:
            import pexpect
        except ImportError, e:
            py.test.skip(str(e))
        kwds.setdefault('timeout', 10)
        child = pexpect.spawn(*args, **kwds)
        child.logfile = sys.stdout
        return child

    def spawn(self, argv=[]):
        # avoid running start.py, cause it might contain
        # things like readline or rlcompleter(2) included
        child = self._spawn(sys.executable, ['-S'] + argv)
        child.sendline('from pyrepl.python_reader import main')
        child.sendline('main()')
        return child

    def test_basic(self):
        child = self.spawn()
        child.sendline('a = 3')
        child.sendline('a')
        child.expect('3')
        
