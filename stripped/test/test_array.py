"""Test the arraymodule.
   Roger E. Masse
"""

import unittest
from test import support
import io
import struct
import sys

import array

try:
    # Try to determine availability of long long independently
    # of the array module under test
    struct.calcsize('@q')
    have_long_long = True
except struct.error:
    have_long_long = False



class ArraySubclass(array.array):
    pass

class ArraySubclassWithKwargs(array.array):
    def __init__(self, typecode, newarg=None):
        super().__init__(typecode)                                              ###

typecodes = "bBhHiIlLfd"                                                        ###
if have_long_long:
    typecodes += 'qQ'

class BadConstructorTest(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(TypeError, array.array)
        self.assertRaises(TypeError, array.array, spam=42)
        self.assertRaises(ValueError, array.array, 'x')


class BaseTest:
    # Required class attributes (provided by subclasses
    # typecode: the typecode to test
    # example: an initializer usable in the constructor for this type
    # smallerexample: the same length as example, but smaller
    # biggerexample: the same length as example, but bigger
    # outside: An entry that is not in example
    # minitemsize: the minimum guaranteed itemsize

    def assertEntryEqual(self, entry1, entry2):
        self.assertEqual(entry1, entry2)

    def badtypecode(self):
        # Return a typecode that is different from our own
        return typecodes[(typecodes.index(self.typecode)+1) % len(typecodes)]

    def test_constructor(self):
        a = array.array(self.typecode)
        self.assertRaises(TypeError, array.array, self.typecode, None)

    def test_len(self):
        a = array.array(self.typecode)
        a.append(self.example[0])
        self.assertEqual(len(a), 1)

        a = array.array(self.typecode, self.example)
        self.assertEqual(len(a), len(self.example))

    def test_fromarray(self):
        a = array.array(self.typecode, self.example)
        b = array.array(self.typecode, a)
        self.assertEqual(a, b)

    def test_repr(self):
        a = array.array(self.typecode, 2*self.example)
        self.assertEqual(a, eval(repr(a), {"array": array.array}))

        a = array.array(self.typecode)
        self.assertEqual(repr(a), "array('%s')" % self.typecode)

    def test_str(self):
        a = array.array(self.typecode, 2*self.example)
        str(a)

    def test_cmp(self):
        a = array.array(self.typecode, self.example)
        self.assertIs(a == 42, False)
        self.assertIs(a != 42, True)

        self.assertIs(a == a, True)
        self.assertIs(a != a, False)

        al = array.array(self.typecode, self.smallerexample)
        ab = array.array(self.typecode, self.biggerexample)

        self.assertIs(a == a*2, False)                                          ###
        self.assertIs(a != a*2, True)                                           ###

        self.assertIs(a == al, False)
        self.assertIs(a != al, True)

        self.assertIs(a == ab, False)
        self.assertIs(a != ab, True)

    def test_add(self):
        a = array.array(self.typecode, self.example) \
            + array.array(self.typecode, self.example[::-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[::-1])
        )

    def test_iadd(self):
        a = array.array(self.typecode, self.example[::-1])
        b = a
        a += array.array(self.typecode, 2*self.example)
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[::-1]+2*self.example)
        )
        a = array.array(self.typecode, self.example)
        a += a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example)
        )

    def test_mul(self):
        a = array.array(self.typecode, self.example)*5
        self.assertEqual(
            a,
            array.array(self.typecode, self.example*5)
        )

        a = array.array(self.typecode, self.example) * 0                        ###
        self.assertEqual(
            a,
            array.array(self.typecode)
        )

        a = array.array(self.typecode, self.example[:1]) * 5                    ###
        self.assertEqual(
            a,
            array.array(self.typecode, [a[0]] * 5)
        )

    def test_imul(self):
        a = array.array(self.typecode, self.example)
        b = a

        a *= 5
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, 5*self.example)
        )

        a *= 0
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a *= 10                                                                 ###
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

    def test_getitem(self):
        a = array.array(self.typecode, self.example)
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[len(self.example)-1], self.example[-1])
        self.assertEntryEqual(a[-len(self.example)], self.example[0])

    def test_setitem(self):
        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[len(self.example)-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-len(self.example)] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

    def test_getslice(self):
        a = array.array(self.typecode, self.example)
        self.assertEqual(a[:], a)

        self.assertEqual(
            a[1:],
            array.array(self.typecode, self.example[1:])
        )

        self.assertEqual(
            a[:1],
            array.array(self.typecode, self.example[:1])
        )

        self.assertEqual(
            a[:-1],
            array.array(self.typecode, self.example[:-1])
        )

        self.assertEqual(
            a[-1:],
            array.array(self.typecode, self.example[-1:])
        )

        self.assertEqual(
            a[-1:-1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[2:1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[1000:],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:], a)
        self.assertEqual(a[:1000], a)
        self.assertEqual(
            a[:-1000],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:1000], a)
        self.assertEqual(
            a[2000:1000],
            array.array(self.typecode)
        )

    def test_extended_getslice(self):
        # Test extended slicing by comparing with list slicing
        # (Assumes list conversion works correctly, too)
        a = array.array(self.typecode, self.example)
        indices = (0, None, 1, 3, 19, 100, -1, -2, -31, -100)
        for start in indices:
            for stop in indices:
                # Everything except the initial 0 (invalid step)
                for step in [1]:                                                ###
                    self.assertEqual(list(a[start:stop:step]),
                                     list(a)[start:stop:step])

    def test_setslice(self):
        a = array.array(self.typecode, self.example)
        a[:1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[:-1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[-1:])
        )

        a = array.array(self.typecode, self.example)
        a[-1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:-1] = a
        self.assertEqual(
            a,
            array.array(
                self.typecode,
                self.example[:1] + self.example + self.example[-1:]
            )
        )

        a = array.array(self.typecode, self.example)
        a[1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[-1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:-1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:0] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[2000:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

    def test_extend(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.extend)

        a = array.array(self.typecode, self.example)
        a.extend(a)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example)
        )

    def test_constructor_with_iterable_argument(self):
        a = array.array(self.typecode, iter(self.example))
        b = array.array(self.typecode, self.example)
        self.assertEqual(a, b)

        # non-iterable argument
        self.assertRaises(TypeError, array.array, self.typecode, 10)

        # pass through errors raised in __iter__
        class A:
            def __iter__(self):
                raise UnicodeError
        self.assertRaises(UnicodeError, array.array, self.typecode, A())

        # pass through errors raised in next()
        def B():
            raise UnicodeError
            yield None
        self.assertRaises(UnicodeError, array.array, self.typecode, B())

    def test_coveritertraverse(self):
        try:
            import gc
        except ImportError:
            self.skipTest('gc module not available')
        a = array.array(self.typecode)
        l = [iter(a)]
        l.append(l)
        gc.collect()

    def test_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously raise a TypeError
        ArraySubclassWithKwargs('b', newarg=1)



