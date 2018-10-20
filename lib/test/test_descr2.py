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

#from copy import deepcopy
#from test import support


#############################################################################   ###
class ClassPropertiesAndMethods(unittest.TestCase):

    def assertHasAttr(self, obj, name):
        self.assertTrue(hasattr(obj, name),
                        '%r has no attribute %r' % (obj, name))

    def assertNotHasAttr(self, obj, name):
        self.assertFalse(hasattr(obj, name),
                         '%r has unexpected attribute %r' % (obj, name))

#    def test_python_dicts(self):
#        # Testing Python subclass of dict...
#        self.assertTrue(issubclass(dict, dict))
#        self.assertIsInstance({}, dict)
#        d = dict()
#        self.assertEqual(d, {})
#        self.assertIs(d.__class__, dict)
#        self.assertIsInstance(d, dict)
#        class C(dict):
#            state = -1
#            def __init__(self_local, *a, **kw):
#                if a:
#                    self.assertEqual(len(a), 1)
#                    self_local.state = a[0]
#                if kw:
#                    for k, v in list(kw.items()):
#                        self_local[v] = k
#            def __getitem__(self, key):
#                return self.get(key, 0)
#            def __setitem__(self_local, key, value):
#                self.assertIsInstance(key, type(0))
#                dict.__setitem__(self_local, key, value)
#            def setstate(self, state):
#                self.state = state
#            def getstate(self):
#                return self.state
#        self.assertTrue(issubclass(C, dict))
#        a1 = C(12)
#        self.assertEqual(a1.state, 12)
#        a2 = C(foo=1, bar=2)
#        self.assertEqual(a2[1] == 'foo' and a2[2], 'bar')
#        a = C()
#        self.assertEqual(a.state, -1)
#        self.assertEqual(a.getstate(), -1)
#        a.setstate(0)
#        self.assertEqual(a.state, 0)
#        self.assertEqual(a.getstate(), 0)
#        a.setstate(10)
#        self.assertEqual(a.state, 10)
#        self.assertEqual(a.getstate(), 10)
#        self.assertEqual(a[42], 0)
#        a[42] = 24
#        self.assertEqual(a[42], 24)
#        N = 50
#        for i in range(N):
#            a[i] = C()
#            for j in range(N):
#                a[i][j] = i*j
#        for i in range(N):
#            for j in range(N):
#                self.assertEqual(a[i][j], i*j)
#
#    def test_python_lists(self):
#        # Testing Python subclass of list...
#        class C(list):
#            def __getitem__(self, i):
#                if isinstance(i, slice):
#                    return i.start, i.stop
#                return list.__getitem__(self, i) + 100
#        a = C()
#        a.extend([0,1,2])
#        self.assertEqual(a[0], 100)
#        self.assertEqual(a[1], 101)
#        self.assertEqual(a[2], 102)
#        self.assertEqual(a[100:200], (100,200))
#
#    def test_metaclass(self):
#        # Testing metaclasses...
#        class C(metaclass=type):
#            def __init__(self):
#                self.__state = 0
#            def getstate(self):
#                return self.__state
#            def setstate(self, state):
#                self.__state = state
#        a = C()
#        self.assertEqual(a.getstate(), 0)
#        a.setstate(10)
#        self.assertEqual(a.getstate(), 10)
#        class _metaclass(type):
#            def myself(cls): return cls
#        class D(metaclass=_metaclass):
#            pass
#        self.assertEqual(D.myself(), D)
#        d = D()
#        self.assertEqual(d.__class__, D)
#        class M1(type):
#            def __new__(cls, name, bases, dict):
#                dict['__spam__'] = 1
#                return type.__new__(cls, name, bases, dict)
#        class C(metaclass=M1):
#            pass
#        self.assertEqual(C.__spam__, 1)
#        c = C()
#        self.assertEqual(c.__spam__, 1)
#
#        class _instance(object):
#            pass
#        class M2(object):
#            @staticmethod
#            def __new__(cls, name, bases, dict):
#                self = object.__new__(cls)
#                self.name = name
#                self.bases = bases
#                self.dict = dict
#                return self
#            def __call__(self):
#                it = _instance()
#                # Early binding of methods
#                for key in self.dict:
#                    if key.startswith("__"):
#                        continue
#                    setattr(it, key, self.dict[key].__get__(it, self))
#                return it
#        class C(metaclass=M2):
#            def spam(self):
#                return 42
#        self.assertEqual(C.name, 'C')
#        self.assertEqual(C.bases, ())
#        self.assertIn('spam', C.dict)
#        c = C()
#        self.assertEqual(c.spam(), 42)
#
#        # More metaclass examples
#
#        class autosuper(type):
#            # Automatically add __super to the class
#            # This trick only works for dynamic classes
#            def __new__(metaclass, name, bases, dict):
#                cls = super(autosuper, metaclass).__new__(metaclass,
#                                                          name, bases, dict)
#                # Name mangling for __super removes leading underscores
#                while name[:1] == "_":
#                    name = name[1:]
#                if name:
#                    name = "_%s__super" % name
#                else:
#                    name = "__super"
#                setattr(cls, name, super(cls))
#                return cls
#        class A(metaclass=autosuper):
#            def meth(self):
#                return "A"
#        class B(A):
#            def meth(self):
#                return "B" + self.__super.meth()
#        class C(A):
#            def meth(self):
#                return "C" + self.__super.meth()
#        class D(C, B):
#            def meth(self):
#                return "D" + self.__super.meth()
#        self.assertEqual(D().meth(), "DCBA")
#        class E(B, C):
#            def meth(self):
#                return "E" + self.__super.meth()
#        self.assertEqual(E().meth(), "EBCA")
#
#        class autoproperty(type):
#            # Automatically create property attributes when methods
#            # named _get_x and/or _set_x are found
#            def __new__(metaclass, name, bases, dict):
#                hits = {}
#                for key, val in dict.items():
#                    if key.startswith("_get_"):
#                        key = key[5:]
#                        get, set = hits.get(key, (None, None))
#                        get = val
#                        hits[key] = get, set
#                    elif key.startswith("_set_"):
#                        key = key[5:]
#                        get, set = hits.get(key, (None, None))
#                        set = val
#                        hits[key] = get, set
#                for key, (get, set) in hits.items():
#                    dict[key] = property(get, set)
#                return super(autoproperty, metaclass).__new__(metaclass,
#                                                            name, bases, dict)
#        class A(metaclass=autoproperty):
#            def _get_x(self):
#                return -self.__x
#            def _set_x(self, x):
#                self.__x = -x
#        a = A()
#        self.assertNotHasAttr(a, "x")
#        a.x = 12
#        self.assertEqual(a.x, 12)
#        self.assertEqual(a._A__x, -12)
#
#        class multimetaclass(autoproperty, autosuper):
#            # Merge of multiple cooperating metaclasses
#            pass
#        class A(metaclass=multimetaclass):
#            def _get_x(self):
#                return "A"
#        class B(A):
#            def _get_x(self):
#                return "B" + self.__super._get_x()
#        class C(A):
#            def _get_x(self):
#                return "C" + self.__super._get_x()
#        class D(C, B):
#            def _get_x(self):
#                return "D" + self.__super._get_x()
#        self.assertEqual(D().x, "DCBA")
#
#        # Make sure type(x) doesn't call x.__class__.__init__
#        class T(type):
#            counter = 0
#            def __init__(self, *args):
#                T.counter += 1
#        class C(metaclass=T):
#            pass
#        self.assertEqual(T.counter, 1)
#        a = C()
#        self.assertEqual(type(a), C)
#        self.assertEqual(T.counter, 1)
#
#        class C(object): pass
#        c = C()
#        try: c()
#        except TypeError: pass
#        else: self.fail("calling object w/o call method should raise "
#                        "TypeError")
#
#        # Testing code to find most derived baseclass
#        class A(type):
#            def __new__(*args, **kwargs):
#                return type.__new__(*args, **kwargs)
#
#        class B(object):
#            pass
#
#        class C(object, metaclass=A):
#            pass
#
#        # The most derived metaclass of D is A rather than type.
#        class D(B, C):
#            pass
#        self.assertIs(A, type(D))
#
#        # issue1294232: correct metaclass calculation
#        new_calls = []  # to check the order of __new__ calls
#        class AMeta(type):
#            @staticmethod
#            def __new__(mcls, name, bases, ns):
#                new_calls.append('AMeta')
#                return super().__new__(mcls, name, bases, ns)
#            @classmethod
#            def __prepare__(mcls, name, bases):
#                return {}
#
#        class BMeta(AMeta):
#            @staticmethod
#            def __new__(mcls, name, bases, ns):
#                new_calls.append('BMeta')
#                return super().__new__(mcls, name, bases, ns)
#            @classmethod
#            def __prepare__(mcls, name, bases):
#                ns = super().__prepare__(name, bases)
#                ns['BMeta_was_here'] = True
#                return ns
#
#        class A(metaclass=AMeta):
#            pass
#        self.assertEqual(['AMeta'], new_calls)
#        new_calls.clear()
#
#        class B(metaclass=BMeta):
#            pass
#        # BMeta.__new__ calls AMeta.__new__ with super:
#        self.assertEqual(['BMeta', 'AMeta'], new_calls)
#        new_calls.clear()
#
#        class C(A, B):
#            pass
#        # The most derived metaclass is BMeta:
#        self.assertEqual(['BMeta', 'AMeta'], new_calls)
#        new_calls.clear()
#        # BMeta.__prepare__ should've been called:
#        self.assertIn('BMeta_was_here', C.__dict__)
#
#        # The order of the bases shouldn't matter:
#        class C2(B, A):
#            pass
#        self.assertEqual(['BMeta', 'AMeta'], new_calls)
#        new_calls.clear()
#        self.assertIn('BMeta_was_here', C2.__dict__)
#
#        # Check correct metaclass calculation when a metaclass is declared:
#        class D(C, metaclass=type):
#            pass
#        self.assertEqual(['BMeta', 'AMeta'], new_calls)
#        new_calls.clear()
#        self.assertIn('BMeta_was_here', D.__dict__)
#
#        class E(C, metaclass=AMeta):
#            pass
#        self.assertEqual(['BMeta', 'AMeta'], new_calls)
#        new_calls.clear()
#        self.assertIn('BMeta_was_here', E.__dict__)
#
#        # Special case: the given metaclass isn't a class,
#        # so there is no metaclass calculation.
#        marker = object()
#        def func(*args, **kwargs):
#            return marker
#        class X(metaclass=func):
#            pass
#        class Y(object, metaclass=func):
#            pass
#        class Z(D, metaclass=func):
#            pass
#        self.assertIs(marker, X)
#        self.assertIs(marker, Y)
#        self.assertIs(marker, Z)
#
#        # The given metaclass is a class,
#        # but not a descendant of type.
#        prepare_calls = []  # to track __prepare__ calls
#        class ANotMeta:
#            def __new__(mcls, *args, **kwargs):
#                new_calls.append('ANotMeta')
#                return super().__new__(mcls)
#            @classmethod
#            def __prepare__(mcls, name, bases):
#                prepare_calls.append('ANotMeta')
#                return {}
#        class BNotMeta(ANotMeta):
#            def __new__(mcls, *args, **kwargs):
#                new_calls.append('BNotMeta')
#                return super().__new__(mcls)
#            @classmethod
#            def __prepare__(mcls, name, bases):
#                prepare_calls.append('BNotMeta')
#                return super().__prepare__(name, bases)
#
#        class A(metaclass=ANotMeta):
#            pass
#        self.assertIs(ANotMeta, type(A))
#        self.assertEqual(['ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#        self.assertEqual(['ANotMeta'], new_calls)
#        new_calls.clear()
#
#        class B(metaclass=BNotMeta):
#            pass
#        self.assertIs(BNotMeta, type(B))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#
#        class C(A, B):
#            pass
#        self.assertIs(BNotMeta, type(C))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#
#        class C2(B, A):
#            pass
#        self.assertIs(BNotMeta, type(C2))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#
#        # This is a TypeError, because of a metaclass conflict:
#        # BNotMeta is neither a subclass, nor a superclass of type
#        with self.assertRaises(TypeError):
#            class D(C, metaclass=type):
#                pass
#
#        class E(C, metaclass=ANotMeta):
#            pass
#        self.assertIs(BNotMeta, type(E))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#
#        class F(object(), C):
#            pass
#        self.assertIs(BNotMeta, type(F))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#
#        class F2(C, object()):
#            pass
#        self.assertIs(BNotMeta, type(F2))
#        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
#        new_calls.clear()
#        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
#        prepare_calls.clear()
#
#        # TypeError: BNotMeta is neither a
#        # subclass, nor a superclass of int
#        with self.assertRaises(TypeError):
#            class X(C, int()):
#                pass
#        with self.assertRaises(TypeError):
#            class X(int(), C):
#                pass
#
#    def test_module_subclasses(self):
#        # Testing Python subclass of module...
#        log = []
#        MT = type(sys)
#        class MM(MT):
#            def __init__(self, name):
#                MT.__init__(self, name)
#            def __getattribute__(self, name):
#                log.append(("getattr", name))
#                return MT.__getattribute__(self, name)
#            def __setattr__(self, name, value):
#                log.append(("setattr", name, value))
#                MT.__setattr__(self, name, value)
#            def __delattr__(self, name):
#                log.append(("delattr", name))
#                MT.__delattr__(self, name)
#        a = MM("a")
#        a.foo = 12
#        x = a.foo
#        del a.foo
#        self.assertEqual(log, [("setattr", "foo", 12),
#                               ("getattr", "foo"),
#                               ("delattr", "foo")])
#
#        # http://python.org/sf/1174712
#        try:
#            class Module(types.ModuleType, str):
#                pass
#        except TypeError:
#            pass
#        else:
#            self.fail("inheriting from ModuleType and str at the same time "
#                      "should fail")
#
#    def test_multiple_inheritance(self):
#        # Testing multiple inheritance...
#        class C(object):
#            def __init__(self):
#                self.__state = 0
#            def getstate(self):
#                return self.__state
#            def setstate(self, state):
#                self.__state = state
#        a = C()
#        self.assertEqual(a.getstate(), 0)
#        a.setstate(10)
#        self.assertEqual(a.getstate(), 10)
#        class D(dict, C):
#            def __init__(self):
#                type({}).__init__(self)
#                C.__init__(self)
#        d = D()
#        self.assertEqual(list(d.keys()), [])
#        d["hello"] = "world"
#        self.assertEqual(list(d.items()), [("hello", "world")])
#        self.assertEqual(d["hello"], "world")
#        self.assertEqual(d.getstate(), 0)
#        d.setstate(10)
#        self.assertEqual(d.getstate(), 10)
#        self.assertEqual(D.__mro__, (D, dict, C, object))
#
#        # SF bug #442833
#        class Node(object):
#            def __int__(self):
#                return int(self.foo())
#            def foo(self):
#                return "23"
#        class Frag(Node, list):
#            def foo(self):
#                return "42"
#        self.assertEqual(Node().__int__(), 23)
#        self.assertEqual(int(Node()), 23)
#        self.assertEqual(Frag().__int__(), 42)
#        self.assertEqual(int(Frag()), 42)
#
    def test_diamond_inheritence(self):
        # Testing multiple inheritance special cases...
        class A(object):
            def spam(self): return "A"
        self.assertEqual(A().spam(), "A")
        class B(A):
            def boo(self): return "B"
            def spam(self): return "B"
        self.assertEqual(B().spam(), "B")
        self.assertEqual(B().boo(), "B")
        class C(A):
            def boo(self): return "C"
        self.assertEqual(C().spam(), "A")
        self.assertEqual(C().boo(), "C")
        class D(B, C): pass
        self.assertEqual(D().spam(), "B")
        self.assertEqual(D().boo(), "B")
