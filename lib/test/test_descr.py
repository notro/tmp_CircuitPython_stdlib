#import builtins
#import copyreg
#import gc
#import itertools
#import math
#import pickle
#import sys
#import types
import unittest
#import weakref

from copy import deepcopy
#from test import support


class OperatorsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.binops = {
            'add': '+',
            'sub': '-',
            'mul': '*',
            'truediv': '/',
            'floordiv': '//',
            'divmod': 'divmod',
            'pow': '**',
            'lshift': '<<',
            'rshift': '>>',
            'and': '&',
            'xor': '^',
            'or': '|',
            'cmp': 'cmp',
            'lt': '<',
            'le': '<=',
            'eq': '==',
            'ne': '!=',
            'gt': '>',
            'ge': '>=',
        }

        for name, expr in list(self.binops.items()):
            if expr.islower():
                expr = expr + "(a, b)"
            else:
                expr = 'a %s b' % expr
            self.binops[name] = expr

        self.unops = {
            'pos': '+',
            'neg': '-',
            'abs': 'abs',
            'invert': '~',
            'int': 'int',
            'float': 'float',
        }

        for name, expr in list(self.unops.items()):
            if expr.islower():
                expr = expr + "(a)"
            else:
                expr = '%s a' % expr
            self.unops[name] = expr

    def unop_test(self, a, res, expr="len(a)", meth="__len__"):
        d = {'a': a}
        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)

        # Find method in parent class
        while meth not in t.__dict__:
            t = t.__bases__[0]
        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(), res)

    def binop_test(self, a, b, res, expr="a+b", meth="__add__"):
        d = {'a': a, 'b': b}

        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)
        while meth not in t.__dict__:
            t = t.__bases__[0]
        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a, b), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(b), res)

#    def sliceop_test(self, a, b, c, res, expr="a[b:c]", meth="__getitem__"):
#        d = {'a': a, 'b': b, 'c': c}
#        self.assertEqual(eval(expr, d), res)
#        t = type(a)
#        m = getattr(t, meth)
#        while meth not in t.__dict__:
#            t = t.__bases__[0]
#        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
#        # method object; the getattr() below obtains its underlying function.
#        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
#        self.assertEqual(m(a, slice(b, c)), res)
#        bm = getattr(a, meth)
#        self.assertEqual(bm(slice(b, c)), res)
#
#    def setop_test(self, a, b, res, stmt="a+=b", meth="__iadd__"):
#        d = {'a': deepcopy(a), 'b': b}
#        exec(stmt, d)
#        self.assertEqual(d['a'], res)
#        t = type(a)
#        m = getattr(t, meth)
#        while meth not in t.__dict__:
#            t = t.__bases__[0]
#        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
#        # method object; the getattr() below obtains its underlying function.
#        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
#        d['a'] = deepcopy(a)
#        m(d['a'], b)
#        self.assertEqual(d['a'], res)
#        d['a'] = deepcopy(a)
#        bm = getattr(d['a'], meth)
#        bm(b)
#        self.assertEqual(d['a'], res)
#
    def set2op_test(self, a, b, c, res, stmt="a[b]=c", meth="__setitem__"):
        d = {'a': deepcopy(a), 'b': b, 'c': c}
        exec(stmt, d)
        self.assertEqual(d['a'], res)
        t = type(a)
        m = getattr(t, meth)
#        while meth not in t.__dict__:
#            t = t.__bases__[0]
#        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
#        # method object; the getattr() below obtains its underlying function.
#        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        d['a'] = deepcopy(a)
        m(d['a'], b, c)
        self.assertEqual(d['a'], res)
        d['a'] = deepcopy(a)
        bm = getattr(d['a'], meth)
        bm(b, c)
        self.assertEqual(d['a'], res)

