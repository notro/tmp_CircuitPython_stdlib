#import builtins
#import copyreg
#import gc
#import itertools
#import math
#import pickle
import sys
#import types
import unittest
#import weakref

from copy import deepcopy
#from test import support


#############################################################################   ###
class ClassPropertiesAndMethods(unittest.TestCase):
#    def test_str_of_str_subclass(self):
#        # Testing __str__ defined in subclass of str ...
#        import binascii
#        import io
#
#        class octetstring(str):
#            def __str__(self):
#                return binascii.b2a_hex(self.encode('ascii')).decode("ascii")
#            def __repr__(self):
#                return self + " repr"
#
#        o = octetstring('A')
#        self.assertEqual(type(o), octetstring)
#        self.assertEqual(type(str(o)), str)
#        self.assertEqual(type(repr(o)), str)
#        self.assertEqual(ord(o), 0x41)
#        self.assertEqual(str(o), '41')
#        self.assertEqual(repr(o), 'A repr')
#        self.assertEqual(o.__str__(), '41')
#        self.assertEqual(o.__repr__(), 'A repr')
#
#        capture = io.StringIO()
#        # Calling str() or not exercises different internal paths.
#        print(o, file=capture)
#        print(str(o), file=capture)
#        self.assertEqual(capture.getvalue(), '41\n41\n')
#        capture.close()
#
#    def test_keyword_arguments(self):
#        # Testing keyword arguments to __init__, __call__...
#        def f(a): return a
#        self.assertEqual(f.__call__(a=42), 42)
#        a = []
#        list.__init__(a, sequence=[0, 1, 2])
#        self.assertEqual(a, [0, 1, 2])
#
#    def test_recursive_call(self):
#        # Testing recursive __call__() by setting to instance of class...
#        class A(object):
#            pass
#
#        A.__call__ = A()
#        try:
#            A()()
#        except RuntimeError:
#            pass
#        else:
#            self.fail("Recursion limit should have been reached for __call__()")
#
#    def test_delete_hook(self):
#        # Testing __del__ hook...
#        log = []
#        class C(object):
#            def __del__(self):
#                log.append(1)
#        c = C()
#        self.assertEqual(log, [])
#        del c
#        support.gc_collect()
#        self.assertEqual(log, [1])
#
#        class D(object): pass
#        d = D()
#        try: del d[0]
#        except TypeError: pass
#        else: self.fail("invalid del() didn't raise TypeError")
#
    def test_hash_inheritance(self):
        # Testing hash of mutable subclasses...

        class mydict(dict):
            pass
        d = mydict()
        try:
            hash(d)
        except TypeError:
            pass
        else:
            self.fail("hash() of dict subclass should fail")

        class mylist(list):
            pass
        d = mylist()
        try:
            hash(d)
        except TypeError:
            pass
        else:
            self.fail("hash() of list subclass should fail")

    def test_str_operations(self):
        try: 'a' + 5
        except TypeError: pass
        else: self.fail("'' + 5 doesn't raise TypeError")

        try: ''.split('')
        except ValueError: pass
        else: self.fail("''.split('') doesn't raise ValueError")

        try: ''.join([0])
        except TypeError: pass
        else: self.fail("''.join([0]) doesn't raise TypeError")

        try: ''.rindex('5')
        except ValueError: pass
        else: self.fail("''.rindex('5') doesn't raise ValueError")

        try: '%(n)s' % None
        except TypeError: pass
        else: self.fail("'%(n)s' % None doesn't raise TypeError")

        try: '%(n' % {}
        except ValueError: pass
        else: self.fail("'%(n' % {} '' doesn't raise ValueError")

        try: '%*s' % ('abc')
        except TypeError: pass
        else: self.fail("'%*s' % ('abc') doesn't raise TypeError")

        try: '%*.*s' % ('abc', 5)
        except TypeError: pass
        else: self.fail("'%*.*s' % ('abc', 5) doesn't raise TypeError")

        try: '%s' % (1, 2)
        except TypeError: pass
        else: self.fail("'%s' % (1, 2) doesn't raise TypeError")

        try: '%' % None
        except ValueError: pass
        else: self.fail("'%' % None doesn't raise ValueError")

        self.assertEqual('534253'.isdigit(), 1)
        self.assertEqual('534253x'.isdigit(), 0)
        self.assertEqual('%c' % 5, '\x05')
        self.assertEqual('%c' % '5', '5')

    def test_deepcopy_recursive(self):
        # Testing deepcopy of recursive objects...
        class Node:
            pass
        a = Node()
        b = Node()
        a.b = b
        b.a = a
        z = deepcopy(a) # This blew up before

#    def test_unintialized_modules(self):
#        # Testing uninitialized module objects...
#        from types import ModuleType as M
#        m = M.__new__(M)
#        str(m)
#        self.assertNotHasAttr(m, "__name__")
#        self.assertNotHasAttr(m, "__file__")
#        self.assertNotHasAttr(m, "foo")
#        self.assertFalse(m.__dict__)   # None or {} are both reasonable answers
#        m.foo = 1
#        self.assertEqual(m.__dict__, {"foo": 1})
#
    def test_funny_new(self):
        # Testing __new__ returning something unexpected...
        class C(object):
            def __new__(cls, arg):
                if isinstance(arg, str): return [1, 2, 3]
                elif isinstance(arg, int): return object.__new__(D)
                else: return object.__new__(cls)
        class D(C):
            def __init__(self, arg):
                self.foo = arg
        self.assertEqual(C("1"), [1, 2, 3])
        self.assertEqual(D("1"), [1, 2, 3])
        d = D(None)
        self.assertEqual(d.foo, None)
        d = C(1)
        self.assertIsInstance(d, D)
#        self.assertEqual(d.foo, 1)
        d = D(1)
        self.assertIsInstance(d, D)
        self.assertEqual(d.foo, 1)

#    def test_imul_bug(self):
#        # Testing for __imul__ problems...
#        # SF bug 544647
#        class C(object):
#            def __imul__(self, other):
#                return (self, other)
#        x = C()
#        y = x
#        y *= 1.0
#        self.assertEqual(y, (x, 1.0))
#        y = x
#        y *= 2
#        self.assertEqual(y, (x, 2))
#        y = x
#        y *= 3
#        self.assertEqual(y, (x, 3))
#        y = x
#        y *= 1<<100
#        self.assertEqual(y, (x, 1<<100))
#        y = x
#        y *= None
#        self.assertEqual(y, (x, None))
#        y = x
#        y *= "foo"
#        self.assertEqual(y, (x, "foo"))
#
    def test_copy_setstate(self):
        # Testing that copy.*copy() correctly uses __setstate__...
        import copy
        class C(object):
            def __init__(self, foo=None):
                self.foo = foo
                self.__foo = foo
            def setfoo(self, foo=None):
                self.foo = foo
            def getfoo(self):
                return self.__foo
            def __getstate__(self):
                return [self.foo]
            def __setstate__(self_, lst):
                self.assertEqual(len(lst), 1)
                self_.__foo = self_.foo = lst[0]
        a = C(42)
        a.setfoo(24)
        self.assertEqual(a.foo, 24)
        self.assertEqual(a.getfoo(), 42)
        b = copy.copy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)
        b = copy.deepcopy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)

    def test_slices(self):
        # Testing cases with slices and overridden __getitem__ ...

        # Strings
        self.assertEqual("hello"[:4], "hell")
        self.assertEqual("hello"[slice(4)], "hell")
#        self.assertEqual(str.__getitem__("hello", slice(4)), "hell")
#        class S(str):
#            def __getitem__(self, x):
#                return str.__getitem__(self, x)
#        self.assertEqual(S("hello")[:4], "hell")
#        self.assertEqual(S("hello")[slice(4)], "hell")
#        self.assertEqual(S("hello").__getitem__(slice(4)), "hell")
        # Tuples
        self.assertEqual((1,2,3)[:2], (1,2))
        self.assertEqual((1,2,3)[slice(2)], (1,2))
