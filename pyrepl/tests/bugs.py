from pyrepl.console import Event
from pyrepl.tests.infrastructure import ReaderTestCase, EA, run_testcase

# this test case should contain as-verbatim-as-possible versions of
# (applicable) bug reports

class BugsTestCase(ReaderTestCase):

    def test_transpose_at_start(self):
        self.run_test([( 'transpose', [EA, '']),
                       ( 'accept',    [''])])

def test():
    run_testcase(BugsTestCase)

if __name__ == '__main__':
    test()
