


func_attrs = {}

def func_hasattr(f, name):
    return f in func_attrs and name in func_attrs[f]

def func_setattr2(f, name, value):
    try:
        fname = f.__name__
    except AttributeError:
        fname = str(id(f))
    print('\nfunc_setattr({!r}:{!r}, {!r}, {!r})'.format(f, fname, name, value))

    if not f in func_attrs:
        func_attrs[f] = {}
    func_attrs[f][name] = value
    if hasattr(f, '__name__'):
        if not f.__name__ in func_attrs:
            func_attrs[f.__name__] = {}
        func_attrs[f.__name__][name] = value

def func_getattr2(f, name, *args):
    try:
        fname = f.__name__
    except AttributeError:
        fname = str(id(f))
    print('\nfunc_getattr({!r}:{!r}, {!r}, {!r})'.format(f, fname, name, args[0]))

    if hasattr(f, '__func__'):
        f2 = f.__func__
        if hasattr(f2, '__name__'):
            fname = f2.__name__
        else:
            fname = '{}'.format(id(f2))
        print('             {!r}:{!r}'.format(f2, fname))

        if hasattr(f2, '__func__'):
            f3 = f2.__func__
            if hasattr(f3, '__name__'):
                fname = f3.__name__
            else:
                fname = '{}'.format(id(f3))
            print('             {!r}:{!r}'.format(f3, fname))




    try:
        val = func_attrs[f][name]
        print('             id >>> {!r}'.format(val))
        return func_attrs[f][name]
    except KeyError:
        pass

    try:
        val = func_attrs[f.__name__][name]
        print('             name >>> {!r}'.format(val))
        return func_attrs[f.__name__][name]
    except (AttributeError, KeyError):
        pass

    if len(args) == 0:
        raise AttributeError("'function' object has no attribute {!r}".format(name))
    print('             default >>> {!r}'.format(args[0]))
    return args[0]

    #if hasattr(f, '__func__'):
    #    f = f.__func__
    #    if hasattr(f, '__name__'):
    #        fname = f.__name__
    #    else:
    #        fname = '{}'.format(id(f))
    #    print('             {!r}:{!r}'.format(f, fname))
    if not func_hasattr(f, name):

        if hasattr(f, '__name__') and f.__name__ in func_attrs and name in func_attrs[f.__name__]:
            print('             >>> __name__: {!r}'.format(func_attrs[f.__name__][name]))
            return func_attrs[f.__name__][name]



        if len(args) == 0:
            raise AttributeError("'function' object has no attribute {!r}".format(name))
        print('             >>> default: {!r}'.format(args[0]))
        return args[0]
    print('             >>> {!r}'.format(func_attrs[f][name]))
    return func_attrs[f][name]


def func_clearattrs():
    func_attrs.clear()


def func_setattr(f, name, value):
#    print('\nfunc_setattr({!r}:{!r}, {!r}, {!r})'.format(f, f.__name__, name, value))

    if not f.__name__ in func_attrs:
        func_attrs[f.__name__] = {}
    func_attrs[f.__name__][name] = value

#    if not f in func_attrs:
#        func_attrs[f] = {}
#    func_attrs[f][name] = value
#    if hasattr(f, '__name__'):
#        if not f.__name__ in func_attrs:
#            func_attrs[f.__name__] = {}
#        func_attrs[f.__name__][name] = value


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