#        self.assertEqual(D.__mro__, (D, B, C, A, object))
        class E(C, B): pass
#        self.assertEqual(E().spam(), "B")
        self.assertEqual(E().boo(), "C")
#        self.assertEqual(E.__mro__, (E, C, B, A, object))
        # MRO order disagreement
#        try:
#            class F(D, E): pass
#        except TypeError:
#            pass
#        else:
#            self.fail("expected MRO order disagreement (F)")
#        try:
#            class G(E, D): pass
#        except TypeError:
#            pass
#        else:
#            self.fail("expected MRO order disagreement (G)")

#    # see thread python-dev/2002-October/029035.html
#    def test_ex5_from_c3_switch(self):
#        # Testing ex5 from C3 switch discussion...
#        class A(object): pass
#        class B(object): pass
#        class C(object): pass
#        class X(A): pass
#        class Y(A): pass
#        class Z(X,B,Y,C): pass
#        self.assertEqual(Z.__mro__, (Z, X, B, Y, A, C, object))
#
#    # see "A Monotonic Superclass Linearization for Dylan",
#    # by Kim Barrett et al. (OOPSLA 1996)
#    def test_monotonicity(self):
#        # Testing MRO monotonicity...
#        class Boat(object): pass
#        class DayBoat(Boat): pass
#        class WheelBoat(Boat): pass
#        class EngineLess(DayBoat): pass
#        class SmallMultihull(DayBoat): pass
#        class PedalWheelBoat(EngineLess,WheelBoat): pass
#        class SmallCatamaran(SmallMultihull): pass
#        class Pedalo(PedalWheelBoat,SmallCatamaran): pass
#
#        self.assertEqual(PedalWheelBoat.__mro__,
#              (PedalWheelBoat, EngineLess, DayBoat, WheelBoat, Boat, object))
#        self.assertEqual(SmallCatamaran.__mro__,
#              (SmallCatamaran, SmallMultihull, DayBoat, Boat, object))
#        self.assertEqual(Pedalo.__mro__,
#              (Pedalo, PedalWheelBoat, EngineLess, SmallCatamaran,
#               SmallMultihull, DayBoat, WheelBoat, Boat, object))
#
#    # see "A Monotonic Superclass Linearization for Dylan",
#    # by Kim Barrett et al. (OOPSLA 1996)
#    def test_consistency_with_epg(self):
#        # Testing consistency with EPG...
#        class Pane(object): pass
#        class ScrollingMixin(object): pass
#        class EditingMixin(object): pass
#        class ScrollablePane(Pane,ScrollingMixin): pass
#        class EditablePane(Pane,EditingMixin): pass
#        class EditableScrollablePane(ScrollablePane,EditablePane): pass
#
#        self.assertEqual(EditableScrollablePane.__mro__,
#              (EditableScrollablePane, ScrollablePane, EditablePane, Pane,
#                ScrollingMixin, EditingMixin, object))
#
#    def test_mro_disagreement(self):
#        # Testing error messages for MRO disagreement...
#        mro_err_msg = """Cannot create a consistent method resolution
#order (MRO) for bases """
#
#        def raises(exc, expected, callable, *args):
#            try:
#                callable(*args)
#            except exc as msg:
#                # the exact msg is generally considered an impl detail
#                if support.check_impl_detail():
#                    if not str(msg).startswith(expected):
#                        self.fail("Message %r, expected %r" %
#                                  (str(msg), expected))
#            else:
#                self.fail("Expected %s" % exc)
#
#        class A(object): pass
#        class B(A): pass
#        class C(object): pass
#
#        # Test some very simple errors
#        raises(TypeError, "duplicate base class A",
#               type, "X", (A, A), {})
#        raises(TypeError, mro_err_msg,
#               type, "X", (A, B), {})
#        raises(TypeError, mro_err_msg,
#               type, "X", (A, C, B), {})
#        # Test a slightly more complex error
#        class GridLayout(object): pass
#        class HorizontalGrid(GridLayout): pass
#        class VerticalGrid(GridLayout): pass
#        class HVGrid(HorizontalGrid, VerticalGrid): pass
#        class VHGrid(VerticalGrid, HorizontalGrid): pass
#        raises(TypeError, mro_err_msg,
#               type, "ConfusedGrid", (HVGrid, VHGrid), {})
#
    def test_object_class(self):
        # Testing object class...
        a = object()
        self.assertEqual(a.__class__, object)
        self.assertEqual(type(a), object)
        b = object()
        self.assertNotEqual(a, b)
        self.assertNotHasAttr(a, "foo")
        try:
            a.foo = 12
        except (AttributeError, TypeError):
            pass
        else:
            self.fail("object() should not allow setting a foo attribute")
        self.assertNotHasAttr(object(), "__dict__")

        class Cdict(object):
            pass
        x = Cdict()
        self.assertEqual(x.__dict__, {})
        x.foo = 1
        self.assertEqual(x.foo, 1)
        self.assertEqual(x.__dict__, {'foo': 1})

