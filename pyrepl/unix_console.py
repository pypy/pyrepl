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

import termios, curses, select, os, struct, types, errno, signal
import re, time, sys
from fcntl import ioctl
from pyrepl.fancy_termios import tcgetattr, tcsetattr
from pyrepl.console import Console, Event
from pyrepl import unix_keymap

# there are arguments for changing this to "refresh"
SIGWINCH_EVENT = 'repaint'

FIONREAD = getattr(termios, "FIONREAD", None)
TIOCGWINSZ = getattr(termios, "TIOCGWINSZ", None)

if sys.version[:3] == '2.1' and sys.platform == 'linux2':
    # 2.1's termios module was bust wrt. *lots* of constants...
    TIOCGWINSZ = getattr(termios, "TIOCGWINSZ", 0x5413)
    FIONREAD = getattr(termios, "FIONREAD", 0x541B)

def _my_getstr(cap, optional=0):
    r = curses.tigetstr(cap)
    if not optional and r is None:
        raise RuntimeError, \
              "terminal doesn't have the required '%s' capability"%cap
    return r

_keynames = {
#    "backspace" : "kbs", # dig this out of tcgetattr instead
    "delete" : "kdch1",
    "down" : "kcud1",
    "end" : "kend",
    "enter" : "kent",
    "f1"  : "kf1",    "f2"  : "kf2",    "f3"  : "kf3",    "f4"  : "kf4",
    "f5"  : "kf5",    "f6"  : "kf6",    "f7"  : "kf7",    "f8"  : "kf8",
    "f9"  : "kf9",    "f10" : "kf10",   "f11" : "kf11",   "f12" : "kf12",
    "f13" : "kf13",   "f14" : "kf14",   "f15" : "kf15",   "f16" : "kf16",
    "f17" : "kf17",   "f18" : "kf18",   "f19" : "kf19",   "f20" : "kf20",
    "home" : "khome",
    "insert" : "kich1",
    "left" : "kcub1",
    "pgdown" : "knp",       "page down" : "knp",
    "pgup"   : "kpp",       "page up"   : "kpp",
    "right" : "kcuf1",
    "up" : "kcuu1",
    }

_keysets = {}

def keyset(con=None):
    if con is None:
        term, fd = os.environ["TERM"], 0
    else:
        term, fd = con.term, con.fd
    try:
        return _keysets[(term, fd)]
    except KeyError:
        set = {'space' : ' ', 'tab' : '\t', 'hash' : '#',
               "escape":"\033", "return":"\n", 'backslash':'\\'}
        for key, code in _keynames.items():
            set[key] = curses.tigetstr(code)
        set["backspace"] = termios.tcgetattr(fd)[6][termios.VERASE]
        return _keysets.setdefault((term, fd), set)

# at this point, can we say: AAAAAAAAAAAAAAAAAAAAAARGH!
def maybe_add_baudrate(dict, rate):
    name = 'B%d'%rate
    if hasattr(termios, name):
        dict[getattr(termios, name)] = rate

ratedict = {}
for r in [0, 110, 115200, 1200, 134, 150, 1800, 19200, 200, 230400,
          2400, 300, 38400, 460800, 4800, 50, 57600, 600, 75, 9600]:
    maybe_add_baudrate(ratedict, r)

del r, maybe_add_baudrate

delayprog = re.compile("\\$<([0-9]+)((?:/|\\*){0,2})>")

try:
    poll = select.poll
except AttributeError:
    # this is exactly the minumum necessary to support what we
    # do with poll objects
    class poll:
        def __init__(self):
            pass
        def register(self, fd, flag):
            self.fd = fd
        def poll(self, timeout=None):
            r,w,e = select.select([self.fd],[],[],timeout)
            return r

POLLIN = getattr(select, "POLLIN", None)

