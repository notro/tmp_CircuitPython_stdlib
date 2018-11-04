# tests for slice objects; in particular the indices method.

import unittest
from test import support

import sys



# Class providing an __index__ method.  Used for testing slice.indices.

class MyIndexable(object):
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


class SliceTest(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(TypeError, slice)
        self.assertRaises(TypeError, slice, 1, 2, 3, 4)

    def test_repr(self):
        self.assertEqual(repr(slice(1, 2, 3)), "slice(1, 2, 3)")

    def test_members(self):
        s = slice(1)
        self.assertEqual(s.start, None)
        self.assertEqual(s.stop, 1)
        self.assertEqual(s.step, None)

        s = slice(1, 2)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, None)

        s = slice(1, 2, 3)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, 3)

        class AnyClass:
            pass

        obj = AnyClass()
        s = slice(obj)
        self.assertTrue(s.stop is obj)

    def test_indices(self):
        self.assertEqual(slice(None           ).indices(10), (0, 10,  1))
        self.assertEqual(slice(None,  None,  2).indices(10), (0, 10,  2))
        self.assertEqual(slice(1,     None,  2).indices(10), (1, 10,  2))
        self.assertEqual(slice(None,  None, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None,  None, -2).indices(10), (9, -1, -2))
        self.assertEqual(slice(3,     None, -2).indices(10), (3, -1, -2))
        # issue 3004 tests
        self.assertEqual(slice(None, -9).indices(10), (0, 1, 1))
        self.assertEqual(slice(None, -10).indices(10), (0, 0, 1))
        self.assertEqual(slice(None, -11).indices(10), (0, 0, 1))
        self.assertEqual(slice(None, -10, -1).indices(10), (9, 0, -1))
        self.assertEqual(slice(None, -11, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None, -12, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None, 9).indices(10), (0, 9, 1))
        self.assertEqual(slice(None, 10).indices(10), (0, 10, 1))
        self.assertEqual(slice(None, 11).indices(10), (0, 10, 1))
        self.assertEqual(slice(None, 8, -1).indices(10), (9, 8, -1))
        self.assertEqual(slice(None, 9, -1).indices(10), (9, 9, -1))

        self.assertEqual(
            slice(-100,  100     ).indices(10),
            slice(None).indices(10)
        )
        self.assertEqual(slice(-100, 100, 2).indices(10), (0, 10,  2))

        self.assertEqual(list(range(10))[::sys.maxsize - 1], [0])

        # Negative length should raise ValueError
        with self.assertRaises(ValueError):
            slice(None).indices(-1)

        # Zero step should raise ValueError
        with self.assertRaises(ValueError):
            slice(0, 10, 0).indices(5)

        # ... but it should be fine to use a custom class that provides index.
        self.assertEqual(slice(0, 10, 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, MyIndexable(10), 1).indices(5), (0, 5, 1))