#        self.assertEqual(tuple.__getitem__((1,2,3), slice(2)), (1,2))
#        class T(tuple):
#            def __getitem__(self, x):
#                return tuple.__getitem__(self, x)
#        self.assertEqual(T((1,2,3))[:2], (1,2))
#        self.assertEqual(T((1,2,3))[slice(2)], (1,2))
#        self.assertEqual(T((1,2,3)).__getitem__(slice(2)), (1,2))
        # Lists
        self.assertEqual([1,2,3][:2], [1,2])
        self.assertEqual([1,2,3][slice(2)], [1,2])
#        self.assertEqual(list.__getitem__([1,2,3], slice(2)), [1,2])
#        class L(list):
#            def __getitem__(self, x):
#                return list.__getitem__(self, x)
#        self.assertEqual(L([1,2,3])[:2], [1,2])
#        self.assertEqual(L([1,2,3])[slice(2)], [1,2])
#        self.assertEqual(L([1,2,3]).__getitem__(slice(2)), [1,2])
#        # Now do lists and __setitem__
#        a = L([1,2,3])
#        a[slice(1, 3)] = [3,2]
#        self.assertEqual(a, [1,3,2])
#        a[slice(0, 2, 1)] = [3,1]
#        self.assertEqual(a, [3,1,2])
#        a.__setitem__(slice(1, 3), [2,1])
#        self.assertEqual(a, [3,2,1])
#        a.__setitem__(slice(0, 2, 1), [2,3])
#        self.assertEqual(a, [2,3,1])

#    def test_subtype_resurrection(self):
#        # Testing resurrection of new-style instance...
#
#        class C(object):
#            container = []
#
#            def __del__(self):
#                # resurrect the instance
#                C.container.append(self)
#
#        c = C()
#        c.attr = 42
#
#        # The most interesting thing here is whether this blows up, due to
#        # flawed GC tracking logic in typeobject.c's call_finalizer() (a 2.2.1
#        # bug).
#        del c
#
#        support.gc_collect()
#        self.assertEqual(len(C.container), 1)
#
#        # Make c mortal again, so that the test framework with -l doesn't report
#        # it as a leak.
#        del C.__del__
#
#    def test_slots_trash(self):
#        # Testing slot trash...
#        # Deallocating deeply nested slotted trash caused stack overflows
#        class trash(object):
#            __slots__ = ['x']
#            def __init__(self, x):
#                self.x = x
#        o = None
#        for i in range(50000):
#            o = trash(o)
#        del o
#
#    def test_slots_multiple_inheritance(self):
#        # SF bug 575229, multiple inheritance w/ slots dumps core
#        class A(object):
#            __slots__=()
#        class B(object):
#            pass
#        class C(A,B) :
#            __slots__=()
#        if support.check_impl_detail():
#            self.assertEqual(C.__basicsize__, B.__basicsize__)
#        self.assertHasAttr(C, '__dict__')
#        self.assertHasAttr(C, '__weakref__')
#        C().x = 2
#
    def test_rmul(self):
        # Testing correct invocation of __rmul__...
        # SF patch 592646
        class C(object):
            def __mul__(self, other):
                return "mul"
            def __rmul__(self, other):
                return "rmul"
        a = C()
        self.assertEqual(a*2, "mul")
        self.assertEqual(a*2.2, "mul")
        self.assertEqual(2*a, "rmul")
        self.assertEqual(2.2*a, "rmul")

