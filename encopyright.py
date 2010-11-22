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
import bzrlib.branch
import bzrlib.log

header_template = """\
#   Copyright 2000-%s Michael Hudson-Doyle <micahel@gmail.com>%s
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

branch, path = bzrlib.branch.Branch.open_containing(sys.argv[0])
rev_tree = branch.basis_tree()
branch.lock_read()

def process(thing):
    if os.path.isdir(thing):
        for subthing in os.listdir(thing):
            process(os.path.join(thing, subthing))
    elif os.path.isfile(thing):
        if thing[-3:] == '.py':
            process_file(thing)
    else:
        print "W `%s' not file or directory"%(thing,)

author_map = {
    u'mwh': None,
    u'Michael Hudson <michael.hudson@linaro.org>': None,
    u'arigo': u"Armin Rigo",
    u'antocuni': u'Antonio Cuni',
    u'bob': u'Bob Ippolito',
    u'fijal': u'Maciek Fijalkowski',
    u'agaynor': u'Alex Gaynor',
    u'hpk': u'Holger Krekel',
    }

def process_file(file):
    ilines = open(file).readlines()
    file_id = rev_tree.path2id(file)
    last_modified = rev_tree.get_file_mtime(file_id)
    modified_year = time.gmtime(last_modified)[0]
    rev_ids = [rev_id for (revno, rev_id, what)
               in bzrlib.log.find_touching_revisions(branch, file_id)]
    revs = branch.repository.get_revisions(rev_ids)
    authors = set()
    for rev in revs:
        authors.update(rev.get_apparent_authors())
    extra_authors = []
    for a in authors:
        if a not in author_map:
            print 'E: need real name for %r' % a
        ea = author_map.get(a)
        if ea:
            extra_authors.append(ea)
    extra_authors.sort()
    header = header_template % (modified_year, ''.join([author_template%ea for ea in extra_authors]))
    header_lines = header.splitlines()
    prelines = []
    old_copyright = []

    if not ilines:
        print "W ignoring empty file `%s'"%(file,)
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

    if abs(len(old_copyright) - len(header_lines)) < 2:
        for x, y in zip(old_copyright, header_lines):
            if x[:-1] != y:
                print "C change needed in", file
                ofile = open(file, "w")
                for l in prelines:
                    ofile.write(l)
                ofile.write(header + "\n")
                for l in ilines[i:]:
                    ofile.write(l)
                ofile.close()
                break
        else:
            print "M no change needed in", file
    else:
        print "A no (c) in", file
        ofile = open(file, "w")
        for l in prelines:
            ofile.write(l)
        ofile.write(header + "\n\n")
        for l in ilines[len(prelines):]:
            ofile.write(l)
        ofile.close()
        

for thing in sys.argv[1:]:
    process(thing)