#    def test_slots(self):
#        # Testing __slots__...
#        class C0(object):
#            __slots__ = []
#        x = C0()
#        self.assertNotHasAttr(x, "__dict__")
#        self.assertNotHasAttr(x, "foo")
#
#        class C1(object):
#            __slots__ = ['a']
#        x = C1()
#        self.assertNotHasAttr(x, "__dict__")
#        self.assertNotHasAttr(x, "a")
#        x.a = 1
#        self.assertEqual(x.a, 1)
#        x.a = None
#        self.assertEqual(x.a, None)
#        del x.a
#        self.assertNotHasAttr(x, "a")
#
#        class C3(object):
#            __slots__ = ['a', 'b', 'c']
#        x = C3()
#        self.assertNotHasAttr(x, "__dict__")
#        self.assertNotHasAttr(x, 'a')
#        self.assertNotHasAttr(x, 'b')
#        self.assertNotHasAttr(x, 'c')
#        x.a = 1
#        x.b = 2
#        x.c = 3
#        self.assertEqual(x.a, 1)
#        self.assertEqual(x.b, 2)
#        self.assertEqual(x.c, 3)
#
#        class C4(object):
#            """Validate name mangling"""
#            __slots__ = ['__a']
#            def __init__(self, value):
#                self.__a = value
#            def get(self):
#                return self.__a
#        x = C4(5)
#        self.assertNotHasAttr(x, '__dict__')
#        self.assertNotHasAttr(x, '__a')
#        self.assertEqual(x.get(), 5)
#        try:
#            x.__a = 6
#        except AttributeError:
#            pass
#        else:
#            self.fail("Double underscored names not mangled")
#
#        # Make sure slot names are proper identifiers
#        try:
#            class C(object):
#                __slots__ = [None]
#        except TypeError:
#            pass
#        else:
#            self.fail("[None] slots not caught")
#        try:
#            class C(object):
#                __slots__ = ["foo bar"]
#        except TypeError:
#            pass
#        else:
#            self.fail("['foo bar'] slots not caught")
#        try:
#            class C(object):
#                __slots__ = ["foo\0bar"]
#        except TypeError:
#            pass
#        else:
#            self.fail("['foo\\0bar'] slots not caught")
#        try:
#            class C(object):
#                __slots__ = ["1"]
#        except TypeError:
#            pass
#        else:
#            self.fail("['1'] slots not caught")
#        try:
#            class C(object):
#                __slots__ = [""]
#        except TypeError:
#            pass
#        else:
#            self.fail("[''] slots not caught")
#        class C(object):
#            __slots__ = ["a", "a_b", "_a", "A0123456789Z"]
#        # XXX(nnorwitz): was there supposed to be something tested
#        # from the class above?
#
#        # Test a single string is not expanded as a sequence.
#        class C(object):
#            __slots__ = "abc"
#        c = C()
#        c.abc = 5
#        self.assertEqual(c.abc, 5)
#
#        # Test unicode slot names
#        # Test a single unicode string is not expanded as a sequence.
#        class C(object):
#            __slots__ = "abc"
#        c = C()
#        c.abc = 5
#        self.assertEqual(c.abc, 5)
#
#        # _unicode_to_string used to modify slots in certain circumstances
#        slots = ("foo", "bar")
#        class C(object):
#            __slots__ = slots
#        x = C()
#        x.foo = 5
#        self.assertEqual(x.foo, 5)
#        self.assertIs(type(slots[0]), str)
#        # this used to leak references
#        try:
#            class C(object):
#                __slots__ = [chr(128)]
#        except (TypeError, UnicodeEncodeError):
#            pass
#        else:
#            self.fail("[chr(128)] slots not caught")
#
#        # Test leaks
#        class Counted(object):
#            counter = 0    # counts the number of instances alive
#            def __init__(self):
#                Counted.counter += 1
#            def __del__(self):
#                Counted.counter -= 1
#        class C(object):
#            __slots__ = ['a', 'b', 'c']
#        x = C()
#        x.a = Counted()
#        x.b = Counted()
#        x.c = Counted()
#        self.assertEqual(Counted.counter, 3)
#        del x
#        support.gc_collect()
#        self.assertEqual(Counted.counter, 0)
#        class D(C):
#            pass
#        x = D()
#        x.a = Counted()
#        x.z = Counted()
#        self.assertEqual(Counted.counter, 2)
#        del x
#        support.gc_collect()
#        self.assertEqual(Counted.counter, 0)
#        class E(D):
#            __slots__ = ['e']
#        x = E()
#        x.a = Counted()
#        x.z = Counted()
#        x.e = Counted()
#        self.assertEqual(Counted.counter, 3)
#        del x
#        support.gc_collect()
#        self.assertEqual(Counted.counter, 0)
#
#        # Test cyclical leaks [SF bug 519621]
#        class F(object):
#            __slots__ = ['a', 'b']
#        s = F()
#        s.a = [Counted(), s]
#        self.assertEqual(Counted.counter, 1)
#        s = None
#        support.gc_collect()
#        self.assertEqual(Counted.counter, 0)
#
#        # Test lookup leaks [SF bug 572567]
#        if hasattr(gc, 'get_objects'):
#            class G(object):
#                def __eq__(self, other):
#                    return False
#            g = G()
#            orig_objects = len(gc.get_objects())
#            for i in range(10):
#                g==g
#            new_objects = len(gc.get_objects())
#            self.assertEqual(orig_objects, new_objects)
#
#        class H(object):
#            __slots__ = ['a', 'b']
#            def __init__(self):
#                self.a = 1
#                self.b = 2
#            def __del__(self_):
#                self.assertEqual(self_.a, 1)
#                self.assertEqual(self_.b, 2)
#        with support.captured_output('stderr') as s:
#            h = H()
#            del h
#        self.assertEqual(s.getvalue(), '')
#
#        class X(object):
#            __slots__ = "a"
#        with self.assertRaises(AttributeError):
#            del X().a
#
#    def test_slots_special(self):
#        # Testing __dict__ and __weakref__ in __slots__...
#        class D(object):
#            __slots__ = ["__dict__"]
#        a = D()
#        self.assertHasAttr(a, "__dict__")
#        self.assertNotHasAttr(a, "__weakref__")
#        a.foo = 42
#        self.assertEqual(a.__dict__, {"foo": 42})
#
#        class W(object):
#            __slots__ = ["__weakref__"]
#        a = W()
#        self.assertHasAttr(a, "__weakref__")
#        self.assertNotHasAttr(a, "__dict__")
#        try:
#            a.foo = 42
#        except AttributeError:
#            pass
#        else:
#            self.fail("shouldn't be allowed to set a.foo")
#
#        class C1(W, D):
#            __slots__ = []
#        a = C1()
#        self.assertHasAttr(a, "__dict__")
#        self.assertHasAttr(a, "__weakref__")
#        a.foo = 42
#        self.assertEqual(a.__dict__, {"foo": 42})
#
#        class C2(D, W):
#            __slots__ = []
#        a = C2()
#        self.assertHasAttr(a, "__dict__")
#        self.assertHasAttr(a, "__weakref__")
#        a.foo = 42
#        self.assertEqual(a.__dict__, {"foo": 42})
#
#    def test_slots_descriptor(self):
#        # Issue2115: slot descriptors did not correctly check
#        # the type of the given object
#        import abc
#        class MyABC(metaclass=abc.ABCMeta):
#            __slots__ = "a"
#
#        class Unrelated(object):
#            pass
#        MyABC.register(Unrelated)
#
#        u = Unrelated()
#        self.assertIsInstance(u, MyABC)
#
#        # This used to crash
#        self.assertRaises(TypeError, MyABC.a.__set__, u, 3)
#
    def test_dynamics(self):
        # Testing class attribute propagation...
        class D(object):
            pass
        class E(D):
            pass
        class F(D):
            pass
        D.foo = 1
        self.assertEqual(D.foo, 1)
        # Test that dynamic attributes are inherited
        self.assertEqual(E.foo, 1)
        self.assertEqual(F.foo, 1)
        # Test dynamic instances
        class C(object):
            pass
        a = C()
        self.assertNotHasAttr(a, "foobar")
        C.foobar = 2
        self.assertEqual(a.foobar, 2)
        C.method = lambda self: 42
        self.assertEqual(a.method(), 42)
        C.__repr__ = lambda self: "C()"
        self.assertEqual(repr(a), "C()")
