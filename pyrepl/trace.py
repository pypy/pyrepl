import os

trace_filename = os.environ.get("PYREPL_TRACE")

trace_file = open(trace_filename, "a") if trace_filename is not None else None


def trace(line, *k, **kw):
    if trace_file is None:
        return
    if k or kw:
        line = line.format(*k, **kw)
    trace_file.write(line + "\n")
    trace_file.flush()
