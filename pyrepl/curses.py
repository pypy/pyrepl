
# Some try-import logic for two purposes: avoiding to bring in the whole
# pure Python curses package if possible; and, in _curses is not actually
# present, falling back to _minimal_curses (which is either a ctypes-based
# pure Python module or a PyPy built-in module).
try:
    import _curses
except ImportError:
    try:
        import _minimal_curses as _curses
    except ImportError:
        # Who knows, maybe some environment has "curses" but not "_curses".
        # If not, at least the following import gives a clean ImportError.
        import _curses

setupterm = _curses.setupterm
tigetstr = _curses.tigetstr
tparm = _curses.tparm