#        C.__int__ = lambda self: 100
#        self.assertEqual(int(a), 100)
        self.assertEqual(a.foobar, 2)
        self.assertNotHasAttr(a, "spam")
        def mygetattr(self, name):
            if name == "spam":
                return "spam"
            raise AttributeError
        C.__getattr__ = mygetattr
        self.assertEqual(a.spam, "spam")
        a.new = 12
        self.assertEqual(a.new, 12)
#        def mysetattr(self, name, value):
#            if name == "spam":
#                raise AttributeError
#            return object.__setattr__(self, name, value)
#        C.__setattr__ = mysetattr
#        try:
#            a.spam = "not spam"
#        except AttributeError:
#            pass
#        else:
#            self.fail("expected AttributeError")
        self.assertEqual(a.spam, "spam")
        class D(C):
            pass
        d = D()
        d.foo = 1
        self.assertEqual(d.foo, 1)

        # Test handling of int*seq and seq*int
        class I(int):
            pass
#        self.assertEqual("a"*I(2), "aa")
        self.assertEqual(I(2)*"a", "aa")
#        self.assertEqual(2*I(3), 6)
        self.assertEqual(I(3)*2, 6)
#        self.assertEqual(I(3)*I(2), 6)
#
#        # Test comparison of classes with dynamic metaclasses
#        class dynamicmetaclass(type):
#            pass
#        class someclass(metaclass=dynamicmetaclass):
#            pass
#        self.assertNotEqual(someclass, object)

    def test_errors(self):
        # Testing errors...
        try:
            class C(list, dict):
                pass
        except TypeError:
            pass
        else:
            self.fail("inheritance from both list and dict should be illegal")

        try:
            class C(object, None):
                pass
        except TypeError:
            pass
        else:
            self.fail("inheritance from non-type should be illegal")
        class Classic:
            pass

        try:
            class C(type(len)):
                pass
        except TypeError:
            pass
        else:
            self.fail("inheritance from CFunction should be illegal")