class UnixConsole(Console):
    def __init__(self, fd, term):
        self.fd = fd
        self.pollob = poll()
        self.pollob.register(fd, POLLIN)
        curses.setupterm(term, fd)
        self.term = term
        
        self._bel   = _my_getstr("bel")
        self._civis = _my_getstr("civis", optional=1)
        self._clear = _my_getstr("clear")
        self._cnorm = _my_getstr("cnorm", optional=1)
        self._cub   = _my_getstr("cub",   optional=1)
        self._cub1  = _my_getstr("cub1",  1)
        self._cud   = _my_getstr("cud",   1)
        self._cud1  = _my_getstr("cud1",  1)
        self._cuf   = _my_getstr("cuf",   1)
        self._cuf1  = _my_getstr("cuf1",  1)
        self._cup   = _my_getstr("cup")
        self._cuu   = _my_getstr("cuu",   1)
        self._cuu1  = _my_getstr("cuu1",  1)
        self._dch1  = _my_getstr("dch1",  1)
        self._dch   = _my_getstr("dch",   1)
        self._el    = _my_getstr("el")
        self._hpa   = _my_getstr("hpa",   1)
        self._ich   = _my_getstr("ich",   1)
        self._ich1  = _my_getstr("ich1",  1)
        self._ind   = _my_getstr("ind",   1)
        self._pad   = _my_getstr("pad",   1)
        self._ri    = _my_getstr("ri",    1)
        self._rmkx  = _my_getstr("rmkx",  1)
        self._smkx  = _my_getstr("smkx",  1)
        
        ## work out how we're going to sling the cursor around
        if 0 and self._hpa: # hpa don't work in windows telnet :-(
            self.__move_x = self.__move_x_hpa
        elif self._cub and self._cuf:
            self.__move_x = self.__move_x_cub_cuf
        elif self._cub1 and self._cuf1:
            self.__move_x = self.__move_x_cub1_cuf1
        else:
            raise RuntimeError, "insufficient terminal (horizontal)"

        if self._cuu and self._cud:
            self.__move_y = self.__move_y_cuu_cud
        elif self._cuu1 and self._cud1:
            self.__move_y = self.__move_y_cuu1_cud1
        else:
            raise RuntimeError, "insufficient terminal (vertical)"

        if self._dch1:
            self.dch1 = self._dch1
        elif self._dch:
            self.dch1 = curses.tparm(self._dch, 1)
        else:
            self.dch1 = None

        if self._ich1:
            self.ich1 = self._ich1
        elif self._ich:
            self.ich1 = curses.tparm(self._ich, 1)
        else:
            self.ich1 = None

        self.__move = self.__move_short

        self.keymap = {}

    def install_keymap(self, new_keymap):
        self.k = self.keymap = \
                     unix_keymap.compile_keymap(new_keymap, keyset(self))

    def describe_event(self, event):
        return unix_keymap.unparse_keyf(event.chars, keyset(self))

    def refresh(self, screen, (cx, cy)):
        # this function is still too long (over 90 lines)
        self.__maybe_write_code(self._civis)

        if not self.__gone_tall:
            while len(self.screen) < min(len(screen), self.height):
                self.__move(0, len(self.screen) - 1)
                self.__write("\n")
                self.__posxy = 0, len(self.screen)
                self.screen.append("")
        else:
            while len(self.screen) < len(screen):
                self.screen.append("")            

        if len(screen) > self.height:
            self.__gone_tall = 1
            self.__move = self.__move_tall

        px, py = self.__posxy
        old_offset = offset = self.__offset
        height = self.height

        if 0:
            global counter
            try:
                counter
            except NameError:
                counter = 0
            self.__write_code(curses.tigetstr("setaf"), counter)
            counter += 1
            if counter > 8:
                counter = 0

        # we make sure the cursor is on the screen, and that we're
        # using all of the screen if we can
        if cy < offset:
            offset = cy
        elif cy >= offset + height:
            offset = cy - height + 1
        elif offset > 0 and len(screen) < offset + height:
            offset = max(len(screen) - height, 0)
            screen.append([])

        oldscr = self.screen[old_offset:old_offset + height]
        newscr = screen[offset:offset + height]

        # use hardware scrolling if we have it.
        if old_offset > offset and self._ri:
            self.__write_code(self._cup, 0, 0)
            self.__posxy = 0, old_offset
            for i in range(old_offset - offset):
                self.__write_code(self._ri)
                oldscr.pop(-1)
                oldscr.insert(0, "")
        elif old_offset < offset and self._ind:
            self.__write_code(self._cup, self.height - 1, 0)
            self.__posxy = 0, old_offset + self.height - 1
            for i in range(offset - old_offset):
                self.__write_code(self._ind)
                oldscr.pop(0)
                oldscr.append("")

        self.__offset = offset

        # in the refresh loop we check for a common case: the
        # insertion of a single character.

        for y, oldline, newline, in zip(range(offset, offset + height),
                                        oldscr,
                                        newscr):
            if oldline != newline:
                self.write_changed_line(y, oldline, newline, px)
                
        y = len(newscr)
        while y < len(oldscr):
            self.__move(0, y)
            self.__posxy = 0, y
            self.__write_code(self._el)
            y += 1

        self.__maybe_write_code(self._cnorm)
        
        self.flushoutput()
        self.screen = screen
        self.move_cursor(cx, cy)

    def write_changed_line(self, y, oldline, newline, px):
        # this is frustrating; there's no reason to test (say)
        # self.dch1 inside the loop -- but alternative ways of
        # structuring this function are equally painful (I'm trying to
        # avoid writing code generators these days...)
        x = 0
        minlen = min(len(oldline), len(newline))
        while x < minlen and oldline[x] == newline[x]:
            x += 1
        if oldline[x:] == newline[x+1:] and self.ich1:
            if ( y == self.__posxy[1] and x > self.__posxy[0]
                 and oldline[px:x] == newline[px+1:x+1] ):
                x = px
            self.__move(x, y)
            self.__write_code(self.ich1)
            self.__write(newline[x])
            self.__posxy = x + 1, y
        elif x < minlen and oldline[x + 1:] == newline[x + 1:]:
            self.__move(x, y)
            self.__write(newline[x])
            self.__posxy = x + 1, y
        elif (self.dch1 and self.ich1 and len(newline) == self.width
              and x < len(newline) - 2
              and newline[x+1:-1] == oldline[x:-2]):
            self.__move(self.width - 2, y)
            self.__posxy = self.width - 2, y
            self.__write_code(self.dch1)
            self.__move(x, y)
            self.__write_code(self.ich1)
            self.__write(newline[x])
            self.__posxy = x + 1, y
        else:
            self.__move(x, y)
            if len(oldline) > len(newline):
                self.__write_code(self._el)
            self.__write(newline[x:])
            self.__posxy = len(newline), y
        self.flushoutput()

    def __write(self, text):
        self.__buffer.append((text, 0))

    def __write_code(self, fmt, *args):
        self.__buffer.append((curses.tparm(fmt, *args), 1))

    def __maybe_write_code(self, fmt, *args):
        if fmt:
            self.__write_code(fmt, *args)

    def __move_y_cuu1_cud1(self, y):
        dy = y - self.__posxy[1]
        if dy > 0:
            self.__write_code(dy*self._cud1)
        elif dy < 0:
            self.__write_code((-dy)*self._cuu1)

    def __move_y_cuu_cud(self, y):
        dy = y - self.__posxy[1]
        if dy > 0:
            self.__write_code(self._cud, dy)
        elif dy < 0:
            self.__write_code(self._cuu, -dy)

    def __move_x_hpa(self, x):
        if x != self.__posxy[0]:
            self.__write_code(self._hpa, x)

    def __move_x_cub1_cuf1(self, x):
        dx = x - self.__posxy[0]
        if dx > 0:
            self.__write_code(self._cuf1*dx)
        elif dx < 0:
            self.__write_code(self._cub1*(-dx))

    def __move_x_cub_cuf(self, x):
        dx = x - self.__posxy[0]
        if dx > 0:
            self.__write_code(self._cuf, dx)
        elif dx < 0:
            self.__write_code(self._cub, -dx)

    def __move_short(self, x, y):
        self.__move_x(x)
        self.__move_y(y)

    def __move_tall(self, x, y):
        assert 0 <= y - self.__offset < self.height, y - self.__offset
        self.__write_code(self._cup, y - self.__offset, x)

    def move_cursor(self, x, y):
        if y < self.__offset or y >= self.__offset + self.height:
            self.__event_queue.append(Event('refresh', '', ''))
        else:
            self.__move(x, y)
            self.__posxy = x, y
            self.flushoutput()

    def prepare(self):
        # per-readline preparations:
        self.__svtermstate = tcgetattr(self.fd)
        raw = self.__svtermstate.copy()
        raw.iflag &=~ (termios.BRKINT | termios.INPCK |
                       termios.ISTRIP | termios.IXON)
        raw.oflag &=~ (termios.OPOST)
        raw.cflag &=~ (termios.CSIZE|termios.PARENB)
        raw.cflag |=  (termios.CS8)
        raw.lflag &=~ (termios.ICANON|termios.ECHO|
                       termios.IEXTEN|(termios.ISIG*1))
        raw.cc[termios.VMIN] = 1
        raw.cc[termios.VTIME] = 0
        tcsetattr(self.fd, termios.TCSADRAIN, raw)

        self.screen = []
        self.height, self.width = self.getheightwidth()

        self.__buffer = []
        
        self.__posxy = 0, 0
        self.__gone_tall = 0
        self.__move = self.__move_short
        self.__offset = 0

        self.__maybe_write_code(self._smkx)

        self.old_sigwinch = signal.signal(
            signal.SIGWINCH, self.__sigwinch)
        self.__event_queue = []

        # per-event preparations:
        self.__cmd_buf = ''
        self.k = self.keymap

    def restore(self):
        self.__maybe_write_code(self._rmkx)
        self.flushoutput()
        tcsetattr(self.fd, termios.TCSADRAIN, self.__svtermstate)

        signal.signal(signal.SIGWINCH, self.old_sigwinch)

    def __sigwinch(self, signum, frame):
        self.height, self.width = self.getheightwidth()
        self.__event_queue.append(Event(SIGWINCH_EVENT, '', ''))

    def get_event(self, block=1):
        if self.__event_queue:
            return self.__event_queue.pop(0)
        while 1:
            if block or self.pollob.poll(0):
                while 1: # All hail Unix!
                    try:
                        c = os.read(self.fd, 1)
                    except OSError, err:
                        if err.errno == errno.EINTR:
                            if self.__event_queue:
                                return self.__event_queue.pop(0)
                            else:
                                continue # be explicit
                        else:
                            raise
                    else:
                        break
                self.__cmd_buf += c
                try:
                    k = self.k = self.k[c]
                except:
                    self.__cmd_buf += self.getpending()
                    k = "invalid-key"
                if type(k) is not types.DictType:
                    e = Event(k, self.__cmd_buf, self.__cmd_buf)
                    self.k = self.keymap
                    self.__cmd_buf = ''
                    return e
            if not block:
                return None

    def wait(self):
        self.pollob.poll()

    def set_cursor_vis(self, vis):
        if vis:
            self.__maybe_write_code(self._cnorm)
        else:
            self.__maybe_write_code(self._civis)

    def repaint_prep(self):
        if not self.__gone_tall:
            self.__posxy = 0, self.__posxy[1]
            self.__write("\r")
            ns = len(self.screen)*['\000'*self.width]
            self.screen = ns
        else:
            self.__posxy = 0, self.__offset
            self.__move(0, self.__offset)
            ns = self.height*['\000'*self.width]
            self.screen = ns

    if TIOCGWINSZ:
        def getheightwidth(self):
            try:
                return int(os.environ["LINES"]), int(os.environ["COLUMNS"])
            except KeyError:
                height, width = struct.unpack(
                    "hhhh", ioctl(self.fd, TIOCGWINSZ, "\000"*8))[0:2]
                if not height: return 25, 80
                return height, width
    else:
        def getheightwidth(self):
            try:
                return int(os.environ["LINES"]), int(os.environ["COLUMNS"])
            except KeyError:
                return 25, 80

    def forgetinput(self):
        termios.tcflush(self.fd, termios.TCIFLUSH)

    def flushoutput(self):
        for text, iscode in self.__buffer:
            if iscode:
                self.__tputs(text)
            else:
                os.write(self.fd, text)
        del self.__buffer[:]

    def __tputs(self, fmt, prog=delayprog):
        """A Python implementation of the curses tputs function; the
        curses one can't really be wrapped in a sane manner.

        I have the strong suspicion that this is complexity that
        will never do anyone any good."""
        # using .get() means that things will blow up
        # only if the bps is actually needed (which I'm
        # betting is pretty unlkely)
        bps = ratedict.get(self.__svtermstate.ospeed)
        while 1:
            m = prog.search(fmt)
            if not m:
                os.write(self.fd, fmt)
                break
            x, y = m.span()
            os.write(self.fd, fmt[:x])
            fmt = fmt[y:]
            delay = int(m.group(1))
            if '*' in m.group(2):
                delay *= self.height
            if self._pad:
                nchars = (bps*delay)/1000
                os.write(self.fd, self._pad*nchars)
            else:
                time.sleep(float(delay)/1000.0)

    def finish(self):
        y = len(self.screen) - 1
        while y >= 0 and not self.screen[y]:
            y -= 1
        self.__move(0, min(y, self.height + self.__offset - 1))
        self.__write("\n\r")
        self.flushoutput()

    def beep(self):
        self.__maybe_write_code(self._bel)
        self.flushoutput()

    if FIONREAD:
        def getpending(self):
            amount = struct.unpack(
                "i", ioctl(self.fd, FIONREAD, "\0\0\0\0"))[0]
            return os.read(self.fd, amount)
    else:
        def getpending(self):
            return os.read(self.fd, 100000) # that should be enough :)

    def clear(self):
        self.__write_code(self._clear)
        self.__gone_tall = 1
        self.__move = self.__move_tall
        self.__posxy = 0, 0
        self.screen = []
