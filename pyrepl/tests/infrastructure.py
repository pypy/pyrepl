from pyrepl.reader import Reader
from pyrepl.console import Console, Event
import unittest
import sys

class EqualsAnything(object):
    def __eq__(self, other):
        return True
EA = EqualsAnything()

class TestConsole(Console):
    height = 24
    width = 80
    encoding = 'utf-8'

    def __init__(self, events, testcase, verbose=False):
        self.events = events
        self.next_screen = None
        self.verbose = verbose
        self.testcase = testcase

    def refresh(self, screen, xy):
        if self.next_screen is not None:
            self.testcase.assertEqual(
                screen, self.next_screen,
                "[ %s != %s after %r ]"%(screen, self.next_screen,
                                         self.last_event_name))

    def get_event(self, block=1):
        ev, sc = self.events.pop(0)
        self.next_screen = sc
        if not isinstance(ev, tuple):
            ev = (ev,)
        self.last_event_name = ev[0]
        if self.verbose:
            print "event", ev
        return Event(*ev)

class TestReader(Reader):
    def get_prompt(self, lineno, cursor_on_line):
        return ''
    def refresh(self):
        Reader.refresh(self)
        self.dirty = True

class ReaderTestCase(unittest.TestCase):
    def run_test(self, test_spec, reader_class=TestReader):
        # remember to finish your test_spec with 'accept' or similar!
        con = TestConsole(test_spec, self)
        reader = reader_class(con)
        reader.readline()

class BasicTestRunner:
    def run(self, test):
        result = unittest.TestResult()
        test(result)
        return result

def run_testcase(testclass):
    suite = unittest.makeSuite(testclass)
    runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
    result = runner.run(suite)
    
