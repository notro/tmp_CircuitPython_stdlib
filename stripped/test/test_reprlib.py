"""
  Test cases for the repr module
  Nick Mathewson
"""

import unittest

from reprlib import repr as r # Don't shadow builtin repr
from reprlib import Repr
from reprlib import recursive_repr


def nestedTuple(nesting):
    t = ()
    for i in range(nesting):
        t = (t,)
    return t

class ReprTests(unittest.TestCase):

    def test_string(self):
        eq = self.assertEqual
        eq(r("abc"), "'abc'")
        eq(r("abcdefghijklmnop"),"'abcdefghijklmnop'")

        s = "a"*30+"b"*30
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

        eq(r("\"'"), repr("\"'"))
        s = "\""*30+"'"*100
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

    def test_tuple(self):
        eq = self.assertEqual
        eq(r((1,)), "(1,)")

        t3 = (1, 2, 3)
        eq(r(t3), "(1, 2, 3)")

        r2 = Repr()
        r2.maxtuple = 2
        expected = repr(t3)[:-2] + "...)"
        eq(r2.repr(t3), expected)

    def test_container(self):
        from array import array

        eq = self.assertEqual
        # Tuples give up after 6 elements
        eq(r(()), "()")
        eq(r((1,)), "(1,)")
        eq(r((1, 2, 3)), "(1, 2, 3)")
        eq(r((1, 2, 3, 4, 5, 6)), "(1, 2, 3, 4, 5, 6)")
        eq(r((1, 2, 3, 4, 5, 6, 7)), "(1, 2, 3, 4, 5, 6, ...)")

        # Lists give up after 6 as well
        eq(r([]), "[]")
        eq(r([1]), "[1]")
        eq(r([1, 2, 3]), "[1, 2, 3]")
        eq(r([1, 2, 3, 4, 5, 6]), "[1, 2, 3, 4, 5, 6]")
        eq(r([1, 2, 3, 4, 5, 6, 7]), "[1, 2, 3, 4, 5, 6, ...]")

        # Sets give up after 6 as well
        eq(r(set([])), "set([])")
        eq(r(set([1])), "set([1])")
        eq(r(set([1, 2, 3])), "set([1, 2, 3])")
        eq(r(set([1, 2, 3, 4, 5, 6])), "set([1, 2, 3, 4, 5, 6])")
        eq(r(set([1, 2, 3, 4, 5, 6, 7])), "set([1, 2, 3, 4, 5, 6, ...])")

        # Frozensets give up after 6 as well
        eq(r(frozenset([])), "frozenset([])")
        eq(r(frozenset([1])), "frozenset([1])")
        eq(r(frozenset([1, 2, 3])), "frozenset([1, 2, 3])")
        eq(r(frozenset([1, 2, 3, 4, 5, 6])), "frozenset([1, 2, 3, 4, 5, 6])")
        eq(r(frozenset([1, 2, 3, 4, 5, 6, 7])), "frozenset([1, 2, 3, 4, 5, 6, ...])")

        # Dictionaries give up after 4.
        eq(r({}), "{}")
        d = {'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}
        eq(r(d), "{'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}")
        d['arthur'] = 1
        eq(r(d), "{'alice': 1, 'arthur': 1, 'bob': 2, 'charles': 3, ...}")

    def test_numbers(self):
        eq = self.assertEqual
        eq(r(123), repr(123))
        eq(r(123), repr(123))
        eq(r(1.0/3), repr(1.0/3))

        n = 10**100
        expected = repr(n)[:18] + "..." + repr(n)[-19:]
        eq(r(n), expected)

    def test_instance(self):
        eq = self.assertEqual
        i1 = ClassWithRepr("a")
        eq(r(i1), repr(i1))

        i2 = ClassWithRepr("x"*1000)
        expected = repr(i2)[:13] + "..." + repr(i2)[-14:]
        eq(r(i2), expected)

        i3 = ClassWithFailingRepr()
        eq(r(i3), ("<ClassWithFailingRepr instance at %x>"%id(i3)))

        s = r(ClassWithFailingRepr)
        self.assertTrue(s.startswith("<class "))
        self.assertTrue(s.endswith(">"))

    def test_range(self):
        eq = self.assertEqual
        eq(repr(range(1)), 'range(0, 1)')
        eq(repr(range(1, 2)), 'range(1, 2)')
        eq(repr(range(1, 4, 3)), 'range(1, 4, 3)')

    def test_unsortable(self):
        # Repr.repr() used to call sorted() on sets, frozensets and dicts
        # without taking into account that not all objects are comparable
        x = set([1j, 2j, 3j])
        y = frozenset(x)
        z = {1j: 1, 2j: 2}
        r(x)
        r(y)
        r(z)

class ClassWithRepr:
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "ClassWithRepr(%r)" % self.s


class ClassWithFailingRepr:
    def __repr__(self):
        raise Exception("This should be caught by Repr.repr_instance")

class MyContainer:
    'Helper class for TestRecursiveRepr'
    def __init__(self, values):
        self.values = list(values)
    def append(self, value):
        self.values.append(value)
    @recursive_repr()
    def __repr__(self):
        return '<' + ', '.join(map(str, self.values)) + '>'

class MyContainer2(MyContainer):
    @recursive_repr('+++')
    def __repr__(self):
        return '<' + ', '.join(map(str, self.values)) + '>'

class TestRecursiveRepr(unittest.TestCase):
    def test_recursive_repr(self):
        m = MyContainer(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, ..., x, ...>')
        m = MyContainer2(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, +++, x, +++>')

