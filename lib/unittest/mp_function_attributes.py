


func_attrs = {}

def func_hasattr(f, name):
    return f in func_attrs and name in func_attrs[f]

def func_setattr(f, name, value):
    #print('func_setattr:', f, name, value)
    if not f in func_attrs:
        func_attrs[f] = {}
    func_attrs[f][name] = value

def func_getattr(f, name, *args):
    if not func_hasattr(f, name):
        if len(args) == 0:
            raise AttributeError("'function' object has no attribute {!r}".format(name))
        return args[0]
    return func_attrs[f][name]

def func_clearattrs():
    func_attrs.clear()