#    def setsliceop_test(self, a, b, c, d, res, stmt="a[b:c]=d", meth="__setitem__"):
#        dictionary = {'a': deepcopy(a), 'b': b, 'c': c, 'd': d}
#        exec(stmt, dictionary)
#        self.assertEqual(dictionary['a'], res)
#        t = type(a)
#        while meth not in t.__dict__:
#            t = t.__bases__[0]
#        m = getattr(t, meth)
#        # in some implementations (e.g. PyPy), 'm' can be a regular unbound
#        # method object; the getattr() below obtains its underlying function.
#        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
#        dictionary['a'] = deepcopy(a)
#        m(dictionary['a'], slice(b, c), d)
#        self.assertEqual(dictionary['a'], res)
#        dictionary['a'] = deepcopy(a)
#        bm = getattr(dictionary['a'], meth)
#        bm(slice(b, c), d)
#        self.assertEqual(dictionary['a'], res)
#
#    def test_lists(self):
#        # Testing list operations...
#        # Asserts are within individual test methods
#        self.binop_test([1], [2], [1,2], "a+b", "__add__")
#        self.binop_test([1,2,3], 2, 1, "b in a", "__contains__")
#        self.binop_test([1,2,3], 4, 0, "b in a", "__contains__")
#        self.binop_test([1,2,3], 1, 2, "a[b]", "__getitem__")
#        self.sliceop_test([1,2,3], 0, 2, [1,2], "a[b:c]", "__getitem__")
#        self.setop_test([1], [2], [1,2], "a+=b", "__iadd__")
#        self.setop_test([1,2], 3, [1,2,1,2,1,2], "a*=b", "__imul__")
#        self.unop_test([1,2,3], 3, "len(a)", "__len__")
#        self.binop_test([1,2], 3, [1,2,1,2,1,2], "a*b", "__mul__")
#        self.binop_test([1,2], 3, [1,2,1,2,1,2], "b*a", "__rmul__")
#        self.set2op_test([1,2], 1, 3, [1,3], "a[b]=c", "__setitem__")
#        self.setsliceop_test([1,2,3,4], 1, 3, [5,6], [1,5,6,4], "a[b:c]=d",
#                        "__setitem__")
#
    def test_dicts(self):
        # Testing dict operations...
#        self.binop_test({1:2,3:4}, 1, 1, "b in a", "__contains__")
#        self.binop_test({1:2,3:4}, 2, 0, "b in a", "__contains__")
#        self.binop_test({1:2,3:4}, 1, 2, "a[b]", "__getitem__")

        d = {1:2, 3:4}
        l1 = []
        for i in list(d.keys()):
            l1.append(i)
        l = []
        for i in iter(d):
            l.append(i)
        self.assertEqual(l, l1)
#        l = []
#        for i in d.__iter__():
#            l.append(i)
#        self.assertEqual(l, l1)
#        l = []
#        for i in dict.__iter__(d):
#            l.append(i)
#        self.assertEqual(l, l1)
        d = {1:2, 3:4}
#        self.unop_test(d, 2, "len(a)", "__len__")
        self.assertEqual(eval(repr(d), {}), d)
#        self.assertEqual(eval(d.__repr__(), {}), d)
        self.set2op_test({1:2,3:4}, 2, 3, {1:2,2:3,3:4}, "a[b]=c",
                        "__setitem__")

    # Tests for unary and binary operators
    def number_operators(self, a, b, skip=[]):
        dict = {'a': a, 'b': b}

        for name, expr in self.binops.items():
            if name not in skip:
                name = "__%s__" % name
                if hasattr(a, name):
                    res = eval(expr, dict)
                    self.binop_test(a, b, res, expr, name)

        for name, expr in list(self.unops.items()):
            if name not in skip:
                name = "__%s__" % name
                if hasattr(a, name):
                    res = eval(expr, dict)
                    self.unop_test(a, res, expr, name)

    def test_ints(self):
        # Testing int operations...
        self.number_operators(100, 3)
        # The following crashes in Python 2.2
#        self.assertEqual((1).__bool__(), 1)
#        self.assertEqual((0).__bool__(), 0)
        # This returns 'NotImplemented' in Python 2.2
        class C(int):
            def __add__(self, other):
                return NotImplemented
        self.assertEqual(C(5), 5)
        try:
            C() + ""
        except TypeError:
            pass
        else:
            self.fail("NotImplemented should have caused TypeError")

    def test_floats(self):
        # Testing float operations...
        self.number_operators(100.0, 3.0)

    def test_complexes(self):
        # Testing complex operations...
        self.number_operators(100.0j, 3.0j, skip=['lt', 'le', 'gt', 'ge',
                                                  'int', 'float',
                                                  'floordiv', 'divmod', 'mod'])

