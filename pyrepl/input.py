# (naming modules after builtin functions is not such a hot idea...)

# an KeyTrans instance translates Event objects into Command objects

# hmm, at what level do we want [C-i] and [tab] to be equivalent?
# [meta-a] and [esc a]?  obviously, these are going to be equivalent
# for the UnixConsole, but should they be for PygameConsole?

# it would in any situation seem to be a bad idea to bind, say, [tab]
# and [C-i] to *different* things... but should binding one bind the
# other?

# executive, temporary decision: [tab] and [C-i] are distinct, but
# [meta-key] is identified with [esc key].  We demand that any console
# class does quite a lot towards emulating a unix terminal.

class InputTranslator(object):
    def push(self, evt):
        pass
    def get(self):
        pass
    def empty(self):
        pass

class KeymapTranslator(InputTranslator):
    def __init__(self, keymap, verbose=0, invalid_cls=None):
        self.verbose = verbose
        from pyrepl.keymap import compile_keymap, parse_keys
        self.keymap = keymap
        self.invalid_cls = invalid_cls
        d = {}
        for keyspec, command in keymap:
            keyseq = tuple(parse_keys(keyspec))
            d[keyseq] = command
        if self.verbose:
            print d
        self.k = self.ck = compile_keymap(d, ())
        self.results = []
        self.stack = []
    def push(self, evt):
        if self.verbose:
            print "pushed", evt.data,
        key = evt.data
        d = self.k.get(key)
        if isinstance(d, dict):
            if self.verbose:
                print "transition"
            self.stack.append((key, self.stack + [key]))
            self.k = d
        else:
            if d is None:
                if self.verbose:
                    print "invalid"
                self.results.append(
                    (self.invalid_cls,
                     self.stack + [key]))
            else:
                if self.verbose:
                    print "matched", d
                self.results.append((d,
                                     self.stack + [key]))
            self.stack = []
            self.k = self.ck
    def get(self):
        if self.results:
            return self.results.pop(0)
        else:
            return None
    def empty(self):
        return not self.results
            
