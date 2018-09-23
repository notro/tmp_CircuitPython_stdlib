"""
Operator Interface

This module exports a set of functions corresponding to the intrinsic
operators of Python.  For example, operator.add(x, y) is equivalent
to the expression x+y.  The function names are those used for special
methods; variants without leading and trailing '__' are also provided
for convenience.

This is the pure Python implementation of the module.
"""

def add(a, b):
    "Same as a + b."
    return a + b

def mul(a, b):
    "Same as a * b."
    return a * b

def neg(a):
    "Same as -a."
    return -a

def pow(a, b):
    "Same as a ** b."
    return a ** b


# Generalized Lookup Objects **************************************************#

class attrgetter:
    """
    Return a callable object that fetches the given attribute(s) from its operand.
    After f = attrgetter('name'), the call f(r) returns r.name.
    After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
    After h = attrgetter('name.first', 'name.last'), the call h(r) returns
    (r.name.first, r.name.last).
    """
    def __init__(self, attr, *attrs):
        if not attrs:
            if not isinstance(attr, str):
                raise TypeError('attribute name must be a string')
            names = attr.split('.')
            def func(obj):
                for name in names:
                    obj = getattr(obj, name)
                return obj
            self._call = func
        else:
            getters = tuple(map(attrgetter, (attr,) + attrs))
            def func(obj):
                return tuple(getter(obj) for getter in getters)
            self._call = func

    def __call__(self, obj):
        return self._call(obj)

