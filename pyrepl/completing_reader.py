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

from pyrepl import historical_reader, commands, reader
from pyrepl.historical_reader import HistoricalReader as HR

completing_keymap = historical_reader.history_keymap + (
    (r'\t', 'complete'),)

def uniqify(l):
    d = {}
    for i in l:
        d[i] = 1
    r = d.keys()
    r.sort()
    return r

def prefix(wordlist, j = 0):
    d = {}
    i = j
    try:
        while 1:
            for word in wordlist:
                d[word[i]] = 1
            if len(d) > 1:
                return wordlist[0][j:i]
            i += 1
            d = {}
    except IndexError:
        return wordlist[0][j:i]

def build_menu(cons, wordlist, start):
    maxlen = max(map(len, wordlist))
    cols = cons.width / (maxlen + 4)
    rows = (len(wordlist) - 1)/cols + 1
    menu = []
    i = start
    for r in range(rows):
        row = []
        for col in range(cols):
            row.append("[ %-*s ]"%(maxlen, wordlist[i]))
            i += 1
            if i >= len(wordlist):
                break
        menu.append( ''.join(row) )
        if i >= len(wordlist):
            i = 0
            break
        if r + 5 > cons.height:
            menu.append("   %d more... "%(len(wordlist) - i))
            break
    return menu, i    

# this gets somewhat user interface-y, and as a result the logic gets
# very convoluted.
#
#  To summarise the summary of the summary:- people are a problem.
#                  -- The Hitch-Hikers Guide to the Galaxy, Episode 12

#### Desired behaviour of the completions commands.
# the considerations are:
# (1) how many completions are possible
# (2) whether the last command was a completion
#
# if there's no possible completion, beep at the user and point this out.
# this is easy.
#
# if there's only one possible completion, stick it in.  if the last thing
# user did was a completion, point out that he isn't getting anywhere.
#
# now it gets complicated.
# 
# for the first press of a completion key:
#  if there's a common prefix, stick it in.

#  irrespective of whether anything got stuck in, if the word is now
#  complete, show the "complete but not unique" message

#  if there's no common prefix and if the word is not now complete,
#  beep.

#        common prefix ->    yes          no
#        word complete \/
#            yes           "cbnu"      "cbnu"
#            no              -          beep

# for the second bang on the completion key
#  there will necessarily be no common prefix
#  show a menu of the choices.

# for subsequent bangs, rotate the menu around (if there are sufficient
# choices).

class complete(commands.Command):
    def do(self):
        r = self.reader
        stem = r.get_stem()
        if r.last_command_is(self.__class__):
            completions = r.cmpltn_menu_choices
        else:
            r.cmpltn_menu_choices = completions = \
                                        r.get_completions(stem)
        if len(completions) == 0:
            r.error("no matches")
        elif len(completions) == 1:
            if len(completions[0]) == len(stem) and \
                   r.last_command_is(self.__class__):
                r.msg = "[ sole completion ]"
                r.dirty = 1
            r.insert(completions[0][len(stem):])
        else:
            p = prefix(completions, len(stem))
            if p <> '':
                r.insert(p)
            if r.last_command_is(self.__class__):
                if not r.cmpltn_menu_vis:
                    r.cmpltn_menu_vis = 1
                r.cmpltn_menu, r.cmpltn_menu_end = build_menu(
                    r.console, completions, r.cmpltn_menu_end)
                r.dirty = 1
            elif stem + p in completions:
                r.msg = "[ complete but not unique ]"
                r.dirty = 1
            else:
                r.msg = "[ not unique ]"
                r.dirty = 1

class self_insert(commands.self_insert):
    def do(self):
        commands.self_insert.do(self)
        r = self.reader
        if r.cmpltn_menu_vis:
            stem = r.get_stem()
            if len(stem) < 1:
                r.cmpltn_reset()
            else:
                completions = [w for w in r.cmpltn_menu_choices
                               if w.startswith(stem)]
                if completions:
                    r.cmpltn_menu, r.cmpltn_menu_end = build_menu(
                        r.console, completions, 0)
                else:
                    r.cmpltn_reset()

class CompletingReader(HR):
    """Adds completion support to the HistoricalReader class.

    Adds instance variables:
      * cmpltn_menu, cmpltn_menu_vis, cmpltn_menu_end, cmpltn_choices:
      *
    """

    keymap = completing_keymap
    
    HR_init = HR.__init__
    def __init__(self, console):
        self.HR_init(console)
        self.cmpltn_menu = ["[ menu 1 ]", "[ menu 2 ]"]
        self.cmpltn_menu_vis = 0
        self.cmpltn_menu_end = 0
        for c in [complete, self_insert]:
            self.commands[c.__name__] = c
            self.commands[c.__name__.replace('_', '-')] = c        

    def install_keymap(self):
        self.console.install_keymap(self.keymap)

    HR_after_command = HR.after_command
    def after_command(self, cmd):
        self.HR_after_command(cmd)
        if not isinstance(cmd, complete) and not isinstance(cmd, self_insert):
            self.cmpltn_reset()

    HR_calc_screen = HR.calc_screen
    def calc_screen(self):
        screen = self.HR_calc_screen()
        if self.cmpltn_menu_vis:
            ly = self.lxy[1]
            screen[ly:ly] = self.cmpltn_menu
            self.screeninfo[ly:ly] = [(0, [])]*len(self.cmpltn_menu)
            self.cxy = self.cxy[0], self.cxy[1] + len(self.cmpltn_menu)
        return screen

    HR_finish = HR.finish
    def finish(self):
        self.HR_finish()
        self.cmpltn_reset()

    def cmpltn_reset(self):
        self.cmpltn_menu = []
        self.cmpltn_menu_vis = 0
        self.cmpltn_menu_end = 0
        self.cmpltn_menu_choices = []        

    def get_stem(self):
        st = self.syntax_table
        b = self.buffer
        p = self.pos - 1
        while p >= 0 and st[b[p]] == reader.SYNTAX_WORD:
            p -= 1
        return ''.join(b[p+1:self.pos])

    def get_completions(self, stem):
        return []

def test():
    class TestReader(CompletingReader):
        def get_completions(self, stem):
            return [s for l in map(lambda x:x.split(),self.history)
                    for s in l if s and s.startswith(stem)]
    reader = TestReader()
    reader.ps1 = "c**> "
    reader.ps2 = "c/*> "
    reader.ps3 = "c|*> "
    reader.ps4 = "c\*> "
    while reader.readline():
        pass

if __name__=='__main__':
    test()
