"""This is an alternative to python_reader which tries to emulate
the CPython prompt as closely as possible, with the exception of
allowing multiline input and multiline history entries.
"""

import sys
from pyrepl.readline import multiline_input


def run_multiline_interactive_console(mainmodule=None):
    import code
    if mainmodule is None:
        import __main__ as mainmodule
    console = code.InteractiveConsole(mainmodule.__dict__)

    def more_lines(unicodetext):
        # ooh, look at the hack:
        src = "#coding:utf-8\n"+unicodetext.encode('utf-8')
        try:
            code = console.compile(src, '<input>', 'single')
        except (OverflowError, SyntaxError, ValueError):
            return False
        else:
            return code is None

    while 1:
        try:
            ps1 = getattr(sys, 'ps1', '>>> ')
            ps2 = getattr(sys, 'ps2', '... ')
            try:
                statement = multiline_input(more_lines, ps1, ps2)
            except EOFError:
                break
            more = console.push(statement)
            assert not more
        except KeyboardInterrupt:
            console.write("\nKeyboardInterrupt\n")
            console.resetbuffer()
