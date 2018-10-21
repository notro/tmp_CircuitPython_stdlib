"""Unit tests for the copy module."""

import copy

import unittest
from test import support


class TestCopy(unittest.TestCase):

    # Attempt full line coverage of copy.py from top to bottom

    def test_exceptions(self):
        self.assertIs(copy.Error, copy.error)
        self.assertTrue(issubclass(copy.Error, Exception))

    # The copy() method

    def test_copy_basic(self):
        x = 42
        y = copy.copy(x)
        self.assertEqual(x, y)

    def test_copy_copy(self):
        class C(object):
            def __init__(self, foo):
                self.foo = foo
            def __copy__(self):
                return C(self.foo)
        x = C(42)
        y = copy.copy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    def test_copy_reduce_ex(self):
        class C(object):
            def __reduce_ex__(self, proto):
                c.append(1)
                return ""
            def __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_copy_reduce(self):
        class C(object):
            def __reduce__(self):
                c.append(1)
                return ""
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    # Type-specific _copy_xxx() methods

    def test_copy_atomic(self):
        class Classic:
            pass
        class NewStyle(object):
            pass
        def f():
            pass
        tests = [None, 42, 2**100, 3.14, True, False, 1j,
                 "hello", "hello\u1234",                                        ###
                 b"world", bytes(range(256)),
                 NewStyle, range(10), Classic]                                  ###
        for x in tests:
            self.assertIs(copy.copy(x), x)

    def test_copy_list(self):
        x = [1, 2, 3]
        self.assertEqual(copy.copy(x), x)

    def test_copy_tuple(self):
        x = (1, 2, 3)
        self.assertEqual(copy.copy(x), x)

    def test_copy_dict(self):
        x = {"foo": 1, "bar": 2}
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_vanilla(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __eq__(self, other):
                return self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_copy(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __copy__(self):
                return C(self.foo)
            def __eq__(self, other):
                return self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_getstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                return {"foo": self.foo}
            def __eq__(self, other):
                return self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_setstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __setstate__(self, state):
                self.foo = state["foo"]
            def __eq__(self, other):
                return self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    def test_copy_inst_getstate_setstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                return self.foo
            def __setstate__(self, state):
                self.foo = state
            def __eq__(self, other):
                return self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    # The deepcopy() method

    def test_deepcopy_basic(self):
        x = 42
        y = copy.deepcopy(x)
        self.assertEqual(y, x)

    def test_deepcopy_memo(self):
        # Tests of reflexive objects are under type-specific sections below.
        # This tests only repetitions of objects.
        x = []
        x = [x, x]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0], y[1])

    def test_deepcopy_deepcopy(self):
        class C(object):
            def __init__(self, foo):
                self.foo = foo
            def __deepcopy__(self, memo=None):
                return C(self.foo)
        x = C(42)
        y = copy.deepcopy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    def test_deepcopy_reduce_ex(self):
        class C(object):
            def __reduce_ex__(self, proto):
                c.append(1)
                return ""
            def __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    def test_deepcopy_reduce(self):
        class C(object):
            def __reduce__(self):
                c.append(1)
                return ""
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    # Type-specific _deepcopy_xxx() methods

    def test_deepcopy_atomic(self):
        class Classic:
            pass
        class NewStyle(object):
            pass
        def f():
            pass
        tests = [None, 42, 2**100, 3.14, True, False, 1j,
                 "hello", "hello\u1234",                                        ###
                 NewStyle, range(10), Classic]                                  ###
        for x in tests:
            self.assertIs(copy.deepcopy(x), x)

    def test_deepcopy_list(self):
        x = [[1, 2], 3]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_deepcopy_reflexive_list(self):
        x = []
        x.append(x)
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y[0], y)
        self.assertEqual(len(y), 1)

    def test_deepcopy_empty_tuple(self):
        x = ()
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    def test_deepcopy_tuple(self):
        x = ([1, 2], 3)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_deepcopy_tuple_of_immutables(self):
        x = ((1, 2), 3)
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    def test_deepcopy_reflexive_tuple(self):
        x = ([],)
        x[0].append(x)
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0][0], y)

    def test_deepcopy_dict(self):
        x = {"foo": [1, 2], "bar": 3}
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x["foo"], y["foo"])

    def test_deepcopy_reflexive_dict(self):
        x = {}
        x['foo'] = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y['foo'], y)
        self.assertEqual(len(y), 1)

    def test_deepcopy_keepalive(self):
        memo = {}
        x = []
        y = copy.deepcopy(x, memo)
        self.assertIs(memo[id(memo)][0], x)

    def test_deepcopy_dont_memo_immutable(self):
        memo = {}
        x = [1, 2, 3, 4]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # There's the entry for the new list, and the keep alive.
        self.assertEqual(len(memo), 2)

        memo = {}
        x = [(1, 2)]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # Tuples with immutable contents are immutable for deepcopy.
        self.assertEqual(len(memo), 2)

    def test_deepcopy_inst_vanilla(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __eq__(self, other):
                return self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_deepcopy(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __deepcopy__(self, memo):
                return C(copy.deepcopy(self.foo, memo))
            def __eq__(self, other):
                return self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                return {"foo": self.foo}
            def __eq__(self, other):
                return self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_setstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __setstate__(self, state):
                self.foo = state["foo"]
            def __eq__(self, other):
                return self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_inst_getstate_setstate(self):
        class C:
            def __init__(self, foo):
                self.foo = foo
            def __getstate__(self):
                return self.foo
            def __setstate__(self, state):
                self.foo = state
            def __eq__(self, other):
                return self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_deepcopy_reflexive_inst(self):
        class C:
            pass
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    # _reconstruct()

    def test_reconstruct_string(self):
        class C(object):
            def __reduce__(self):
                return ""
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        y = copy.deepcopy(x)
        self.assertIs(y, x)

    def test_reconstruct_nostate(self):
        class C(object):
            def __reduce__(self):
                return (C, ())
        x = C()
        x.foo = 42
        y = copy.copy(x)
        self.assertIs(y.__class__, x.__class__)
        y = copy.deepcopy(x)
        self.assertIs(y.__class__, x.__class__)

    def test_reconstruct_state(self):
        class C(object):
            def __reduce__(self):
                return (C, (), self.__dict__)
            def __eq__(self, other):
                return self.__dict__ == other.__dict__
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertEqual(y, x)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    def test_reconstruct_reflexive(self):
        class C(object):
            pass
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    # Additions for Python 2.3 and pickle protocol 2

    def test_reduce_4tuple(self):
        class C(list):
            def __reduce__(self):
                return (C, (), self.__dict__, iter(self))
            def __eq__(self, other):
                return (list(self) == list(other) and
                        self.__dict__ == other.__dict__)
        x = C([[1, 2], 3])
        y = copy.copy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIs(x[0], y[0])
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    def test_getstate_exc(self):
        class EvilState(object):
            def __getstate__(self):
                raise ValueError("ain't got no stickin' state")
        self.assertRaises(ValueError, copy.copy, EvilState())

    def test_copy_function(self):
        self.assertEqual(copy.copy(global_foo), global_foo)
        def foo(x, y): return x+y
        self.assertEqual(copy.copy(foo), foo)
        bar = lambda: None
        self.assertEqual(copy.copy(bar), bar)

    def test_deepcopy_function(self):
        self.assertEqual(copy.deepcopy(global_foo), global_foo)
        def foo(x, y): return x+y
        self.assertEqual(copy.deepcopy(foo), foo)
        bar = lambda: None
        self.assertEqual(copy.deepcopy(bar), bar)


def global_foo(x, y): return x+y