#    def test_ipow(self):
#        # Testing correct invocation of __ipow__...
#        # [SF bug 620179]
#        class C(object):
#            def __ipow__(self, other):
#                pass
#        a = C()
#        a **= 2
#
#    def test_mutable_bases(self):
#        # Testing mutable bases...
#
#        # stuff that should work:
#        class C(object):
#            pass
#        class C2(object):
#            def __getattribute__(self, attr):
#                if attr == 'a':
#                    return 2
#                else:
#                    return super(C2, self).__getattribute__(attr)
#            def meth(self):
#                return 1
#        class D(C):
#            pass
#        class E(D):
#            pass
#        d = D()
#        e = E()
#        D.__bases__ = (C,)
#        D.__bases__ = (C2,)
#        self.assertEqual(d.meth(), 1)
#        self.assertEqual(e.meth(), 1)
#        self.assertEqual(d.a, 2)
#        self.assertEqual(e.a, 2)
#        self.assertEqual(C2.__subclasses__(), [D])
#
#        try:
#            del D.__bases__
#        except (TypeError, AttributeError):
#            pass
#        else:
#            self.fail("shouldn't be able to delete .__bases__")
#
#        try:
#            D.__bases__ = ()
#        except TypeError as msg:
#            if str(msg) == "a new-style class can't have only classic bases":
#                self.fail("wrong error message for .__bases__ = ()")
#        else:
#            self.fail("shouldn't be able to set .__bases__ to ()")
#
#        try:
#            D.__bases__ = (D,)
#        except TypeError:
#            pass
#        else:
#            # actually, we'll have crashed by here...
#            self.fail("shouldn't be able to create inheritance cycles")
#
#        try:
#            D.__bases__ = (C, C)
#        except TypeError:
#            pass
#        else:
#            self.fail("didn't detect repeated base classes")
#
#        try:
#            D.__bases__ = (E,)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't be able to create inheritance cycles")
#
#    def test_builtin_bases(self):
#        # Make sure all the builtin types can have their base queried without
#        # segfaulting. See issue #5787.
#        builtin_types = [tp for tp in builtins.__dict__.values()
#                         if isinstance(tp, type)]
#        for tp in builtin_types:
#            object.__getattribute__(tp, "__bases__")
#            if tp is not object:
#                self.assertEqual(len(tp.__bases__), 1, tp)
#
#        class L(list):
#            pass
#
#        class C(object):
#            pass
#
#        class D(C):
#            pass
#
#        try:
#            L.__bases__ = (dict,)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't turn list subclass into dict subclass")
#
#        try:
#            list.__bases__ = (dict,)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't be able to assign to list.__bases__")
#
#        try:
#            D.__bases__ = (C, list)
#        except TypeError:
#            pass
#        else:
#            assert 0, "best_base calculation found wanting"
#
#    def test_unsubclassable_types(self):
#        with self.assertRaises(TypeError):
#            class X(type(None)):
#                pass
#        with self.assertRaises(TypeError):
#            class X(object, type(None)):
#                pass
#        with self.assertRaises(TypeError):
#            class X(type(None), object):
#                pass
#        class O(object):
#            pass
#        with self.assertRaises(TypeError):
#            class X(O, type(None)):
#                pass
#        with self.assertRaises(TypeError):
#            class X(type(None), O):
#                pass
#
#        class X(object):
#            pass
#        with self.assertRaises(TypeError):
#            X.__bases__ = type(None),
#        with self.assertRaises(TypeError):
#            X.__bases__ = object, type(None)
#        with self.assertRaises(TypeError):
#            X.__bases__ = type(None), object
#        with self.assertRaises(TypeError):
#            X.__bases__ = O, type(None)
#        with self.assertRaises(TypeError):
#            X.__bases__ = type(None), O
#
#    def test_mutable_bases_with_failing_mro(self):
#        # Testing mutable bases with failing mro...
#        class WorkOnce(type):
#            def __new__(self, name, bases, ns):
#                self.flag = 0
#                return super(WorkOnce, self).__new__(WorkOnce, name, bases, ns)
#            def mro(self):
#                if self.flag > 0:
#                    raise RuntimeError("bozo")
#                else:
#                    self.flag += 1
#                    return type.mro(self)
#
#        class WorkAlways(type):
#            def mro(self):
#                # this is here to make sure that .mro()s aren't called
#                # with an exception set (which was possible at one point).
#                # An error message will be printed in a debug build.
#                # What's a good way to test for this?
#                return type.mro(self)
#
#        class C(object):
#            pass
#
#        class C2(object):
#            pass
#
#        class D(C):
#            pass
#
#        class E(D):
#            pass
#
#        class F(D, metaclass=WorkOnce):
#            pass
#
#        class G(D, metaclass=WorkAlways):
#            pass
#
#        # Immediate subclasses have their mro's adjusted in alphabetical
#        # order, so E's will get adjusted before adjusting F's fails.  We
#        # check here that E's gets restored.
#
#        E_mro_before = E.__mro__
#        D_mro_before = D.__mro__
#
#        try:
#            D.__bases__ = (C2,)
#        except RuntimeError:
#            self.assertEqual(E.__mro__, E_mro_before)
#            self.assertEqual(D.__mro__, D_mro_before)
#        else:
#            self.fail("exception not propagated")
#
#    def test_mutable_bases_catch_mro_conflict(self):
#        # Testing mutable bases catch mro conflict...
#        class A(object):
#            pass
#
#        class B(object):
#            pass
#
#        class C(A, B):
#            pass
#
#        class D(A, B):
#            pass
#
#        class E(C, D):
#            pass
#
#        try:
#            C.__bases__ = (B, A)
#        except TypeError:
#            pass
#        else:
#            self.fail("didn't catch MRO conflict")
#
#    def test_mutable_names(self):
#        # Testing mutable names...
#        class C(object):
#            pass
#
#        # C.__module__ could be 'test_descr' or '__main__'
#        mod = C.__module__
#
#        C.__name__ = 'D'
#        self.assertEqual((C.__module__, C.__name__), (mod, 'D'))
#
#        C.__name__ = 'D.E'
#        self.assertEqual((C.__module__, C.__name__), (mod, 'D.E'))
#
#    def test_evil_type_name(self):
#        # A badly placed Py_DECREF in type_set_name led to arbitrary code
#        # execution while the type structure was not in a sane state, and a
#        # possible segmentation fault as a result.  See bug #16447.
#        class Nasty(str):
#            def __del__(self):
#                C.__name__ = "other"
#
#        class C:
#            pass
#
#        C.__name__ = Nasty("abc")
#        C.__name__ = "normal"
#
    def test_subclass_right_op(self):
        # Testing correct dispatch of subclass overloading __r<op>__...

        # This code tests various cases where right-dispatch of a subclass
        # should be preferred over left-dispatch of a base class.

        # Case 1: subclass of int; this tests code in abstract.c::binary_op1()

        class B(int):
            def __floordiv__(self, other):
                return "B.__floordiv__"
            def __rfloordiv__(self, other):
                return "B.__rfloordiv__"

        self.assertEqual(B(1) // 1, "B.__floordiv__")
        self.assertEqual(1 // B(1), "B.__rfloordiv__")

        # Case 2: subclass of object; this is just the baseline for case 3

        class C(object):
            def __floordiv__(self, other):
                return "C.__floordiv__"
            def __rfloordiv__(self, other):
                return "C.__rfloordiv__"

        self.assertEqual(C() // 1, "C.__floordiv__")
        self.assertEqual(1 // C(), "C.__rfloordiv__")

        # Case 3: subclass of new-style class; here it gets interesting

        class D(C):
            def __floordiv__(self, other):
                return "D.__floordiv__"
            def __rfloordiv__(self, other):
                return "D.__rfloordiv__"

        self.assertEqual(D() // C(), "D.__floordiv__")
#        self.assertEqual(C() // D(), "D.__rfloordiv__")

        # Case 4: this didn't work right in 2.2.2 and 2.3a1

        class E(C):
            pass

        self.assertEqual(E.__rfloordiv__, C.__rfloordiv__)

        self.assertEqual(E() // 1, "C.__floordiv__")
        self.assertEqual(1 // E(), "C.__rfloordiv__")
        self.assertEqual(E() // C(), "C.__floordiv__")
        self.assertEqual(C() // E(), "C.__floordiv__") # This one would fail

#    @support.impl_detail("testing an internal kind of method object")
#    def test_meth_class_get(self):
#        # Testing __get__ method of METH_CLASS C methods...
#        # Full coverage of descrobject.c::classmethod_get()
#
#        # Baseline
#        arg = [1, 2, 3]
#        res = {1: None, 2: None, 3: None}
#        self.assertEqual(dict.fromkeys(arg), res)
#        self.assertEqual({}.fromkeys(arg), res)
#
#        # Now get the descriptor
#        descr = dict.__dict__["fromkeys"]
#
#        # More baseline using the descriptor directly
#        self.assertEqual(descr.__get__(None, dict)(arg), res)
#        self.assertEqual(descr.__get__({})(arg), res)
#
#        # Now check various error cases
#        try:
#            descr.__get__(None, None)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't have allowed descr.__get__(None, None)")
#        try:
#            descr.__get__(42)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't have allowed descr.__get__(42)")
#        try:
#            descr.__get__(None, 42)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't have allowed descr.__get__(None, 42)")
#        try:
#            descr.__get__(None, int)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't have allowed descr.__get__(None, int)")
#
#    def test_isinst_isclass(self):
#        # Testing proxy isinstance() and isclass()...
#        class Proxy(object):
#            def __init__(self, obj):
#                self.__obj = obj
#            def __getattribute__(self, name):
#                if name.startswith("_Proxy__"):
#                    return object.__getattribute__(self, name)
#                else:
#                    return getattr(self.__obj, name)
#        # Test with a classic class
#        class C:
#            pass
#        a = C()
#        pa = Proxy(a)
#        self.assertIsInstance(a, C)  # Baseline
#        self.assertIsInstance(pa, C) # Test
#        # Test with a classic subclass
#        class D(C):
#            pass
#        a = D()
#        pa = Proxy(a)
#        self.assertIsInstance(a, C)  # Baseline
#        self.assertIsInstance(pa, C) # Test
#        # Test with a new-style class
#        class C(object):
#            pass
#        a = C()
#        pa = Proxy(a)
#        self.assertIsInstance(a, C)  # Baseline
#        self.assertIsInstance(pa, C) # Test
#        # Test with a new-style subclass
#        class D(C):
#            pass
#        a = D()
#        pa = Proxy(a)
#        self.assertIsInstance(a, C)  # Baseline
#        self.assertIsInstance(pa, C) # Test
#
#    def test_proxy_super(self):
#        # Testing super() for a proxy object...
#        class Proxy(object):
#            def __init__(self, obj):
#                self.__obj = obj
#            def __getattribute__(self, name):
#                if name.startswith("_Proxy__"):
#                    return object.__getattribute__(self, name)
#                else:
#                    return getattr(self.__obj, name)
#
#        class B(object):
#            def f(self):
#                return "B.f"
#
#        class C(B):
#            def f(self):
#                return super(C, self).f() + "->C.f"
#
#        obj = C()
#        p = Proxy(obj)
#        self.assertEqual(C.__dict__["f"](p), "B.f->C.f")
#
#    def test_carloverre(self):
#        # Testing prohibition of Carlo Verre's hack...
#        try:
#            object.__setattr__(str, "foo", 42)
#        except TypeError:
#            pass
#        else:
#            self.fail("Carlo Verre __setattr__ succeeded!")
#        try:
#            object.__delattr__(str, "lower")
#        except TypeError:
#            pass
#        else:
#            self.fail("Carlo Verre __delattr__ succeeded!")
#
#    def test_weakref_segfault(self):
#        # Testing weakref segfault...
#        # SF 742911
#        import weakref
#
#        class Provoker:
#            def __init__(self, referrent):
#                self.ref = weakref.ref(referrent)
#
#            def __del__(self):
#                x = self.ref()
#
#        class Oops(object):
#            pass
#
#        o = Oops()
#        o.whatever = Provoker(o)
#        del o
#
#    def test_wrapper_segfault(self):
#        # SF 927248: deeply nested wrappers could cause stack overflow
#        f = lambda:None
#        for i in range(1000000):
#            f = f.__call__
#        f = None
#
#    def test_file_fault(self):
#        # Testing sys.stdout is changed in getattr...
#        test_stdout = sys.stdout
#        class StdoutGuard:
#            def __getattr__(self, attr):
#                sys.stdout = sys.__stdout__
#                raise RuntimeError("Premature access to sys.stdout.%s" % attr)
#        sys.stdout = StdoutGuard()
#        try:
#            print("Oops!")
#        except RuntimeError:
#            pass
#        finally:
#            sys.stdout = test_stdout
#
#    def test_vicious_descriptor_nonsense(self):
#        # Testing vicious_descriptor_nonsense...
#
#        # A potential segfault spotted by Thomas Wouters in mail to
#        # python-dev 2003-04-17, turned into an example & fixed by Michael
#        # Hudson just less than four months later...
#
#        class Evil(object):
#            def __hash__(self):
#                return hash('attr')
#            def __eq__(self, other):
#                del C.attr
#                return 0
#
#        class Descr(object):
#            def __get__(self, ob, type=None):
#                return 1
#
#        class C(object):
#            attr = Descr()
#
#        c = C()
#        c.__dict__[Evil()] = 0
#
#        self.assertEqual(c.attr, 1)
#        # this makes a crash more likely:
#        support.gc_collect()
#        self.assertNotHasAttr(c, 'attr')
#
    def test_init(self):
        # SF 1155938
        class Foo(object):
            def __init__(self):
                return 10
        try:
            Foo()
        except TypeError:
            pass
        else:
            self.fail("did not test __init__() for None return")

#    def test_method_wrapper(self):
#        # Testing method-wrapper objects...
#        # <type 'method-wrapper'> did not support any reflection before 2.5
#
#        # XXX should methods really support __eq__?
#
#        l = []
#        self.assertEqual(l.__add__, l.__add__)
#        self.assertEqual(l.__add__, [].__add__)
#        self.assertNotEqual(l.__add__, [5].__add__)
#        self.assertNotEqual(l.__add__, l.__mul__)
#        self.assertEqual(l.__add__.__name__, '__add__')
#        if hasattr(l.__add__, '__self__'):
#            # CPython
#            self.assertIs(l.__add__.__self__, l)
#            self.assertIs(l.__add__.__objclass__, list)
#        else:
#            # Python implementations where [].__add__ is a normal bound method
#            self.assertIs(l.__add__.im_self, l)
#            self.assertIs(l.__add__.im_class, list)
#        self.assertEqual(l.__add__.__doc__, list.__add__.__doc__)
#        try:
#            hash(l.__add__)
#        except TypeError:
#            pass
#        else:
#            self.fail("no TypeError from hash([].__add__)")
#
#        t = ()
#        t += (7,)
#        self.assertEqual(t.__add__, (7,).__add__)
#        self.assertEqual(hash(t.__add__), hash((7,).__add__))
#
    def test_not_implemented(self):
        # Testing NotImplemented...
        # all binary methods should be able to return a NotImplemented
        import operator

        def specialmethod(self, other):
            return NotImplemented

        def check(expr, x, y):
            try:
                exec(expr, {'x': x, 'y': y, 'operator': operator})
            except TypeError:
                pass
            else:
                self.fail("no TypeError from %r" % (expr,))

        N1 = sys.maxsize + 1    # might trigger OverflowErrors instead of
                                # TypeErrors
        N2 = sys.maxsize         # if sizeof(int) < sizeof(long), might trigger
                                #   ValueErrors instead of TypeErrors
        for name, expr, iexpr in [
                ('__add__',      'x + y',                   'x += y'),
                ('__sub__',      'x - y',                   'x -= y'),
                ('__mul__',      'x * y',                   'x *= y'),
                ('__truediv__',  'x / y',                   'x /= y'),
                ('__floordiv__', 'x // y',                  'x //= y'),
                ('__mod__',      'x % y',                   'x %= y'),
                ('__divmod__',   'divmod(x, y)',            None),
                ('__pow__',      'x ** y',                  'x **= y'),
                ('__lshift__',   'x << y',                  'x <<= y'),
                ('__rshift__',   'x >> y',                  'x >>= y'),
                ('__and__',      'x & y',                   'x &= y'),
                ('__or__',       'x | y',                   'x |= y'),
                ('__xor__',      'x ^ y',                   'x ^= y')]:
            rname = '__r' + name[2:]
            A = type('A', (), {name: specialmethod})
            a = A()
            check(expr, a, a)
            check(expr, a, N1)
            check(expr, a, N2)
            if iexpr:
                check(iexpr, a, a)
                check(iexpr, a, N1)
                check(iexpr, a, N2)
                iname = '__i' + name[2:]
                C = type('C', (), {iname: specialmethod})
                c = C()
                check(iexpr, c, a)
                check(iexpr, c, N1)
                check(iexpr, c, N2)

    def test_assign_slice(self):
        # ceval.c's assign_slice used to check for
        # tp->tp_as_sequence->sq_slice instead of
        # tp->tp_as_sequence->sq_ass_slice

        class C(object):
            def __setitem__(self, idx, value):
                self.value = value

        c = C()
        c[1:2] = 3
        self.assertEqual(c.value, 3)

#    def test_set_and_no_get(self):
#        # See
#        # http://mail.python.org/pipermail/python-dev/2010-January/095637.html
#        class Descr(object):
#
#            def __init__(self, name):
#                self.name = name
#
#            def __set__(self, obj, value):
#                obj.__dict__[self.name] = value
#        descr = Descr("a")
#
#        class X(object):
#            a = descr
#
#        x = X()
#        self.assertIs(x.a, descr)
#        x.a = 42
#        self.assertEqual(x.a, 42)
#
#        # Also check type_getattro for correctness.
#        class Meta(type):
#            pass
#        class X(metaclass=Meta):
#            pass
#        X.a = 42
#        Meta.a = Descr("a")
#        self.assertEqual(X.a, 42)
#
#    def test_getattr_hooks(self):
#        # issue 4230
#
#        class Descriptor(object):
#            counter = 0
#            def __get__(self, obj, objtype=None):
#                def getter(name):
#                    self.counter += 1
#                    raise AttributeError(name)
#                return getter
#
#        descr = Descriptor()
#        class A(object):
#            __getattribute__ = descr
#        class B(object):
#            __getattr__ = descr
#        class C(object):
#            __getattribute__ = descr
#            __getattr__ = descr
#
#        self.assertRaises(AttributeError, getattr, A(), "attr")
#        self.assertEqual(descr.counter, 1)
#        self.assertRaises(AttributeError, getattr, B(), "attr")
#        self.assertEqual(descr.counter, 2)
#        self.assertRaises(AttributeError, getattr, C(), "attr")
#        self.assertEqual(descr.counter, 4)
#
#        class EvilGetattribute(object):
#            # This used to segfault
#            def __getattr__(self, name):
#                raise AttributeError(name)
#            def __getattribute__(self, name):
#                del EvilGetattribute.__getattr__
#                for i in range(5):
#                    gc.collect()
#                raise AttributeError(name)
#
#        self.assertRaises(AttributeError, getattr, EvilGetattribute(), "attr")
#
#    def test_type___getattribute__(self):
#        self.assertRaises(TypeError, type.__getattribute__, list, type)
#
#    def test_abstractmethods(self):
#        # type pretends not to have __abstractmethods__.
#        self.assertRaises(AttributeError, getattr, type, "__abstractmethods__")
#        class meta(type):
#            pass
#        self.assertRaises(AttributeError, getattr, meta, "__abstractmethods__")
#        class X(object):
#            pass
#        with self.assertRaises(AttributeError):
#            del X.__abstractmethods__
#
    def test_proxy_call(self):
        class FakeStr:
            __class__ = str

        fake_str = FakeStr()
#        # isinstance() reads __class__
#        self.assertIsInstance(fake_str, str)

        # call a method descriptor
        with self.assertRaises(TypeError):
            str.split(fake_str)
#
#        # call a slot wrapper descriptor
#        with self.assertRaises(TypeError):
#            str.__add__(fake_str, "abc")

#    def test_repr_as_str(self):
#        # Issue #11603: crash or infinite loop when rebinding __str__ as
#        # __repr__.
#        class Foo:
#            pass
#        Foo.__repr__ = Foo.__str__
#        foo = Foo()
#        self.assertRaises(RuntimeError, str, foo)
#        self.assertRaises(RuntimeError, repr, foo)
#
#    def test_mixing_slot_wrappers(self):
#        class X(dict):
#            __setattr__ = dict.__setitem__
#        x = X()
#        x.y = 42
#        self.assertEqual(x["y"], 42)
#
#    def test_slot_shadows_class_variable(self):
#        with self.assertRaises(ValueError) as cm:
#            class X:
#                __slots__ = ["foo"]
#                foo = None
#        m = str(cm.exception)
#        self.assertEqual("'foo' in __slots__ conflicts with class variable", m)
#
#    def test_set_doc(self):
#        class X:
#            "elephant"
#        X.__doc__ = "banana"
#        self.assertEqual(X.__doc__, "banana")
#        with self.assertRaises(TypeError) as cm:
#            type(list).__dict__["__doc__"].__set__(list, "blah")
#        self.assertIn("can't set list.__doc__", str(cm.exception))
#        with self.assertRaises(TypeError) as cm:
#            type(X).__dict__["__doc__"].__delete__(X)
#        self.assertIn("can't delete X.__doc__", str(cm.exception))
#        self.assertEqual(X.__doc__, "banana")
#
#    def test_qualname(self):
#        descriptors = [str.lower, complex.real, float.real, int.__add__]
#        types = ['method', 'member', 'getset', 'wrapper']
#
#        # make sure we have an example of each type of descriptor
#        for d, n in zip(descriptors, types):
#            self.assertEqual(type(d).__name__, n + '_descriptor')
#
#        for d in descriptors:
#            qualname = d.__objclass__.__qualname__ + '.' + d.__name__
#            self.assertEqual(d.__qualname__, qualname)
#
#        self.assertEqual(str.lower.__qualname__, 'str.lower')
#        self.assertEqual(complex.real.__qualname__, 'complex.real')
#        self.assertEqual(float.real.__qualname__, 'float.real')
#        self.assertEqual(int.__add__.__qualname__, 'int.__add__')
#
#        class X:
#            pass
#        with self.assertRaises(TypeError):
#            del X.__qualname__
#
#        self.assertRaises(TypeError, type.__dict__['__qualname__'].__set__,
#                          str, 'Oink')
#
#        global Y
#        class Y:
#            class Inside:
#                pass
#        self.assertEqual(Y.__qualname__, 'Y')
#        self.assertEqual(Y.Inside.__qualname__, 'Y.Inside')
#
#    def test_qualname_dict(self):
#        ns = {'__qualname__': 'some.name'}
#        tp = type('Foo', (), ns)
#        self.assertEqual(tp.__qualname__, 'some.name')
#        self.assertNotIn('__qualname__', tp.__dict__)
#        self.assertEqual(ns, {'__qualname__': 'some.name'})
#
#        ns = {'__qualname__': 1}
#        self.assertRaises(TypeError, type, 'Foo', (), ns)
#
#    def test_cycle_through_dict(self):
#        # See bug #1469629
#        class X(dict):
#            def __init__(self):
#                dict.__init__(self)
#                self.__dict__ = self
#        x = X()
#        x.attr = 42
#        wr = weakref.ref(x)
#        del x
#        support.gc_collect()
#        self.assertIsNone(wr())
#        for o in gc.get_objects():
#            self.assertIsNot(type(o), X)
#
    def test_object_new_and_init_with_parameters(self):
        # See issue #1683368
#        class OverrideNeither:
#            pass
#        self.assertRaises(TypeError, OverrideNeither, 1)
#        self.assertRaises(TypeError, OverrideNeither, kw=1)
        class OverrideNew:
            def __new__(cls, foo, kw=0, *args, **kwds):
                return object.__new__(cls, *args, **kwds)
#        class OverrideInit:
#            def __init__(self, foo, kw=0, *args, **kwargs):
#                return object.__init__(self, *args, **kwargs)
#        class OverrideBoth(OverrideNew, OverrideInit):
#            pass
#        for case in OverrideNew, OverrideInit, OverrideBoth:
        for case in (OverrideNew, ):                                            ###
            print('\ncase:', case)
            case(1)
            case(1, kw=2)
            self.assertRaises(TypeError, case, 1, 2, 3)
            self.assertRaises(TypeError, case, 1, 2, foo=3)

#    def test_subclassing_does_not_duplicate_dict_descriptors(self):
#        class Base:
#            pass
#        class Sub(Base):
#            pass
#        self.assertIn("__dict__", Base.__dict__)
#        self.assertNotIn("__dict__", Sub.__dict__)
#
#
#class DictProxyTests(unittest.TestCase):
#    def setUp(self):
#        class C(object):
#            def meth(self):
#                pass
#        self.C = C
#
#    @unittest.skipIf(hasattr(sys, 'gettrace') and sys.gettrace(),
#                        'trace function introduces __local__')
#    def test_iter_keys(self):
#        # Testing dict-proxy keys...
#        it = self.C.__dict__.keys()
#        self.assertNotIsInstance(it, list)
#        keys = list(it)
#        keys.sort()
#        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
#                                '__weakref__', 'meth'])
#
#    @unittest.skipIf(hasattr(sys, 'gettrace') and sys.gettrace(),
#                        'trace function introduces __local__')
#    def test_iter_values(self):
#        # Testing dict-proxy values...
#        it = self.C.__dict__.values()
#        self.assertNotIsInstance(it, list)
#        values = list(it)
#        self.assertEqual(len(values), 5)
#
#    @unittest.skipIf(hasattr(sys, 'gettrace') and sys.gettrace(),
#                        'trace function introduces __local__')
#    def test_iter_items(self):
#        # Testing dict-proxy iteritems...
#        it = self.C.__dict__.items()
#        self.assertNotIsInstance(it, list)
#        keys = [item[0] for item in it]
#        keys.sort()
#        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
#                                '__weakref__', 'meth'])
#
#    def test_dict_type_with_metaclass(self):
#        # Testing type of __dict__ when metaclass set...
#        class B(object):
#            pass
#        class M(type):
#            pass
#        class C(metaclass=M):
#            # In 2.3a1, C.__dict__ was a real dict rather than a dict proxy
#            pass
#        self.assertEqual(type(C.__dict__), type(B.__dict__))
#
#    def test_repr(self):
#        # Testing mappingproxy.__repr__.
#        # We can't blindly compare with the repr of another dict as ordering
#        # of keys and values is arbitrary and may differ.
#        r = repr(self.C.__dict__)
#        self.assertTrue(r.startswith('mappingproxy('), r)
#        self.assertTrue(r.endswith(')'), r)
#        for k, v in self.C.__dict__.items():
#            self.assertIn('{!r}: {!r}'.format(k, v), r)
#
#
#class PTypesLongInitTest(unittest.TestCase):
#    # This is in its own TestCase so that it can be run before any other tests.
#    def test_pytype_long_ready(self):
#        # Testing SF bug 551412 ...
#
#        # This dumps core when SF bug 551412 isn't fixed --
#        # but only when test_descr.py is run separately.
#        # (That can't be helped -- as soon as PyType_Ready()
#        # is called for PyLong_Type, the bug is gone.)
#        class UserLong(object):
#            def __pow__(self, *args):
#                pass
#        try:
#            pow(0, UserLong(), 0)
#        except:
#            pass
#
#        # Another segfault only when run early
#        # (before PyType_Ready(tuple) is called)
#        type.mro(tuple)
#
#
#class MiscTests(unittest.TestCase):
#    def test_type_lookup_mro_reference(self):
#        # Issue #14199: _PyType_Lookup() has to keep a strong reference to
#        # the type MRO because it may be modified during the lookup, if
#        # __bases__ is set during the lookup for example.
#        class MyKey(object):
#            def __hash__(self):
#                return hash('mykey')
#
#            def __eq__(self, other):
#                X.__bases__ = (Base2,)
#
#        class Base(object):
#            mykey = 'from Base'
#            mykey2 = 'from Base'
#
#        class Base2(object):
#            mykey = 'from Base2'
#            mykey2 = 'from Base2'
#
#        X = type('X', (Base,), {MyKey(): 5})
#        # mykey is read from Base
#        self.assertEqual(X.mykey, 'from Base')
#        # mykey2 is read from Base2 because MyKey.__eq__ has set __bases__
#        self.assertEqual(X.mykey2, 'from Base2')
#
#
#class PicklingTests(unittest.TestCase):
#
#    def _check_reduce(self, proto, obj, args=(), kwargs={}, state=None,
#                      listitems=None, dictitems=None):
#        if proto >= 4:
#            reduce_value = obj.__reduce_ex__(proto)
#            self.assertEqual(reduce_value[:3],
#                             (copyreg.__newobj_ex__,
#                              (type(obj), args, kwargs),
#                              state))
#            if listitems is not None:
#                self.assertListEqual(list(reduce_value[3]), listitems)
#            else:
#                self.assertIsNone(reduce_value[3])
#            if dictitems is not None:
#                self.assertDictEqual(dict(reduce_value[4]), dictitems)
#            else:
#                self.assertIsNone(reduce_value[4])
#        elif proto >= 2:
#            reduce_value = obj.__reduce_ex__(proto)
#            self.assertEqual(reduce_value[:3],
#                             (copyreg.__newobj__,
#                              (type(obj),) + args,
#                              state))
#            if listitems is not None:
#                self.assertListEqual(list(reduce_value[3]), listitems)
#            else:
#                self.assertIsNone(reduce_value[3])
#            if dictitems is not None:
#                self.assertDictEqual(dict(reduce_value[4]), dictitems)
#            else:
#                self.assertIsNone(reduce_value[4])
#        else:
#            base_type = type(obj).__base__
#            reduce_value = (copyreg._reconstructor,
#                            (type(obj),
#                             base_type,
#                             None if base_type is object else base_type(obj)))
#            if state is not None:
#                reduce_value += (state,)
#            self.assertEqual(obj.__reduce_ex__(proto), reduce_value)
#            self.assertEqual(obj.__reduce__(), reduce_value)
#
#    def test_reduce(self):
#        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
#        args = (-101, "spam")
#        kwargs = {'bacon': -201, 'fish': -301}
#        state = {'cheese': -401}
#
#        class C1:
#            def __getnewargs__(self):
#                return args
#        obj = C1()
#        for proto in protocols:
#            self._check_reduce(proto, obj, args)
#
#        for name, value in state.items():
#            setattr(obj, name, value)
#        for proto in protocols:
#            self._check_reduce(proto, obj, args, state=state)
#
#        class C2:
#            def __getnewargs__(self):
#                return "bad args"
#        obj = C2()
#        for proto in protocols:
#            if proto >= 2:
#                with self.assertRaises(TypeError):
#                    obj.__reduce_ex__(proto)
#
#        class C3:
#            def __getnewargs_ex__(self):
#                return (args, kwargs)
#        obj = C3()
#        for proto in protocols:
#            if proto >= 4:
#                self._check_reduce(proto, obj, args, kwargs)
#            elif proto >= 2:
#                with self.assertRaises(ValueError):
#                    obj.__reduce_ex__(proto)
#
#        class C4:
#            def __getnewargs_ex__(self):
#                return (args, "bad dict")
#        class C5:
#            def __getnewargs_ex__(self):
#                return ("bad tuple", kwargs)
#        class C6:
#            def __getnewargs_ex__(self):
#                return ()
#        class C7:
#            def __getnewargs_ex__(self):
#                return "bad args"
#        for proto in protocols:
#            for cls in C4, C5, C6, C7:
#                obj = cls()
#                if proto >= 2:
#                    with self.assertRaises((TypeError, ValueError)):
#                        obj.__reduce_ex__(proto)
#
#        class C9:
#            def __getnewargs_ex__(self):
#                return (args, {})
#        obj = C9()
#        for proto in protocols:
#            self._check_reduce(proto, obj, args)
#
#        class C10:
#            def __getnewargs_ex__(self):
#                raise IndexError
#        obj = C10()
#        for proto in protocols:
#            if proto >= 2:
#                with self.assertRaises(IndexError):
#                    obj.__reduce_ex__(proto)
#
#        class C11:
#            def __getstate__(self):
#                return state
#        obj = C11()
#        for proto in protocols:
#            self._check_reduce(proto, obj, state=state)
#
#        class C12:
#            def __getstate__(self):
#                return "not dict"
#        obj = C12()
#        for proto in protocols:
#            self._check_reduce(proto, obj, state="not dict")
#
#        class C13:
#            def __getstate__(self):
#                raise IndexError
#        obj = C13()
#        for proto in protocols:
#            with self.assertRaises(IndexError):
#                obj.__reduce_ex__(proto)
#            if proto < 2:
#                with self.assertRaises(IndexError):
#                    obj.__reduce__()
#
#        class C14:
#            __slots__ = tuple(state)
#            def __init__(self):
#                for name, value in state.items():
#                    setattr(self, name, value)
#
#        obj = C14()
#        for proto in protocols:
#            if proto >= 2:
#                self._check_reduce(proto, obj, state=(None, state))
#            else:
#                with self.assertRaises(TypeError):
#                    obj.__reduce_ex__(proto)
#                with self.assertRaises(TypeError):
#                    obj.__reduce__()
#
#        class C15(dict):
#            pass
#        obj = C15({"quebec": -601})
#        for proto in protocols:
#            self._check_reduce(proto, obj, dictitems=dict(obj))
#
#        class C16(list):
#            pass
#        obj = C16(["yukon"])
#        for proto in protocols:
#            self._check_reduce(proto, obj, listitems=list(obj))
#
#    def test_special_method_lookup(self):
#        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
#        class Picky:
#            def __getstate__(self):
#                return {}
#
#            def __getattr__(self, attr):
#                if attr in ("__getnewargs__", "__getnewargs_ex__"):
#                    raise AssertionError(attr)
#                return None
#        for protocol in protocols:
#            state = {} if protocol >= 2 else None
#            self._check_reduce(protocol, Picky(), state=state)
#
#    def _assert_is_copy(self, obj, objcopy, msg=None):
#        """Utility method to verify if two objects are copies of each others.
#        """
#        if msg is None:
#            msg = "{!r} is not a copy of {!r}".format(obj, objcopy)
#        if type(obj).__repr__ is object.__repr__:
#            # We have this limitation for now because we use the object's repr
#            # to help us verify that the two objects are copies. This allows
#            # us to delegate the non-generic verification logic to the objects
#            # themselves.
#            raise ValueError("object passed to _assert_is_copy must " +
#                             "override the __repr__ method.")
#        self.assertIsNot(obj, objcopy, msg=msg)
#        self.assertIs(type(obj), type(objcopy), msg=msg)
#        if hasattr(obj, '__dict__'):
#            self.assertDictEqual(obj.__dict__, objcopy.__dict__, msg=msg)
#            self.assertIsNot(obj.__dict__, objcopy.__dict__, msg=msg)
#        if hasattr(obj, '__slots__'):
#            self.assertListEqual(obj.__slots__, objcopy.__slots__, msg=msg)
#            for slot in obj.__slots__:
#                self.assertEqual(
#                    hasattr(obj, slot), hasattr(objcopy, slot), msg=msg)
#                self.assertEqual(getattr(obj, slot, None),
#                                 getattr(objcopy, slot, None), msg=msg)
#        self.assertEqual(repr(obj), repr(objcopy), msg=msg)
#
#    @staticmethod
#    def _generate_pickle_copiers():
#        """Utility method to generate the many possible pickle configurations.
#        """
#        class PickleCopier:
#            "This class copies object using pickle."
#            def __init__(self, proto, dumps, loads):
#                self.proto = proto
#                self.dumps = dumps
#                self.loads = loads
#            def copy(self, obj):
#                return self.loads(self.dumps(obj, self.proto))
#            def __repr__(self):
#                # We try to be as descriptive as possible here since this is
#                # the string which we will allow us to tell the pickle
#                # configuration we are using during debugging.
#                return ("PickleCopier(proto={}, dumps={}.{}, loads={}.{})"
#                        .format(self.proto,
#                                self.dumps.__module__, self.dumps.__qualname__,
#                                self.loads.__module__, self.loads.__qualname__))
#        return (PickleCopier(*args) for args in
#                   itertools.product(range(pickle.HIGHEST_PROTOCOL + 1),
#                                     {pickle.dumps, pickle._dumps},
#                                     {pickle.loads, pickle._loads}))
#
#    def test_pickle_slots(self):
#        # Tests pickling of classes with __slots__.
#
#        # Pickling of classes with __slots__ but without __getstate__ should
#        # fail (if using protocol 0 or 1)
#        global C
#        class C:
#            __slots__ = ['a']
#        with self.assertRaises(TypeError):
#            pickle.dumps(C(), 0)
#
#        global D
#        class D(C):
#            pass
#        with self.assertRaises(TypeError):
#            pickle.dumps(D(), 0)
#
#        class C:
#            "A class with __getstate__ and __setstate__ implemented."
#            __slots__ = ['a']
#            def __getstate__(self):
#                state = getattr(self, '__dict__', {}).copy()
#                for cls in type(self).__mro__:
#                    for slot in cls.__dict__.get('__slots__', ()):
#                        try:
#                            state[slot] = getattr(self, slot)
#                        except AttributeError:
#                            pass
#                return state
#            def __setstate__(self, state):
#                for k, v in state.items():
#                    setattr(self, k, v)
#            def __repr__(self):
#                return "%s()<%r>" % (type(self).__name__, self.__getstate__())
#
#        class D(C):
#            "A subclass of a class with slots."
#            pass
#
#        global E
#        class E(C):
#            "A subclass with an extra slot."
#            __slots__ = ['b']
#
#        # Now it should work
#        for pickle_copier in self._generate_pickle_copiers():
#            with self.subTest(pickle_copier=pickle_copier):
#                x = C()
#                y = pickle_copier.copy(x)
#                self._assert_is_copy(x, y)
#
#                x.a = 42
#                y = pickle_copier.copy(x)
#                self._assert_is_copy(x, y)
#
#                x = D()
#                x.a = 42
#                x.b = 100
#                y = pickle_copier.copy(x)
#                self._assert_is_copy(x, y)
#
#                x = E()
#                x.a = 42
#                x.b = "foo"
#                y = pickle_copier.copy(x)
#                self._assert_is_copy(x, y)
#
#    def test_reduce_copying(self):
#        # Tests pickling and copying new-style classes and objects.
#        global C1
#        class C1:
#            "The state of this class is copyable via its instance dict."
#            ARGS = (1, 2)
#            NEED_DICT_COPYING = True
#            def __init__(self, a, b):
#                super().__init__()
#                self.a = a
#                self.b = b
#            def __repr__(self):
#                return "C1(%r, %r)" % (self.a, self.b)
#
#        global C2
#        class C2(list):
#            "A list subclass copyable via __getnewargs__."
#            ARGS = (1, 2)
#            NEED_DICT_COPYING = False
#            def __new__(cls, a, b):
#                self = super().__new__(cls)
#                self.a = a
#                self.b = b
#                return self
#            def __init__(self, *args):
#                super().__init__()
#                # This helps testing that __init__ is not called during the
#                # unpickling process, which would cause extra appends.
#                self.append("cheese")
#            @classmethod
#            def __getnewargs__(cls):
#                return cls.ARGS
#            def __repr__(self):
#                return "C2(%r, %r)<%r>" % (self.a, self.b, list(self))
#
#        global C3
#        class C3(list):
#            "A list subclass copyable via __getstate__."
#            ARGS = (1, 2)
#            NEED_DICT_COPYING = False
#            def __init__(self, a, b):
#                self.a = a
#                self.b = b
#                # This helps testing that __init__ is not called during the
#                # unpickling process, which would cause extra appends.
#                self.append("cheese")
#            @classmethod
#            def __getstate__(cls):
#                return cls.ARGS
#            def __setstate__(self, state):
#                a, b = state
#                self.a = a
#                self.b = b
#            def __repr__(self):
#                return "C3(%r, %r)<%r>" % (self.a, self.b, list(self))
#
#        global C4
#        class C4(int):
#            "An int subclass copyable via __getnewargs__."
#            ARGS = ("hello", "world", 1)
#            NEED_DICT_COPYING = False
#            def __new__(cls, a, b, value):
#                self = super().__new__(cls, value)
#                self.a = a
#                self.b = b
#                return self
#            @classmethod
#            def __getnewargs__(cls):
#                return cls.ARGS
#            def __repr__(self):
#                return "C4(%r, %r)<%r>" % (self.a, self.b, int(self))
#
#        global C5
#        class C5(int):
#            "An int subclass copyable via __getnewargs_ex__."
#            ARGS = (1, 2)
#            KWARGS = {'value': 3}
#            NEED_DICT_COPYING = False
#            def __new__(cls, a, b, *, value=0):
#                self = super().__new__(cls, value)
#                self.a = a
#                self.b = b
#                return self
#            @classmethod
#            def __getnewargs_ex__(cls):
#                return (cls.ARGS, cls.KWARGS)
#            def __repr__(self):
#                return "C5(%r, %r)<%r>" % (self.a, self.b, int(self))
#
#        test_classes = (C1, C2, C3, C4, C5)
#        # Testing copying through pickle
#        pickle_copiers = self._generate_pickle_copiers()
#        for cls, pickle_copier in itertools.product(test_classes, pickle_copiers):
#            with self.subTest(cls=cls, pickle_copier=pickle_copier):
#                kwargs = getattr(cls, 'KWARGS', {})
#                obj = cls(*cls.ARGS, **kwargs)
#                proto = pickle_copier.proto
#                if 2 <= proto < 4 and hasattr(cls, '__getnewargs_ex__'):
#                    with self.assertRaises(ValueError):
#                        pickle_copier.dumps(obj, proto)
#                    continue
#                objcopy = pickle_copier.copy(obj)
#                self._assert_is_copy(obj, objcopy)
#                # For test classes that supports this, make sure we didn't go
#                # around the reduce protocol by simply copying the attribute
#                # dictionary. We clear attributes using the previous copy to
#                # not mutate the original argument.
#                if proto >= 2 and not cls.NEED_DICT_COPYING:
#                    objcopy.__dict__.clear()
#                    objcopy2 = pickle_copier.copy(objcopy)
#                    self._assert_is_copy(obj, objcopy2)
#
#        # Testing copying through copy.deepcopy()
#        for cls in test_classes:
#            with self.subTest(cls=cls):
#                kwargs = getattr(cls, 'KWARGS', {})
#                obj = cls(*cls.ARGS, **kwargs)
#                # XXX: We need to modify the copy module to support PEP 3154's
#                # reduce protocol 4.
#                if hasattr(cls, '__getnewargs_ex__'):
#                    continue
#                objcopy = deepcopy(obj)
#                self._assert_is_copy(obj, objcopy)
#                # For test classes that supports this, make sure we didn't go
#                # around the reduce protocol by simply copying the attribute
#                # dictionary. We clear attributes using the previous copy to
#                # not mutate the original argument.
#                if not cls.NEED_DICT_COPYING:
#                    objcopy.__dict__.clear()
#                    objcopy2 = deepcopy(objcopy)
#                    self._assert_is_copy(obj, objcopy2)
#
#    def test_issue24097(self):
#        # Slot name is freed inside __getattr__ and is later used.
#        class S(str):  # Not interned
#            pass
#        class A:
#            __slotnames__ = [S('spam')]
#            def __getattr__(self, attr):
#                if attr == 'spam':
#                    A.__slotnames__[:] = [S('spam')]
#                    return 42
#                else:
#                    raise AttributeError
#
#        import copyreg
#        expected = (copyreg.__newobj__, (A,), (None, {'spam': 42}), None, None)
#        self.assertEqual(A().__reduce__(2), expected)  # Shouldn't crash
#
#
#class SharedKeyTests(unittest.TestCase):
#
#    @support.cpython_only
#    def test_subclasses(self):
#        # Verify that subclasses can share keys (per PEP 412)
#        class A:
#            pass
#        class B(A):
#            pass
#
#        a, b = A(), B()
#        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
#        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({}))
#        a.x, a.y, a.z, a.w = range(4)
#        self.assertNotEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
#        a2 = A()
#        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(a2)))
#        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({}))
#        b.u, b.v, b.w, b.t = range(4)
#        self.assertLess(sys.getsizeof(vars(b)), sys.getsizeof({}))
#
#
#class DebugHelperMeta(type):
#    """
#    Sets default __doc__ and simplifies repr() output.
#    """
#    def __new__(mcls, name, bases, attrs):
#        if attrs.get('__doc__') is None:
#            attrs['__doc__'] = name  # helps when debugging with gdb
#        return type.__new__(mcls, name, bases, attrs)
#    def __repr__(cls):
#        return repr(cls.__name__)
#
#
#class MroTest(unittest.TestCase):
#    """
#    Regressions for some bugs revealed through
#    mcsl.mro() customization (typeobject.c: mro_internal()) and
#    cls.__bases__ assignment (typeobject.c: type_set_bases()).
#    """
#
#    def setUp(self):
#        self.step = 0
#        self.ready = False
#
#    def step_until(self, limit):
#        ret = (self.step < limit)
#        if ret:
#            self.step += 1
#        return ret
#
#    def test_incomplete_set_bases_on_self(self):
#        """
#        type_set_bases must be aware that type->tp_mro can be NULL.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if self.step_until(1):
#                    assert cls.__mro__ is None
#                    cls.__bases__ += ()
#
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#
#    def test_reent_set_bases_on_base(self):
#        """
#        Deep reentrancy must not over-decref old_mro.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if cls.__mro__ is not None and cls.__name__ == 'B':
#                    # 4-5 steps are usually enough to make it crash somewhere
#                    if self.step_until(10):
#                        A.__bases__ += ()
#
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#        class B(A):
#            pass
#        B.__bases__ += ()
#
#    def test_reent_set_bases_on_direct_base(self):
#        """
#        Similar to test_reent_set_bases_on_base, but may crash differently.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                base = cls.__bases__[0]
#                if base is not object:
#                    if self.step_until(5):
#                        base.__bases__ += ()
#
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#        class B(A):
#            pass
#        class C(B):
#            pass
#
#    def test_reent_set_bases_tp_base_cycle(self):
#        """
#        type_set_bases must check for an inheritance cycle not only through
#        MRO of the type, which may be not yet updated in case of reentrance,
#        but also through tp_base chain, which is assigned before diving into
#        inner calls to mro().
#
#        Otherwise, the following snippet can loop forever:
#            do {
#                // ...
#                type = type->tp_base;
#            } while (type != NULL);
#
#        Functions that rely on tp_base (like solid_base and PyType_IsSubtype)
#        would not be happy in that case, causing a stack overflow.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if self.ready:
#                    if cls.__name__ == 'B1':
#                        B2.__bases__ = (B1,)
#                    if cls.__name__ == 'B2':
#                        B1.__bases__ = (B2,)
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#        class B1(A):
#            pass
#        class B2(A):
#            pass
#
#        self.ready = True
#        with self.assertRaises(TypeError):
#            B1.__bases__ += ()
#
#    def test_tp_subclasses_cycle_in_update_slots(self):
#        """
#        type_set_bases must check for reentrancy upon finishing its job
#        by updating tp_subclasses of old/new bases of the type.
#        Otherwise, an implicit inheritance cycle through tp_subclasses
#        can break functions that recurse on elements of that field
#        (like recurse_down_subclasses and mro_hierarchy) eventually
#        leading to a stack overflow.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if self.ready and cls.__name__ == 'C':
#                    self.ready = False
#                    C.__bases__ = (B2,)
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#        class B1(A):
#            pass
#        class B2(A):
#            pass
#        class C(A):
#            pass
#
#        self.ready = True
#        C.__bases__ = (B1,)
#        B1.__bases__ = (C,)
#
#        self.assertEqual(C.__bases__, (B2,))
#        self.assertEqual(B2.__subclasses__(), [C])
#        self.assertEqual(B1.__subclasses__(), [])
#
#        self.assertEqual(B1.__bases__, (C,))
#        self.assertEqual(C.__subclasses__(), [B1])
#
#    def test_tp_subclasses_cycle_error_return_path(self):
#        """
#        The same as test_tp_subclasses_cycle_in_update_slots, but tests
#        a code path executed on error (goto bail).
#        """
#        class E(Exception):
#            pass
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if self.ready and cls.__name__ == 'C':
#                    if C.__bases__ == (B2,):
#                        self.ready = False
#                    else:
#                        C.__bases__ = (B2,)
#                        raise E
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#        class B1(A):
#            pass
#        class B2(A):
#            pass
#        class C(A):
#            pass
#
#        self.ready = True
#        with self.assertRaises(E):
#            C.__bases__ = (B1,)
#        B1.__bases__ = (C,)
#
#        self.assertEqual(C.__bases__, (B2,))
#        self.assertEqual(C.__mro__, tuple(type.mro(C)))
#
#    def test_incomplete_extend(self):
#        """
#        Extending an unitialized type with type->tp_mro == NULL must
#        throw a reasonable TypeError exception, instead of failing
#        with PyErr_BadInternalCall.
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if cls.__mro__ is None and cls.__name__ != 'X':
#                    with self.assertRaises(TypeError):
#                        class X(cls):
#                            pass
#
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#
#    def test_incomplete_super(self):
#        """
#        Attrubute lookup on a super object must be aware that
#        its target type can be uninitialized (type->tp_mro == NULL).
#        """
#        class M(DebugHelperMeta):
#            def mro(cls):
#                if cls.__mro__ is None:
#                    with self.assertRaises(AttributeError):
#                        super(cls, cls).xxx
#
#                return type.mro(cls)
#
#        class A(metaclass=M):
#            pass
#
#
#def test_main():
#    # Run all local test cases, with PTypesLongInitTest first.
#    support.run_unittest(PTypesLongInitTest, OperatorsTest,
#                         ClassPropertiesAndMethods, DictProxyTests,
#                         MiscTests, PicklingTests, SharedKeyTests,
#                         MroTest)
#
#if __name__ == "__main__":
#    test_main()
