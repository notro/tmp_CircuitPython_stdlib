"""Extract, format and print information about Python stack traces."""

import sys
import operator


#
# Formatting and printing lists of traceback lines.
#

def _format_list_iter(extracted_list):
    for filename, lineno, name, line in extracted_list:
        item = '  File "{}", line {}, in {}\n'.format(filename, lineno, name)
        if line:
            item = item + '    {}\n'.format(line.strip())
        yield item


#
# Printing and Extracting Tracebacks.
#

# extractor takes curr and needs to return a tuple of:
# - Frame object
# - Line number
# - Next item (same type as curr)
# In practice, curr is either a traceback or a frame.
def _extract_tb_or_stack_iter(curr, limit, extractor):
    if limit is None:
        limit = getattr(sys, 'tracebacklimit', None)

    n = 0
    while curr is not None and (limit is None or n < limit):
        f, lineno, next_item = extractor(curr)
        co = f.f_code
        filename = co.co_filename
        name = co.co_name

        line = None                                                             ###

        yield (filename, lineno, name, line)
        curr = next_item
        n += 1

def _extract_tb_iter(tb, limit):
    return _extract_tb_or_stack_iter(
                tb, limit,
                operator.attrgetter("tb_frame", "tb_lineno", "tb_next"))


#
# Exception formatting and output.
#


def _format_exception_iter(etype, value, tb, limit, chain):
    if True:                                                                    ###
        values = [(value, tb)]

    for value, tb in values:
        if isinstance(value, str):
            # This is a cause/context message line
            yield value + '\n'
            continue
        if tb:
            yield 'Traceback (most recent call last):\n'
            yield from _format_list_iter(_extract_tb_iter(tb, limit=limit))
        yield from _format_exception_only_iter(type(value), value)

def print_exception(etype, value, tb, limit=None, file=None, chain=True):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    if file is None:
        file = sys.stderr
    for line in _format_exception_iter(etype, value, tb, limit, chain):
        print(line, file=file, end="")

def format_exception(etype, value, tb, limit=None, chain=True):
    """Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The return value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().
    """
    return list(_format_exception_iter(etype, value, tb, limit, chain))

def format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    return list(_format_exception_only_iter(etype, value))

def _format_exception_only_iter(etype, value):
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        yield _format_final_exc_line(etype, value)
        return

    stype = etype.__name__

    if not issubclass(etype, SyntaxError):
        yield _format_final_exc_line(stype, value)
        return

    # It was a syntax error; show exactly where the problem was found.
    filename = "<string>"                                                       ###
    lineno = '?'                                                                ###
    yield '  File "{}", line {}\n'.format(filename, lineno)

    msg = "<no detail available>"                                               ###
    yield "{}: {}\n".format(stype, msg)

def _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = "%s: %s\n" % (etype, valuestr)
    return line

def _some_str(value):
    try:
        return str(value)
    except:
        return '<unprintable %s object>' % type(value).__name__

def print_exc(limit=None, file=None, chain=True):
    """Shorthand for 'print_exception(*sys.exc_info(), limit, file)'."""
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)

def format_exc(limit=None, chain=True):
    """Like print_exc() but return a string."""
    return "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))


def clear_frames(tb):
    pass                                                                        ###
