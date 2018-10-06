func_attrs = {}

def func_clearattrs():
    func_attrs.clear()


def func_setattr(f, name, value):
#    print('\nfunc_setattr({!r}:{!r}, {!r}, {!r})'.format(f, f.__name__, name, value))

    if not f.__name__ in func_attrs:
        func_attrs[f.__name__] = {}
    func_attrs[f.__name__][name] = value


def func_getattr(f, name, *args):
    try:
        f = f.__func__  # In case it's a bound method
    except AttributeError:
        pass

    try:
        fname = f.__name__
    except AttributeError:
        fname = str(id(f))
#    print('\nfunc_getattr({!r}:{!r}, {!r}, {!r})'.format(f, fname, name, args[0]))

    try:
        val = func_attrs[f.__name__][name]
#        print('             name >>> {!r}'.format(val))
        return func_attrs[f.__name__][name]
    except (AttributeError, KeyError):  # AttributeError in case it's a closure
        pass

    if len(args) == 0:
        raise AttributeError("'function' object has no attribute {!r}".format(name))
#    print('             default >>> {!r}'.format(args[0]))
    return args[0]