#        try:
#            class C(object):
#                __slots__ = 1
#        except TypeError:
#            pass
#        else:
#            self.fail("__slots__ = 1 should be illegal")
#
#        try:
#            class C(object):
#                __slots__ = [1]
#        except TypeError:
#            pass
#        else:
#            self.fail("__slots__ = [1] should be illegal")
#
#        class M1(type):
#            pass
#        class M2(type):
#            pass
#        class A1(object, metaclass=M1):
#            pass
#        class A2(object, metaclass=M2):
#            pass
#        try:
#            class B(A1, A2):
#                pass
#        except TypeError:
#            pass
#        else:
#            self.fail("finding the most derived metaclass should have failed")

    def test_classmethods(self):
        # Testing class methods...
        class C(object):
            def foo(*a): return a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        class D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
#        # Test for a specific crash (SF bug 528132)
        def f(cls, arg): return (cls, arg)
#        ff = classmethod(f)
#        self.assertEqual(ff.__get__(0, int)(42), (int, 42))
#        self.assertEqual(ff.__get__(0)(42), (int, 42))

        # Test super() with classmethods (SF bug 535444)
#        self.assertEqual(C.goo.__self__, C)
#        self.assertEqual(D.goo.__self__, D)
#        self.assertEqual(super(D,D).goo.__self__, D)
#        self.assertEqual(super(D,d).goo.__self__, D)
#        self.assertEqual(super(D,D).goo(), (D,))
        self.assertEqual(super(D,d).goo(), (D,))

#        # Verify that a non-callable will raise
#        meth = classmethod(1).__get__(1)
#        self.assertRaises(TypeError, meth)
#
        # Verify that classmethod() doesn't allow keyword args
        try:
            classmethod(f, kw=1)
        except TypeError:
            pass
        else:
            self.fail("classmethod shouldn't accept keyword args")
#
#        cm = classmethod(f)
#        self.assertEqual(cm.__dict__, {})
#        cm.x = 42
#        self.assertEqual(cm.x, 42)
#        self.assertEqual(cm.__dict__, {"x" : 42})
#        del cm.x
#        self.assertNotHasAttr(cm, "x")

#    @support.impl_detail("the module 'xxsubtype' is internal")
#    def test_classmethods_in_c(self):
#        # Testing C-based class methods...
#        import xxsubtype as spam
#        a = (1, 2, 3)
#        d = {'abc': 123}
#        x, a1, d1 = spam.spamlist.classmeth(*a, **d)
#        self.assertEqual(x, spam.spamlist)
#        self.assertEqual(a, a1)
#        self.assertEqual(d, d1)
#        x, a1, d1 = spam.spamlist().classmeth(*a, **d)
#        self.assertEqual(x, spam.spamlist)
#        self.assertEqual(a, a1)
#        self.assertEqual(d, d1)
#        spam_cm = spam.spamlist.__dict__['classmeth']
#        x2, a2, d2 = spam_cm(spam.spamlist, *a, **d)
#        self.assertEqual(x2, spam.spamlist)
#        self.assertEqual(a2, a1)
#        self.assertEqual(d2, d1)
#        class SubSpam(spam.spamlist): pass
#        x2, a2, d2 = spam_cm(SubSpam, *a, **d)
#        self.assertEqual(x2, SubSpam)
#        self.assertEqual(a2, a1)
#        self.assertEqual(d2, d1)
#        with self.assertRaises(TypeError):
#            spam_cm()
#        with self.assertRaises(TypeError):
#            spam_cm(spam.spamlist())
#        with self.assertRaises(TypeError):
#            spam_cm(list)
#
    def test_staticmethods(self):
        # Testing static methods...
        class C(object):
            def foo(*a): return a
            goo = staticmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (1,))
        self.assertEqual(c.goo(1), (1,))
        self.assertEqual(c.foo(1), (c, 1,))
        class D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (1,))
        self.assertEqual(d.goo(1), (1,))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
#        sm = staticmethod(None)
#        self.assertEqual(sm.__dict__, {})
#        sm.x = 42
#        self.assertEqual(sm.x, 42)
#        self.assertEqual(sm.__dict__, {"x" : 42})
#        del sm.x
#        self.assertNotHasAttr(sm, "x")

#    @support.impl_detail("the module 'xxsubtype' is internal")
#    def test_staticmethods_in_c(self):
#        # Testing C-based static methods...
#        import xxsubtype as spam
#        a = (1, 2, 3)
#        d = {"abc": 123}
#        x, a1, d1 = spam.spamlist.staticmeth(*a, **d)
#        self.assertEqual(x, None)
#        self.assertEqual(a, a1)
#        self.assertEqual(d, d1)
#        x, a1, d2 = spam.spamlist().staticmeth(*a, **d)
#        self.assertEqual(x, None)
#        self.assertEqual(a, a1)
#        self.assertEqual(d, d1)
#
    def test_classic(self):
        # Testing classic classes...
        class C:
            def foo(*a): return a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        class D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        class E: # *not* subclassing from C
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
#        self.assertTrue(repr(C.foo.__get__(C())).startswith("<bound method "))

    def test_compattr(self):
        # Testing computed attributes...
        class C(object):
            class computed_attribute(object):
                def __init__(self, get, set=None, delete=None):
                    self.__get = get
                    self.__set = set
                    self.__delete = delete
                def __get__(self, obj, type=None):
                    return self.__get(obj)
                def __set__(self, obj, value):
                    return self.__set(obj, value)
                def __delete__(self, obj):
                    return self.__delete(obj)
            def __init__(self):
                self.__x = 0
            def __get_x(self):
                x = self.__x
                self.__x = x+1
                return x
            def __set_x(self, x):
                self.__x = x
            def __delete_x(self):
                del self.__x
            x = computed_attribute(__get_x, __set_x, __delete_x)
        a = C()
        self.assertEqual(a.x, 0)
        self.assertEqual(a.x, 1)
        a.x = 10
        self.assertEqual(a.x, 10)
        self.assertEqual(a.x, 11)
        del a.x
#        self.assertNotHasAttr(a, 'x')

