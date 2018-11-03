# Python test set -- built-in functions

import test.support, unittest
import sys
import itertools

# pure Python implementations (3 args only), for comparison
def pyrange(start, stop, step):
    if (start - stop) // step < 0:
        # replace stop with next element in the sequence of integers
        # that are congruent to start modulo step.
        stop += (start - stop) % step
        while start != stop:
            yield start
            start += step

def pyrange_reversed(start, stop, step):
    stop += (start - stop) % step
    return pyrange(stop - step, start - step, -step)


class RangeTest(unittest.TestCase):
    def assert_iterators_equal(self, xs, ys, test_id, limit=None):
        # check that an iterator xs matches the expected results ys,
        # up to a given limit.
        if limit is not None:
            xs = itertools.islice(xs, limit)
            ys = itertools.islice(ys, limit)
        sentinel = object()
        pairs = itertools.zip_longest(xs, ys, fillvalue=sentinel)
        for i, (x, y) in enumerate(pairs):
            if x == y:
                continue
            elif x == sentinel:
                self.fail('{}: iterator ended unexpectedly '
                          'at position {}; expected {}'.format(test_id, i, y))
            elif y == sentinel:
                self.fail('{}: unexpected excess element {} at '
                          'position {}'.format(test_id, x, i))
            else:
                self.fail('{}: wrong element at position {};'
                          'expected {}, got {}'.format(test_id, i, y, x))

    def test_range(self):
        self.assertEqual(list(range(3)), [0, 1, 2])
        self.assertEqual(list(range(1, 5)), [1, 2, 3, 4])
        self.assertEqual(list(range(0)), [])
        self.assertEqual(list(range(-3)), [])
        self.assertEqual(list(range(1, 10, 3)), [1, 4, 7])
        self.assertEqual(list(range(5, -5, -3)), [5, 2, -1, -4])

        a = 10
        b = 100
        c = 50

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(b, a, -c))
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(-a, -b, -c))
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)

        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)

        self.assertRaises(TypeError, range, 0.0, 2, 1)
        self.assertRaises(TypeError, range, 1, 2.0, 1)
        self.assertRaises(TypeError, range, 1, 2, 1.0)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)

        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")

    def test_invalid_invocation(self):
        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)
        self.assertRaises(TypeError, range, 1., 1., 1.)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)
        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")
        # Exercise various combinations of bad arguments, to check
        # refcounting logic
        self.assertRaises(TypeError, range, 0.0)
        self.assertRaises(TypeError, range, 0, 0.0)
        self.assertRaises(TypeError, range, 0.0, 0)
        self.assertRaises(TypeError, range, 0.0, 0.0)
        self.assertRaises(TypeError, range, 0, 0, 1.0)
        self.assertRaises(TypeError, range, 0, 0.0, 1)
        self.assertRaises(TypeError, range, 0, 0.0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0, 1)
        self.assertRaises(TypeError, range, 0.0, 0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1.0)

    def test_repr(self):
        self.assertEqual(repr(range(1)), 'range(0, 1)')
        self.assertEqual(repr(range(1, 2)), 'range(1, 2)')
        self.assertEqual(repr(range(1, 2, 3)), 'range(1, 2, 3)')

    def test_odd_bug(self):
        # This used to raise a "SystemError: NULL result without error"
        # because the range validation step was eating the exception
        # before NULL was returned.
        with self.assertRaises(TypeError):
            range([], 1, -1)

    def test_types(self):
        # Non-integer objects *equal* to any of the range's items are supposed
        # to be contained in the range.
        self.assertIn(1.0, range(3))
        self.assertIn(True, range(3))
        self.assertIn(1+0j, range(3))

        class C1:
            def __eq__(self, other): return True
        self.assertIn(C1(), range(3))

        # Objects are never coerced into other types for comparison.
        class C2:
            def __int__(self): return 1
            def __index__(self): return 1
        self.assertNotIn(C2(), range(3))

        # Check that the range.__contains__ optimization is only
        # used for ints, not for instances of subclasses of int.
        class C3(int):
            def __eq__(self, other): return True
        self.assertIn(C3(11), range(10))
        self.assertIn(C3(11), list(range(10)))

    def test_strided_limits(self):
        r = range(0, 101, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertIn(2, r)
        self.assertNotIn(99, r)
        self.assertIn(100, r)
        self.assertNotIn(101, r)

        r = range(0, -20, -1)
        self.assertIn(0, r)
        self.assertIn(-1, r)
        self.assertIn(-19, r)
        self.assertNotIn(-20, r)

        r = range(0, -20, -2)
        self.assertIn(-18, r)
        self.assertNotIn(-19, r)
        self.assertNotIn(-20, r)

    def test_empty(self):
        r = range(0)
        self.assertNotIn(0, r)
        self.assertNotIn(1, r)

        r = range(0, -10)
        self.assertNotIn(0, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(1, r)

    def test_slice(self):
        def check(start, stop, step=None):
            i = slice(start, stop, step)
            self.assertEqual(list(r[i]), list(r)[i])
            self.assertEqual(len(r[i]), len(list(r)[i]))
        for r in [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  ]:
            check(0, 2)
            check(0, 20)
            check(1, 2)
            check(20, 30)
            check(-30, -20)
            check(-1, 100, 2)
            check(0, -1)
            check(-1, -3, -1)

    def test_contains(self):
        r = range(10)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -1)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(0, 10, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertNotIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -2)
        self.assertNotIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)

    def test_reverse_iteration(self):
        for r in [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  ]:
            self.assertEqual(list(reversed(r)), list(r)[::-1])

    def test_issue11845(self):
        r = range(*slice(1, 18, 2).indices(20))
        values = {None, 0, 1, -1, 2, -2, 5, -5, 19, -19,
                  20, -20, 21, -21, 30, -30, 99, -99}
        for i in values:
            for j in values:
                for k in values - {0}:
                    r[i:j:k]

    def test_comparison(self):
        test_ranges = [range(0), range(0, -1), range(1, 1, 3),
                       range(1), range(5, 6), range(5, 6, 2),
                       range(5, 7, 2), range(2), range(0, 4, 2),
                       range(0, 5, 2), range(0, 6, 2)]
        test_tuples = list(map(tuple, test_ranges))

        # Check that equality of ranges matches equality of the corresponding
        # tuples for each pair from the test lists above.
        ranges_eq = [a == b for a in test_ranges for b in test_ranges]
        tuples_eq = [a == b for a in test_tuples for b in test_tuples]

        # Check that != correctly gives the logical negation of ==
        ranges_ne = [a != b for a in test_ranges for b in test_ranges]
        self.assertEqual(ranges_ne, [not x for x in ranges_eq])

        # Ranges are unequal to other types (even sequence types)
        self.assertIs(range(0) == (), False)
        self.assertIs(() == range(0), False)
        self.assertIs(range(2) == [0, 1], False)

        # Order comparisons are not implemented for ranges.
        with self.assertRaises(TypeError):
            range(0) < range(0)
        with self.assertRaises(TypeError):
            range(0) > range(0)
        with self.assertRaises(TypeError):
            range(0) <= range(0)
        with self.assertRaises(TypeError):
            range(0) >= range(0)


    def test_attributes(self):
        # test the start, stop and step attributes of range objects
        self.assert_attrs(range(0), 0, 0, 1)
        self.assert_attrs(range(10), 0, 10, 1)
        self.assert_attrs(range(-10), 0, -10, 1)
        self.assert_attrs(range(0, 10, 1), 0, 10, 1)
        self.assert_attrs(range(0, 10, 3), 0, 10, 3)
        self.assert_attrs(range(10, 0, -1), 10, 0, -1)
        self.assert_attrs(range(10, 0, -3), 10, 0, -3)

    def assert_attrs(self, rangeobj, start, stop, step):
        self.assertEqual(rangeobj.start, start)
        self.assertEqual(rangeobj.stop, stop)
        self.assertEqual(rangeobj.step, step)

        with self.assertRaises(AttributeError):
            rangeobj.start = 0
        with self.assertRaises(AttributeError):
            rangeobj.stop = 10
        with self.assertRaises(AttributeError):
            rangeobj.step = 1

        with self.assertRaises(AttributeError):
            del rangeobj.start
        with self.assertRaises(AttributeError):
            del rangeobj.stop
        with self.assertRaises(AttributeError):
            del rangeobj.step

