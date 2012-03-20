#!/usr/local/bin/python

#   Copyright 2000-2003 Michael Hudson mwh@python.net
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

import os, time, sys
import py

header_template = """\
#   Copyright 2000-%(lastyear)s Michael Hudson-Doyle <micahel@gmail.com>%(others)s
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
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\
"""

author_template = "\n#%s%%s"%(' '*(header_template.index("Michael")+1),)



author_map = {
    u'mwh': None,
    u'micahel': None,
    u'Michael Hudson <michael.hudson@linaro.org>': None,
    u'arigo': u"Armin Rigo",
    u'antocuni': u'Antonio Cuni',
    u'anto': u'Antonio Cuni',
    u'bob': u'Bob Ippolito',
    u'fijal': u'Maciek Fijalkowski',
    u'agaynor': u'Alex Gaynor',
    u'hpk': u'Holger Krekel',
    u'Ronny': u'Ronny Pfannschmidt',
    u'amauryfa': u"Amaury Forgeot d'Arc",
    }


def author_revs(path):
    proc = py.std.subprocess.Popen([
        'hg','log', str(path),
        '--template', '{author|user} {date}\n',
        '-r', 'not keyword("encopyright")',
    ], stdout=py.std.subprocess.PIPE)
    output, _ = proc.communicate()
    lines = output.splitlines()
    for line in lines:
        try:
            name, date = line.split(None, 1)
        except ValueError:
            pass
        else:
            if '-' in date:
                date = date.split('-')[0]
            yield name, float(date)


def process(path):
    ilines = path.readlines()
    revs = sorted(author_revs(path), key=lambda x:x[1])
    modified_year = time.gmtime(revs[-1][1])[0]
    if not modified_year:
        print 'E: no sensible modified_year found for', path
        modified_year = time.gmtime(time.time())[0]
    extra_authors = []
    authors = set(rev[0] for rev in revs)
    for a in authors:
        if a not in author_map:
            print 'E: need real name for', a
        ea = author_map.get(a)
        if ea:
            extra_authors.append(ea)
    extra_authors.sort()
    header = header_template % {
        'lastyear': modified_year,
        'others': ''.join([author_template%ea for ea in extra_authors])
    }
    header_lines = header.splitlines()
    prelines = []
    old_copyright = []

    if not ilines:
        print "W ignoring empty file", path
        return

    i = 0

    if ilines[0][:2] == '#!':
        prelines.append(ilines[0])
        i += 1
    
    while i < len(ilines) and not ilines[i].strip():
        prelines.append(ilines[i])
        i += 1

    while i < len(ilines) and ilines[i][:1] == '#':
        old_copyright.append(ilines[i])
        i += 1

    if abs(len(old_copyright) - len(header_lines)) < 2 + len(extra_authors):
        for x, y in zip(old_copyright, header_lines):
            if x[:-1] != y:
                print "C change needed in", path
                ofile = path.open("w")
                for l in prelines:
                    ofile.write(l)
                ofile.write(header + "\n")
                for l in ilines[i:]:
                    ofile.write(l)
                ofile.close()
                break
        else:
            print "M no change needed in", path
    else:
        print "A no (c) in", file
        with path.open("w") as ofile:
            for l in prelines:
                ofile.write(l)
            ofile.write(header + "\n\n")
            for l in ilines[len(prelines):]:
                ofile.write(l)


for thing in sys.argv[1:]:
    path = py.path.local(thing)
    if path.check(dir=1):
        for item in path.visit('*.py'):
            process(item)
    elif path.check(file=1, ext='py'):
        process(path)