#    def test_newslots(self):
#        # Testing __new__ slot override...
#        class C(list):
#            def __new__(cls):
#                self = list.__new__(cls)
#                self.foo = 1
#                return self
#            def __init__(self):
#                self.foo = self.foo + 2
#        a = C()
#        self.assertEqual(a.foo, 3)
#        self.assertEqual(a.__class__, C)
#        class D(C):
#            pass
#        b = D()
#        self.assertEqual(b.foo, 3)
#        self.assertEqual(b.__class__, D)
#
#    def test_altmro(self):
#        # Testing mro() and overriding it...
#        class A(object):
#            def f(self): return "A"
#        class B(A):
#            pass
#        class C(A):
#            def f(self): return "C"
#        class D(B, C):
#            pass
#        self.assertEqual(D.mro(), [D, B, C, A, object])
#        self.assertEqual(D.__mro__, (D, B, C, A, object))
#        self.assertEqual(D().f(), "C")
#
#        class PerverseMetaType(type):
#            def mro(cls):
#                L = type.mro(cls)
#                L.reverse()
#                return L
#        class X(D,B,C,A, metaclass=PerverseMetaType):
#            pass
#        self.assertEqual(X.__mro__, (object, A, C, B, D, X))
#        self.assertEqual(X().f(), "A")
#
#        try:
#            class _metaclass(type):
#                def mro(self):
#                    return [self, dict, object]
#            class X(object, metaclass=_metaclass):
#                pass
#            # In CPython, the class creation above already raises
#            # TypeError, as a protection against the fact that
#            # instances of X would segfault it.  In other Python
#            # implementations it would be ok to let the class X
#            # be created, but instead get a clean TypeError on the
#            # __setitem__ below.
#            x = object.__new__(X)
#            x[5] = 6
#        except TypeError:
#            pass
#        else:
#            self.fail("devious mro() return not caught")
#
#        try:
#            class _metaclass(type):
#                def mro(self):
#                    return [1]
#            class X(object, metaclass=_metaclass):
#                pass
#        except TypeError:
#            pass
#        else:
#            self.fail("non-class mro() return not caught")
#
#        try:
#            class _metaclass(type):
#                def mro(self):
#                    return 1
#            class X(object, metaclass=_metaclass):
#                pass
#        except TypeError:
#            pass
#        else:
#            self.fail("non-sequence mro() return not caught")
#
#    def test_overloading(self):
#        # Testing operator overloading...
#
#        class B(object):
#            "Intermediate class because object doesn't have a __setattr__"
#
#        class C(B):
#            def __getattr__(self, name):
#                if name == "foo":
#                    return ("getattr", name)
#                else:
#                    raise AttributeError
#            def __setattr__(self, name, value):
#                if name == "foo":
#                    self.setattr = (name, value)
#                else:
#                    return B.__setattr__(self, name, value)
#            def __delattr__(self, name):
#                if name == "foo":
#                    self.delattr = name
#                else:
#                    return B.__delattr__(self, name)
#
#            def __getitem__(self, key):
#                return ("getitem", key)
#            def __setitem__(self, key, value):
#                self.setitem = (key, value)
#            def __delitem__(self, key):
#                self.delitem = key
#
#        a = C()
#        self.assertEqual(a.foo, ("getattr", "foo"))
#        a.foo = 12
#        self.assertEqual(a.setattr, ("foo", 12))
#        del a.foo
#        self.assertEqual(a.delattr, "foo")
#
#        self.assertEqual(a[12], ("getitem", 12))
#        a[12] = 21
#        self.assertEqual(a.setitem, (12, 21))
#        del a[12]
#        self.assertEqual(a.delitem, 12)
#
#        self.assertEqual(a[0:10], ("getitem", slice(0, 10)))
#        a[0:10] = "foo"
#        self.assertEqual(a.setitem, (slice(0, 10), "foo"))
#        del a[0:10]
#        self.assertEqual(a.delitem, (slice(0, 10)))
#
    def test_methods(self):
        # Testing methods...
        class C(object):
            def __init__(self, x):
                self.x = x
            def foo(self):
                return self.x
        c1 = C(1)
        self.assertEqual(c1.foo(), 1)
        class D(C):
            boo = C.foo
            goo = c1.foo
        d2 = D(2)
        self.assertEqual(d2.foo(), 2)
        self.assertEqual(d2.boo(), 2)
        self.assertEqual(d2.goo(), 1)
        class E(object):
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
#        self.assertTrue(repr(C.foo.__get__(C(1))).startswith("<bound method "))