#        class Number(complex):
#            __slots__ = ['prec']
#            def __new__(cls, *args, **kwds):
#                result = complex.__new__(cls, *args)
#                result.prec = kwds.get('prec', 12)
#                return result
#            def __repr__(self):
#                prec = self.prec
#                if self.imag == 0.0:
#                    return "%.*g" % (prec, self.real)
#                if self.real == 0.0:
#                    return "%.*gj" % (prec, self.imag)
#                return "(%.*g+%.*gj)" % (prec, self.real, prec, self.imag)
#            __str__ = __repr__
#
#        a = Number(3.14, prec=6)
#        self.assertEqual(repr(a), "3.14")
#        self.assertEqual(a.prec, 6)
#
#        a = Number(a, prec=2)
#        self.assertEqual(repr(a), "3.1")
#        self.assertEqual(a.prec, 2)
#
#        a = Number(234.5)
#        self.assertEqual(repr(a), "234.5")
#        self.assertEqual(a.prec, 12)
#
#    def test_explicit_reverse_methods(self):
#        # see issue 9930
#        self.assertEqual(complex.__radd__(3j, 4.0), complex(4.0, 3.0))
#        self.assertEqual(float.__rsub__(3.0, 1), -2.0)
#
#    @support.impl_detail("the module 'xxsubtype' is internal")
#    def test_spam_lists(self):
#        # Testing spamlist operations...
#        import copy, xxsubtype as spam
#
#        def spamlist(l, memo=None):
#            import xxsubtype as spam
#            return spam.spamlist(l)
#
#        # This is an ugly hack:
#        copy._deepcopy_dispatch[spam.spamlist] = spamlist
#
#        self.binop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+b",
#                       "__add__")
#        self.binop_test(spamlist([1,2,3]), 2, 1, "b in a", "__contains__")
#        self.binop_test(spamlist([1,2,3]), 4, 0, "b in a", "__contains__")
#        self.binop_test(spamlist([1,2,3]), 1, 2, "a[b]", "__getitem__")
#        self.sliceop_test(spamlist([1,2,3]), 0, 2, spamlist([1,2]), "a[b:c]",
#                          "__getitem__")
#        self.setop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+=b",
#                        "__iadd__")
#        self.setop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*=b",
#                        "__imul__")
#        self.unop_test(spamlist([1,2,3]), 3, "len(a)", "__len__")
#        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*b",
#                        "__mul__")
#        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "b*a",
#                        "__rmul__")
#        self.set2op_test(spamlist([1,2]), 1, 3, spamlist([1,3]), "a[b]=c",
#                         "__setitem__")
#        self.setsliceop_test(spamlist([1,2,3,4]), 1, 3, spamlist([5,6]),
#                             spamlist([1,5,6,4]), "a[b:c]=d", "__setitem__")
#        # Test subclassing
#        class C(spam.spamlist):
#            def foo(self): return 1
#        a = C()
#        self.assertEqual(a, [])
#        self.assertEqual(a.foo(), 1)
#        a.append(100)
#        self.assertEqual(a, [100])
#        self.assertEqual(a.getstate(), 0)
#        a.setstate(42)
#        self.assertEqual(a.getstate(), 42)
#
#    @support.impl_detail("the module 'xxsubtype' is internal")
#    def test_spam_dicts(self):
#        # Testing spamdict operations...
#        import copy, xxsubtype as spam
#        def spamdict(d, memo=None):
#            import xxsubtype as spam
#            sd = spam.spamdict()
#            for k, v in list(d.items()):
#                sd[k] = v
#            return sd
#        # This is an ugly hack:
#        copy._deepcopy_dispatch[spam.spamdict] = spamdict
#
#        self.binop_test(spamdict({1:2,3:4}), 1, 1, "b in a", "__contains__")
#        self.binop_test(spamdict({1:2,3:4}), 2, 0, "b in a", "__contains__")
#        self.binop_test(spamdict({1:2,3:4}), 1, 2, "a[b]", "__getitem__")
#        d = spamdict({1:2,3:4})
#        l1 = []
#        for i in list(d.keys()):
#            l1.append(i)
#        l = []
#        for i in iter(d):
#            l.append(i)
#        self.assertEqual(l, l1)
#        l = []
#        for i in d.__iter__():
#            l.append(i)
#        self.assertEqual(l, l1)
#        l = []
#        for i in type(spamdict({})).__iter__(d):
#            l.append(i)
#        self.assertEqual(l, l1)
#        straightd = {1:2, 3:4}
#        spamd = spamdict(straightd)
#        self.unop_test(spamd, 2, "len(a)", "__len__")
#        self.unop_test(spamd, repr(straightd), "repr(a)", "__repr__")
#        self.set2op_test(spamdict({1:2,3:4}), 2, 3, spamdict({1:2,2:3,3:4}),
#                   "a[b]=c", "__setitem__")
#        # Test subclassing
#        class C(spam.spamdict):
#            def foo(self): return 1
#        a = C()
#        self.assertEqual(list(a.items()), [])
#        self.assertEqual(a.foo(), 1)
#        a['foo'] = 'bar'
#        self.assertEqual(list(a.items()), [('foo', 'bar')])
#        self.assertEqual(a.getstate(), 0)
#        a.setstate(100)
#        self.assertEqual(a.getstate(), 100)
#
