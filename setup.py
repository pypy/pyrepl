from distutils.core import setup, Extension

long_desc = """\
pyrepl is a Python library, inspired by readline, for building flexible
command line interfaces, featuring:
 * sane multi-line editing
 * history, with incremental search
 * completion, including displaying of available options
 * a fairly large subset of the readline emacs-mode keybindings
 * a liberal, Python-style, license
 * a new python top-level."""


setup(
    name = "pyrepl",
    version = "0.7.2",
    author = "Michael Hudson",
    author_email = "mwh@python.net",
    url = "http://starship.python.net/crew/mwh/hacks/pyrepl.html",
    licence = "MIT X11 style",
    description = "A library for building flexible command line interfaces",
    platforms = ["unix", "linux"],

    packages = ["pyrepl"],
    ext_modules = [Extension("_pyrepl_utils", ["pyrepl_utilsmodule.c"])],
    scripts = ["pythoni"],
    long_description = long_desc,
    )