#    def test_special_method_lookup(self):
#        # The lookup of special methods bypasses __getattr__ and
#        # __getattribute__, but they still can be descriptors.
#
#        def run_context(manager):
#            with manager:
#                pass
#        def iden(self):
#            return self
#        def hello(self):
#            return b"hello"
#        def empty_seq(self):
#            return []
#        def zero(self):
#            return 0
#        def complex_num(self):
#            return 1j
#        def stop(self):
#            raise StopIteration
#        def return_true(self, thing=None):
#            return True
#        def do_isinstance(obj):
#            return isinstance(int, obj)
#        def do_issubclass(obj):
#            return issubclass(int, obj)
#        def do_dict_missing(checker):
#            class DictSub(checker.__class__, dict):
#                pass
#            self.assertEqual(DictSub()["hi"], 4)
#        def some_number(self_, key):
#            self.assertEqual(key, "hi")
#            return 4
#        def swallow(*args): pass
#        def format_impl(self, spec):
#            return "hello"
#
#        # It would be nice to have every special method tested here, but I'm
#        # only listing the ones I can remember outside of typeobject.c, since it
#        # does it right.
#        specials = [
#            ("__bytes__", bytes, hello, set(), {}),
#            ("__reversed__", reversed, empty_seq, set(), {}),
#            ("__length_hint__", list, zero, set(),
#             {"__iter__" : iden, "__next__" : stop}),
#            ("__sizeof__", sys.getsizeof, zero, set(), {}),
#            ("__instancecheck__", do_isinstance, return_true, set(), {}),
#            ("__missing__", do_dict_missing, some_number,
#             set(("__class__",)), {}),
#            ("__subclasscheck__", do_issubclass, return_true,
#             set(("__bases__",)), {}),
#            ("__enter__", run_context, iden, set(), {"__exit__" : swallow}),
#            ("__exit__", run_context, swallow, set(), {"__enter__" : iden}),
#            ("__complex__", complex, complex_num, set(), {}),
#            ("__format__", format, format_impl, set(), {}),
#            ("__floor__", math.floor, zero, set(), {}),
#            ("__trunc__", math.trunc, zero, set(), {}),
#            ("__trunc__", int, zero, set(), {}),
#            ("__ceil__", math.ceil, zero, set(), {}),
#            ("__dir__", dir, empty_seq, set(), {}),
#            ("__round__", round, zero, set(), {}),
#            ]
#
#        class Checker(object):
#            def __getattr__(self, attr, test=self):
#                test.fail("__getattr__ called with {0}".format(attr))
#            def __getattribute__(self, attr, test=self):
#                if attr not in ok:
#                    test.fail("__getattribute__ called with {0}".format(attr))
#                return object.__getattribute__(self, attr)
#        class SpecialDescr(object):
#            def __init__(self, impl):
#                self.impl = impl
#            def __get__(self, obj, owner):
#                record.append(1)
#                return self.impl.__get__(obj, owner)
#        class MyException(Exception):
#            pass
#        class ErrDescr(object):
#            def __get__(self, obj, owner):
#                raise MyException
#
#        for name, runner, meth_impl, ok, env in specials:
#            class X(Checker):
#                pass
#            for attr, obj in env.items():
#                setattr(X, attr, obj)
#            setattr(X, name, meth_impl)
#            runner(X())
#
#            record = []
#            class X(Checker):
#                pass
#            for attr, obj in env.items():
#                setattr(X, attr, obj)
#            setattr(X, name, SpecialDescr(meth_impl))
#            runner(X())
#            self.assertEqual(record, [1], name)
#
#            class X(Checker):
#                pass
#            for attr, obj in env.items():
#                setattr(X, attr, obj)
#            setattr(X, name, ErrDescr())
#            self.assertRaises(MyException, runner, X())
#
    def test_specials(self):
        # Testing special operators...
        # Test operators like __hash__ for which a built-in default exists

        # Test the default behavior for static classes
        class C(object):
            def __getitem__(self, i):
                if 0 <= i < 10: return i
                raise IndexError
        c1 = C()
        c2 = C()
        self.assertFalse(not c1)
        self.assertNotEqual(id(c1), id(c2))
        hash(c1)
        hash(c2)
        self.assertEqual(c1, c1)
        self.assertTrue(c1 != c2)
        self.assertFalse(c1 != c1)
        self.assertFalse(c1 == c2)
        # Note that the module name appears in str/repr, and that varies
        # depending on whether this test is run standalone or from a framework.
        self.assertGreaterEqual(str(c1).find('C object at '), 0)
        self.assertEqual(str(c1), repr(c1))
        self.assertNotIn(-1, c1)
        for i in range(10):
            self.assertIn(i, c1)
        self.assertNotIn(10, c1)
        # Test the default behavior for dynamic classes
        class D(object):
            def __getitem__(self, i):
                if 0 <= i < 10: return i
                raise IndexError
        d1 = D()
        d2 = D()
        self.assertFalse(not d1)
        self.assertNotEqual(id(d1), id(d2))
        hash(d1)
        hash(d2)
        self.assertEqual(d1, d1)
        self.assertNotEqual(d1, d2)
        self.assertFalse(d1 != d1)
        self.assertFalse(d1 == d2)
        # Note that the module name appears in str/repr, and that varies
        # depending on whether this test is run standalone or from a framework.
        self.assertGreaterEqual(str(d1).find('D object at '), 0)
        self.assertEqual(str(d1), repr(d1))
        self.assertNotIn(-1, d1)
        for i in range(10):
            self.assertIn(i, d1)
        self.assertNotIn(10, d1)
        # Test overridden behavior
        class Proxy(object):
            def __init__(self, x):
                self.x = x
            def __bool__(self):
                return not not self.x
            def __hash__(self):
                return hash(self.x)
            def __eq__(self, other):
                return self.x == other
            def __ne__(self, other):
                return self.x != other
            def __ge__(self, other):
                return self.x >= other
            def __gt__(self, other):
                return self.x > other
            def __le__(self, other):
                return self.x <= other
            def __lt__(self, other):
                return self.x < other
            def __str__(self):
                return "Proxy:%s" % self.x
            def __repr__(self):
                return "Proxy(%r)" % self.x
            def __contains__(self, value):
                return value in self.x
        p0 = Proxy(0)
        p1 = Proxy(1)
        p_1 = Proxy(-1)
        self.assertFalse(p0)
        self.assertFalse(not p1)
        self.assertEqual(hash(p0), hash(0))
        self.assertEqual(p0, p0)
        self.assertNotEqual(p0, p1)
        self.assertFalse(p0 != p0)
        self.assertEqual(not p0, p1)
#        self.assertTrue(p0 < p1)
#        self.assertTrue(p0 <= p1)
#        self.assertTrue(p1 > p0)
#        self.assertTrue(p1 >= p0)
        self.assertEqual(str(p0), "Proxy:0")
        self.assertEqual(repr(p0), "Proxy(0)")
        p10 = Proxy(range(10))
        self.assertNotIn(-1, p10)
        for i in range(10):
            self.assertIn(i, p10)
        self.assertNotIn(10, p10)

#    def test_weakrefs(self):
#        # Testing weak references...
#        import weakref
#        class C(object):
#            pass
#        c = C()
#        r = weakref.ref(c)
#        self.assertEqual(r(), c)
#        del c
#        support.gc_collect()
#        self.assertEqual(r(), None)
#        del r
#        class NoWeak(object):
#            __slots__ = ['foo']
#        no = NoWeak()
#        try:
#            weakref.ref(no)
#        except TypeError as msg:
#            self.assertIn("weak reference", str(msg))
#        else:
#            self.fail("weakref.ref(no) should be illegal")
#        class Weak(object):
#            __slots__ = ['foo', '__weakref__']
#        yes = Weak()
#        r = weakref.ref(yes)
#        self.assertEqual(r(), yes)
#        del yes
#        support.gc_collect()
#        self.assertEqual(r(), None)
#        del r
#
    def test_properties(self):
        # Testing property...
        class C(object):
            def getx(self):
                return self.__x
            def setx(self, value):
                self.__x = value
            def delx(self):
                del self.__x
            x = property(getx, setx, delx, doc="I'm the x property.")
        a = C()
#        self.assertNotHasAttr(a, "x")
        a.x = 42
#        self.assertEqual(a._C__x, 42)
        self.assertEqual(a.x, 42)
        del a.x
#        self.assertNotHasAttr(a, "x")
        self.assertNotHasAttr(a, "_C__x")
#        C.x.__set__(a, 100)
#        self.assertEqual(C.x.__get__(a), 100)
#        C.x.__delete__(a)
#        self.assertNotHasAttr(a, "x")
#
#        raw = C.__dict__['x']
#        self.assertIsInstance(raw, property)
#
#        attrs = dir(raw)
#        self.assertIn("__doc__", attrs)
#        self.assertIn("fget", attrs)
#        self.assertIn("fset", attrs)
#        self.assertIn("fdel", attrs)
#
#        self.assertEqual(raw.__doc__, "I'm the x property.")
#        self.assertIs(raw.fget, C.__dict__['getx'])
#        self.assertIs(raw.fset, C.__dict__['setx'])
#        self.assertIs(raw.fdel, C.__dict__['delx'])
#
#        for attr in "__doc__", "fget", "fset", "fdel":
#            try:
#                setattr(raw, attr, 42)
#            except AttributeError as msg:
#                if str(msg).find('readonly') < 0:
#                    self.fail("when setting readonly attr %r on a property, "
#                              "got unexpected AttributeError msg %r" % (attr, str(msg)))
#            else:
#                self.fail("expected AttributeError from trying to set readonly %r "
#                          "attr on a property" % attr)
#
        class D(object):
            __getitem__ = property(lambda s: 1/0)

        d = D()
        try:
            for i in d:
                str(i)
        except ZeroDivisionError:
            pass
        else:
            self.fail("expected ZeroDivisionError from bad property")

#    @unittest.skipIf(sys.flags.optimize >= 2,
#                     "Docstrings are omitted with -O2 and above")
#    def test_properties_doc_attrib(self):
#        class E(object):
#            def getter(self):
#                "getter method"
#                return 0
#            def setter(self_, value):
#                "setter method"
#                pass
#            prop = property(getter)
#            self.assertEqual(prop.__doc__, "getter method")
#            prop2 = property(fset=setter)
#            self.assertEqual(prop2.__doc__, None)
#
#    @support.cpython_only
#    def test_testcapi_no_segfault(self):
#        # this segfaulted in 2.5b2
#        try:
#            import _testcapi
#        except ImportError:
#            pass
#        else:
#            class X(object):
#                p = property(_testcapi.test_with_docstring)
#
    def test_properties_plus(self):
        class C(object):
            foo = property(doc="hello")
            @foo.getter
            def foo(self):
                return self._foo
            @foo.setter
            def foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            def foo(self):
                del self._foo
        c = C()
