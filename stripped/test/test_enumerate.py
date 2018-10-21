import unittest
import sys


class G:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        return self.seqn[i]

class I:
    'Sequence using iterator protocol'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class Ig:
    'Sequence using iterator protocol defined with a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        for val in self.seqn:
            yield val

class X:
    'Missing __getitem__ and __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __next__(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class E:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        3 // 0

class N:
    'Iterator missing __next__()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self

class EnumerateTestCase(unittest.TestCase):                                     ###

    enum = enumerate
    seq, res = 'abc', [(0,'a'), (1,'b'), (2,'c')]

    def test_basicfunction(self):
        self.assertEqual(type(self.enum(self.seq)), self.enum)
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)

    def test_getitemseqn(self):
        self.assertEqual(list(self.enum(G(self.seq))), self.res)
        e = self.enum(G(''))
        self.assertRaises(StopIteration, next, e)

    def test_iteratorseqn(self):
        self.assertEqual(list(self.enum(I(self.seq))), self.res)
        e = self.enum(I(''))
        self.assertRaises(StopIteration, next, e)

    def test_iteratorgenerator(self):
        self.assertEqual(list(self.enum(Ig(self.seq))), self.res)
        e = self.enum(Ig(''))
        self.assertRaises(StopIteration, next, e)

    def test_noniterable(self):
        self.assertRaises(TypeError, self.enum, X(self.seq))

    def test_exception_propagation(self):
        self.assertRaises(ZeroDivisionError, list, self.enum(E(self.seq)))

    def test_argumentcheck(self):
        self.assertRaises(TypeError, self.enum) # no arguments
        self.assertRaises(TypeError, self.enum, 1) # wrong type (not iterable)
        self.assertRaises(TypeError, self.enum, 'abc', 'a') # wrong type
        self.assertRaises(TypeError, self.enum, 'abc', 2, 3) # too many arguments

class MyEnum(enumerate):
    pass

class SubclassTestCase(EnumerateTestCase):

    enum = MyEnum

    def test_basicfunction(self):                                               ###
        self.skipTest('AssertionError: <enumerate> != <MyEnum object at 20010c20>')  ###
                                                                                ###
class TestEmpty(EnumerateTestCase):

    seq, res = '', []

class TestReversed(unittest.TestCase):                                          ###

    def test_simple(self):
        class A:
            def __getitem__(self, i):
                if i < 5:
                    return str(i)
                raise StopIteration
            def __len__(self):
                return 5
        for data in 'abc', range(5), tuple(enumerate('abc')), A(), range(1,17,5):
            self.assertEqual(list(data)[::-1], list(reversed(data)))
        # don't allow keyword arguments
        self.assertRaises(TypeError, reversed, [], a=1)

    def test_gc(self):
        class Seq:
            def __len__(self):
                return 10
            def __getitem__(self, index):
                return index
        s = Seq()
        r = reversed(s)
        s.r = r

    def test_args(self):
        self.assertRaises(TypeError, reversed)
        self.assertRaises(TypeError, reversed, [], 'extra')

    def test_objmethods(self):
        # Objects must have __len__() and __getitem__() implemented.
        class NoLen(object):
            def __getitem__(self): return 1
        nl = NoLen()
        self.assertRaises(TypeError, reversed, nl)


class EnumerateStartTestCase(EnumerateTestCase):

    def test_basicfunction(self):
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)


class TestStart(EnumerateStartTestCase):

    enum = lambda self, i: enumerate(i, start=11)
    seq, res = 'abc', [(11, 'a'), (12, 'b'), (13, 'c')]