class StringTest(BaseTest):

    def test_setitem(self):
        super().test_setitem()
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.__setitem__, 0, self.example[:2])

class NumberTest(BaseTest):

    def test_assignment(self):
        a = array.array(self.typecode, range(10))
        b = a[:]
        c = a[:]
        ins = array.array(self.typecode, range(2))
        a[2:3] = ins
        b[slice(2,3)] = ins
        c[2:3:] = ins

    def test_iterationcontains(self):
        a = array.array(self.typecode, range(10))
        self.assertEqual(list(a), list(range(10)))

    def check_overflow(self, lower, upper):
        # method to be used by subclasses

        # should not overflow assigning lower limit
        a = array.array(self.typecode, [lower])
        a[0] = lower
        # should overflow assigning less than lower limit
        self.assertRaises(OverflowError, array.array, self.typecode, [lower-1])
        self.assertRaises(OverflowError, a.__setitem__, 0, lower-1)
        # should not overflow assigning upper limit
        a = array.array(self.typecode, [upper])
        a[0] = upper
        # should overflow assigning more than upper limit
        self.assertRaises(OverflowError, array.array, self.typecode, [upper+1])
        self.assertRaises(OverflowError, a.__setitem__, 0, upper+1)

class SignedNumberTest(NumberTest):
    example = [-1, 0, 1, 42, 0x7f]
    smallerexample = [-1, 0, 1, 42, 0x7e]
    biggerexample = [-1, 0, 1, 43, 0x7f]
    outside = 23

class UnsignedNumberTest(NumberTest):
    example = [0, 1, 17, 23, 42, 0xff]
    smallerexample = [0, 1, 17, 23, 42, 0xfe]
    biggerexample = [0, 1, 17, 23, 43, 0xff]
    outside = 0xaa


class ByteTest(SignedNumberTest, unittest.TestCase):
    typecode = 'b'
    minitemsize = 1

class UnsignedByteTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'B'
    minitemsize = 1

class ShortTest(SignedNumberTest, unittest.TestCase):
    typecode = 'h'
    minitemsize = 2

class UnsignedShortTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'H'
    minitemsize = 2

class IntTest(SignedNumberTest, unittest.TestCase):
    typecode = 'i'
    minitemsize = 2

class UnsignedIntTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'I'
    minitemsize = 2

class LongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'l'
    minitemsize = 4

class UnsignedLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'L'
    minitemsize = 4

@unittest.skipIf(not have_long_long, 'need long long support')
class LongLongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'q'
    minitemsize = 8
                                                                                ###
    # -1 ends up as 65535 in these tests                                        ###
    # We can't mark using expectedFailure since function name is used as key    ###
    # and all functions with that name would be marked (no function properties) ###
    def test_fromarray(self):                                                   ###
        raise unittest.SkipTest('FAILS on -1')                                  ###
                                                                                ###
    def test_mul(self):                                                         ###
        raise unittest.SkipTest('FAILS on -1')                                  ###
                                                                                ###
    def test_setitem(self):                                                     ###
        raise unittest.SkipTest('FAILS on -1')                                  ###

@unittest.skipIf(not have_long_long, 'need long long support')
class UnsignedLongLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'Q'
    minitemsize = 8

class FPTest(NumberTest):
    example = [-42.0, 0, 42, 1e5, -1e10]
    smallerexample = [-42.0, 0, 42, 1e5, -2e10]
    biggerexample = [-42.0, 0, 42, 1e5, 1e10]
    outside = 23

    def assertEntryEqual(self, entry1, entry2):
        self.assertAlmostEqual(entry1, entry2)

class FloatTest(FPTest, unittest.TestCase):
    typecode = 'f'
    minitemsize = 4

class DoubleTest(FPTest, unittest.TestCase):
    typecode = 'd'
    minitemsize = 8

