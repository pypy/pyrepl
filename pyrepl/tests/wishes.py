from pyrepl.console import Event
from pyrepl.tests.infrastructure import ReaderTestCase, EA, run_testcase

# this test case should contain as-verbatim-as-possible versions of
# (applicable) feature requests

class WishesTestCase(ReaderTestCase):

    def test_quoted_insert_repeat(self):
        self.run_test([(('digit-arg', '3'),      ['']),
                       ( 'quoted-insert',        ['']),
                       (('self-insert', '\033'), ['^[^[^[']),
                       ( 'accept',               None)])

def test():
    run_testcase(WishesTestCase)

if __name__ == '__main__':
    test()
