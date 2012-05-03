#   Copyright 2000-2004 Michael Hudson mwh@python.net
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

from setuptools import setup, Extension

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
    version = "0.8.4",
    author = "Michael Hudson-Doyle",
    author_email = "micahel@gmail.com",
    maintainer="Ronny Pfannschmidt",
    maintainer_email="ronny.pfannschmidt@gmx.de",
    url = "http://bitbucket.org/pypy/pyrepl/",
    license = "MIT X11 style",
    description = "A library for building flexible command line interfaces",
    platforms = ["unix", "linux"],
    packages = ["pyrepl" ],
    #ext_modules = [Extension("_pyrepl_utils", ["pyrepl_utilsmodule.c"])],
    scripts = ["pythoni", "pythoni1"],
    long_description = long_desc,
    )