#        self.assertEqual(C.foo.__doc__, "hello")
#        self.assertNotHasAttr(c, "foo")
        c.foo = -42
        self.assertHasAttr(c, '_foo')
        self.assertEqual(c._foo, 42)
        self.assertEqual(c.foo, 42)
        del c.foo
        self.assertNotHasAttr(c, '_foo')
#        self.assertNotHasAttr(c, "foo")

        class D(C):
            @C.foo.deleter
            def foo(self):
                try:
                    del self._foo
                except AttributeError:
                    pass
        d = D()
        d.foo = 24
        self.assertEqual(d.foo, 24)
        del d.foo
        del d.foo

        class E(object):
            @property
            def foo(self):
                return self._foo
            @foo.setter
            def foo(self, value):
                raise RuntimeError
            @foo.setter
            def foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            def foo(self, value=None):
                del self._foo

        e = E()
        e.foo = -42
        self.assertEqual(e.foo, 42)
        del e.foo

        class F(E):
            @E.foo.deleter
            def foo(self):
                del self._foo
            @foo.setter
            def foo(self, value):
                self._foo = max(0, value)
        f = F()
        f.foo = -10
        self.assertEqual(f.foo, 0)
        del f.foo

    def test_dict_constructors(self):
        # Testing dict constructor ...
        d = dict()
        self.assertEqual(d, {})
        d = dict({})
        self.assertEqual(d, {})
        d = dict({1: 2, 'a': 'b'})
        self.assertEqual(d, {1: 2, 'a': 'b'})
        self.assertEqual(d, dict(list(d.items())))
        self.assertEqual(d, dict(iter(d.items())))
        d = dict({'one':1, 'two':2})
        self.assertEqual(d, dict(one=1, two=2))
        self.assertEqual(d, dict(**d))
        self.assertEqual(d, dict({"one": 1}, two=2))
        self.assertEqual(d, dict([("two", 2)], one=1))
        self.assertEqual(d, dict([("one", 100), ("two", 200)], **d))
        self.assertEqual(d, dict(**d))

        for badarg in 0, 0, 0j, "0", [0], (0,):
            try:
                dict(badarg)
            except TypeError:
                pass
            except ValueError:
                if badarg == "0":
                    # It's a sequence, and its elements are also sequences (gotta
                    # love strings <wink>), but they aren't of length 2, so this
                    # one seemed better as a ValueError than a TypeError.
                    pass
                else:
                    self.fail("no TypeError from dict(%r)" % badarg)
            else:
                self.fail("no TypeError from dict(%r)" % badarg)

        try:
            dict({}, {})
        except TypeError:
            pass
        else:
            self.fail("no TypeError from dict({}, {})")

        class Mapping:
            # Lacks a .keys() method; will be added later.
            dict = {1:2, 3:4, 'a':1j}

        try:
            dict(Mapping())
        except TypeError:
            pass
        else:
            self.fail("no TypeError from dict(incomplete mapping)")

#        Mapping.keys = lambda self: list(self.dict.keys())
#        Mapping.__getitem__ = lambda self, i: self.dict[i]
#        d = dict(Mapping())
#        self.assertEqual(d, Mapping.dict)

        # Init from sequence of iterable objects, each producing a 2-sequence.
        class AddressBookEntry:
            def __init__(self, first, last):
                self.first = first
                self.last = last
            def __iter__(self):
                return iter([self.first, self.last])

        d = dict([AddressBookEntry('Tim', 'Warsaw'),
                  AddressBookEntry('Barry', 'Peters'),
                  AddressBookEntry('Tim', 'Peters'),
                  AddressBookEntry('Barry', 'Warsaw')])
        self.assertEqual(d, {'Barry': 'Warsaw', 'Tim': 'Peters'})

        d = dict(zip(range(4), range(1, 5)))
        self.assertEqual(d, dict([(i, i+1) for i in range(4)]))

        # Bad sequence lengths.
        for bad in [('tooshort',)], [('too', 'long', 'by 1')]:
            try:
                dict(bad)
            except ValueError:
                pass
            else:
                self.fail("no ValueError from dict(%r)" % bad)

    def test_dir(self):
        # Testing dir() ...
#        junk = 12
#        self.assertEqual(dir(), ['junk', 'self'])
#        del junk

        # Just make sure these don't blow up!
        for arg in 2, 2, 2j, 2e0, [2], "2", b"2", (2,), {2:2}, type, self.test_dir:
            dir(arg)

        # Test dir on new-style classes.  Since these have object as a
        # base class, a lot more gets sucked in.
        def interesting(strings):
            return [s for s in strings if not s.startswith('_')]

        class C(object):
            Cdata = 1
            def Cmethod(self): pass

        cstuff = ['Cdata', 'Cmethod']
        self.assertEqual(interesting(dir(C)), cstuff)

        c = C()
        self.assertEqual(interesting(dir(c)), cstuff)
        ## self.assertIn('__self__', dir(C.Cmethod))

        c.cdata = 2
        c.cmethod = lambda self: 0
        self.assertEqual(interesting(dir(c)), cstuff + ['cdata', 'cmethod'])
        ## self.assertIn('__self__', dir(c.Cmethod))

        class A(C):
            Adata = 1
            def Amethod(self): pass

#        astuff = ['Adata', 'Amethod'] + cstuff
        astuff = cstuff + ['Adata', 'Amethod']                                  ###
        self.assertEqual(interesting(dir(A)), astuff)
        ## self.assertIn('__self__', dir(A.Amethod))
        a = A()
        self.assertEqual(interesting(dir(a)), astuff)
        a.adata = 42
        a.amethod = lambda self: 3
        self.assertEqual(interesting(dir(a)), astuff + ['adata', 'amethod'])
        ## self.assertIn('__self__', dir(a.Amethod))

#        # Try a module subclass.
#        class M(type(sys)):
#            pass
#        minstance = M("m")
#        minstance.b = 2
#        minstance.a = 1
#        default_attributes = ['__name__', '__doc__', '__package__',
#                              '__loader__', '__spec__']
#        names = [x for x in dir(minstance) if x not in default_attributes]
#        self.assertEqual(names, ['a', 'b'])
#
#        class M2(M):
#            def getdict(self):
#                return "Not a dict!"
#            __dict__ = property(getdict)
#
#        m2instance = M2("m2")
#        m2instance.b = 2
#        m2instance.a = 1
#        self.assertEqual(m2instance.__dict__, "Not a dict!")
#        try:
#            dir(m2instance)
#        except TypeError:
#            pass
#
        # Two essentially featureless objects, just inheriting stuff from
        # object.
        self.assertEqual(dir(NotImplemented), dir(Ellipsis))

        # Nasty test case for proxied objects
        class Wrapper(object):
            def __init__(self, obj):
                self.__obj = obj
            def __repr__(self):
                return "Wrapper(%s)" % repr(self.__obj)
            def __getitem__(self, key):
                return Wrapper(self.__obj[key])
            def __len__(self):
                return len(self.__obj)
            def __getattr__(self, name):
                return Wrapper(getattr(self.__obj, name))

        class C(object):
            def __getclass(self):
                return Wrapper(type(self))
            __class__ = property(__getclass)

        dir(C()) # This used to segfault
