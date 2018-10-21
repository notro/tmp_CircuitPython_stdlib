
import math
import operator
import os
import random
import sys
import struct
import time
import unittest

from test import support
from math import isinf, isnan, copysign, ldexp

INF = float("inf")
NAN = float("nan")


class FloatSubclass(float):
    pass

class OtherFloatSubclass(float):
    pass

class GeneralFloatCases(unittest.TestCase):

    def test_float(self):
        self.assertEqual(float(3.14), 3.14)
        self.assertEqual(float(314), 314.0)
        self.assertEqual(float("  3.14  "), 3.14)
        self.assertRaises(ValueError, float, "  0x3.1  ")
        self.assertRaises(ValueError, float, "  -0x3.p-1  ")
        self.assertRaises(ValueError, float, "  +0x3.p-1  ")
        self.assertRaises(ValueError, float, "++3.14")
        self.assertRaises(ValueError, float, "+-3.14")
        self.assertRaises(ValueError, float, "-+3.14")
        self.assertRaises(ValueError, float, "--3.14")
        self.assertRaises(ValueError, float, ".nan")
        self.assertRaises(ValueError, float, "+.inf")
        self.assertRaises(TypeError, float, {})
        # check that we don't accept alternate exponent markers
        self.assertRaises(ValueError, float, "-1.7d29")
        self.assertRaises(ValueError, float, "3D-14")
        # extra long strings should not be a problem
        float(b'.' + b'1'*1000)
        float('.' + '1'*1000)

    def test_float_memoryview(self):
        self.assertEqual(float(memoryview(b'12.3')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3\x00')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3 ')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3A')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.34')[1:4]), 2.3)

    def test_error_message(self):
        testlist = ('\xbd', '123\xbd', '  123 456  ')
        for s in testlist:
            try:
                float(s)
            except ValueError as e:
                self.assertIn('invalid', e.args[0])                             ###
            else:
                self.fail("Expected int(%r) to raise a ValueError", s)


    def test_float_with_comma(self):
        # set locale to something that doesn't use '.' for the decimal point
        # float must not accept the locale specific decimal point but
        # it still has to accept the normal python syntax

        self.assertEqual(float("  3.14  "), 3.14)
        self.assertEqual(float("+3.14  "), 3.14)
        self.assertEqual(float("-3.14  "), -3.14)
        self.assertEqual(float(".14  "), .14)
        self.assertEqual(float("3.  "), 3.0)
        self.assertEqual(float("3.e3  "), 3000.0)
        self.assertEqual(float("3.2e3  "), 3200.0)
        self.assertEqual(float("2.5e-1  "), 0.25)
        self.assertEqual(float("5e-1"), 0.5)
        self.assertRaises(ValueError, float, "  3,14  ")
        self.assertRaises(ValueError, float, "  +3,14  ")
        self.assertRaises(ValueError, float, "  -3,14  ")
        self.assertRaises(ValueError, float, "  0x3.1  ")
        self.assertRaises(ValueError, float, "  -0x3.p-1  ")
        self.assertRaises(ValueError, float, "  +0x3.p-1  ")
        self.assertEqual(float("  25.e-1  "), 2.5)
        self.assertAlmostEqual(float("  .25e-1  "), .025)

    def test_float_containment(self):
        floats = (INF, -INF, 0.0, 1.0)                                          ###
        for f in floats:
            self.assertIn(f, {f})
            self.assertIn(f, {f: None})
            self.assertEqual([f].count(f), 1, "[].count('%r') != 1" % f)
            self.assertIn(f, floats)

        for f in floats:
            # nonidentical containers, same type, same contents
            self.assertTrue([f] == [f], "[%r] != [%r]" % (f, f))
            self.assertTrue((f,) == (f,), "(%r,) != (%r,)" % (f, f))
            self.assertTrue({f} == {f}, "{%r} != {%r}" % (f, f))
            self.assertTrue({f : None} == {f: None}, "{%r : None} != "
                                                   "{%r : None}" % (f, f))

            # identical containers
            l, t, s, d = [f], (f,), {f}, {f: None}
            self.assertTrue(l == l, "[%r] not equal to itself" % f)
            self.assertTrue(t == t, "(%r,) not equal to itself" % f)
            self.assertTrue(s == s, "{%r} not equal to itself" % f)
            self.assertTrue(d == d, "{%r : None} not equal to itself" % f)

    def assertEqualAndEqualSign(self, a, b):
        # fail unless a == b and a and b have the same sign bit;
        # the only difference from assertEqual is that this test
        # distinguishes -0.0 and 0.0.
        self.assertEqual((a, copysign(1.0, a)), (b, copysign(1.0, b)))

    def test_float_pow(self):
        # test builtin pow and ** operator for IEEE 754 special cases.
        # Special cases taken from section F.9.4.4 of the C99 specification

        for pow_op in pow, operator.pow:
            # x**NAN is NAN for any x except 1
            self.assertTrue(isnan(pow_op(-0.0, NAN)))
            self.assertTrue(isnan(pow_op(0.0, NAN)))
            self.assertTrue(isnan(pow_op(0.5, NAN)))
            self.assertTrue(isnan(pow_op(2.0, NAN)))
            self.assertTrue(isnan(pow_op(INF, NAN)))
            self.assertTrue(isnan(pow_op(NAN, NAN)))

            # NAN**y is NAN for any y except +-0
            self.assertTrue(isnan(pow_op(NAN, -INF)))
            self.assertTrue(isnan(pow_op(NAN, -2.0)))
            self.assertTrue(isnan(pow_op(NAN, -1.0)))
            self.assertTrue(isnan(pow_op(NAN, -0.5)))
            self.assertTrue(isnan(pow_op(NAN, 0.5)))
            self.assertTrue(isnan(pow_op(NAN, 1.0)))
            self.assertTrue(isnan(pow_op(NAN, 2.0)))
            self.assertTrue(isnan(pow_op(NAN, INF)))

            # (+-0)**y raises ZeroDivisionError for y a negative odd integer
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -1.0)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -1.0)

            # (+-0)**y raises ZeroDivisionError for y finite and negative
            # but not an odd integer
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -2.0)
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -0.5)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -2.0)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -0.5)

            # (+-0)**y is +-0 for y a positive odd integer
            self.assertEqualAndEqualSign(pow_op(-0.0, 1.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 1.0), 0.0)

            # (+-0)**y is 0 for y finite and positive but not an odd integer
            self.assertEqualAndEqualSign(pow_op(-0.0, 0.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, 2.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 0.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 2.0), 0.0)

            # (-1)**+-inf is 1
            self.assertEqualAndEqualSign(pow_op(-1.0, -INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, INF), 1.0)

            # 1**y is 1 for any y, even if y is an infinity or nan
            self.assertEqualAndEqualSign(pow_op(1.0, -INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -1.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.5), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.5), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 1.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, NAN), 1.0)

            # x**+-0 is 1 for any x, even if x is a zero, infinity, or nan
            self.assertEqualAndEqualSign(pow_op(-INF, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(INF, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(NAN, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-INF, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.5, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(INF, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(NAN, -0.0), 1.0)

            # x**y defers to complex pow for finite negative x and
            # non-integral y.
            self.assertEqual(type(pow_op(-2.0, -0.5)), complex)
            self.assertEqual(type(pow_op(-2.0, 0.5)), complex)
            self.assertEqual(type(pow_op(-1.0, -0.5)), complex)
            self.assertEqual(type(pow_op(-1.0, 0.5)), complex)
            self.assertEqual(type(pow_op(-0.5, -0.5)), complex)
            self.assertEqual(type(pow_op(-0.5, 0.5)), complex)

            # x**-INF is INF for abs(x) < 1
            self.assertEqualAndEqualSign(pow_op(-0.5, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(-0.0, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(0.0, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(0.5, -INF), INF)

            # x**-INF is 0 for abs(x) > 1
            self.assertEqualAndEqualSign(pow_op(-INF, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -INF), 0.0)

            # x**INF is 0 for abs(x) < 1
            self.assertEqualAndEqualSign(pow_op(-0.5, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, INF), 0.0)

            # x**INF is INF for abs(x) > 1
            self.assertEqualAndEqualSign(pow_op(-INF, INF), INF)
            self.assertEqualAndEqualSign(pow_op(-2.0, INF), INF)
            self.assertEqualAndEqualSign(pow_op(2.0, INF), INF)
            self.assertEqualAndEqualSign(pow_op(INF, INF), INF)

            # (-INF)**y is -0.0 for y a negative odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, -1.0), -0.0)

            # (-INF)**y is 0.0 for y negative but not an odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, -2.0), 0.0)

            # (-INF)**y is -INF for y a positive odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, 1.0), -INF)

            # (-INF)**y is INF for y positive but not an odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, 2.0), INF)

            # INF**y is INF for y positive
            self.assertEqualAndEqualSign(pow_op(INF, 0.5), INF)
            self.assertEqualAndEqualSign(pow_op(INF, 1.0), INF)
            self.assertEqualAndEqualSign(pow_op(INF, 2.0), INF)

            # INF**y is 0.0 for y negative
            self.assertEqualAndEqualSign(pow_op(INF, -2.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -1.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -0.5), 0.0)

            # basic checks not covered by the special cases above
            self.assertEqualAndEqualSign(pow_op(-2.0, -2.0), 0.25)
            self.assertEqualAndEqualSign(pow_op(-2.0, -1.0), -0.5)
            self.assertEqualAndEqualSign(pow_op(-2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 1.0), -2.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 2.0), 4.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -1.0), -1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 1.0), -1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2.0), 0.25)
            self.assertEqualAndEqualSign(pow_op(2.0, -1.0), 0.5)
            self.assertEqualAndEqualSign(pow_op(2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 1.0), 2.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 2.0), 4.0)

            # 1 ** large and -1 ** large; some libms apparently
            # have problems with these
            self.assertEqualAndEqualSign(pow_op(1.0, -1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 1e100), 1.0)

            # check sign for results that underflow to 0
            self.assertEqualAndEqualSign(pow_op(-2.0, -2000.0), 0.0)
            self.assertEqual(type(pow_op(-2.0, -2000.5)), complex)
            self.assertEqualAndEqualSign(pow_op(-2.0, -2001.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2000.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2000.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2001.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, 2000.0), 0.0)
            self.assertEqual(type(pow_op(-0.5, 2000.5)), complex)
            self.assertEqualAndEqualSign(pow_op(-0.5, 2001.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2000.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2000.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2001.0), 0.0)

            # check we don't raise an exception for subnormal results,
            # and validate signs.  Tests currently disabled, since
            # they fail on systems where a subnormal result from pow
            # is flushed to zero (e.g. Debian/ia64.)
            #self.assertTrue(0.0 < pow_op(0.5, 1048) < 1e-315)
            #self.assertTrue(0.0 < pow_op(-0.5, 1048) < 1e-315)
            #self.assertTrue(0.0 < pow_op(0.5, 1047) < 1e-315)
            #self.assertTrue(0.0 > pow_op(-0.5, 1047) > -1e-315)
            #self.assertTrue(0.0 < pow_op(2.0, -1048) < 1e-315)
            #self.assertTrue(0.0 < pow_op(-2.0, -1048) < 1e-315)
            #self.assertTrue(0.0 < pow_op(2.0, -1047) < 1e-315)
            #self.assertTrue(0.0 > pow_op(-2.0, -1047) > -1e-315)


BE_DOUBLE_INF = b'\x7f\xf0\x00\x00\x00\x00\x00\x00'
LE_DOUBLE_INF = bytes(reversed(BE_DOUBLE_INF))
BE_DOUBLE_NAN = b'\x7f\xf8\x00\x00\x00\x00\x00\x00'
LE_DOUBLE_NAN = bytes(reversed(BE_DOUBLE_NAN))

BE_FLOAT_INF = b'\x7f\x80\x00\x00'
LE_FLOAT_INF = bytes(reversed(BE_FLOAT_INF))
BE_FLOAT_NAN = b'\x7f\xc0\x00\x00'
LE_FLOAT_NAN = bytes(reversed(BE_FLOAT_NAN))


# on an IEEE platform, all we guarantee is that bit patterns
# representing infinities or NaNs do not raise an exception; all else
# is accident (today).
# let's also try to guarantee that -0.0 and 0.0 don't get confused.

class IEEEFormatTestCase(unittest.TestCase):

    def test_double_specials_do_unpack(self):
        for fmt, data in [('>d', BE_DOUBLE_INF),
                          ('>d', BE_DOUBLE_NAN),
                          ('<d', LE_DOUBLE_INF),
                          ('<d', LE_DOUBLE_NAN)]:
            struct.unpack(fmt, data)

    def test_float_specials_do_unpack(self):
        for fmt, data in [('>f', BE_FLOAT_INF),
                          ('>f', BE_FLOAT_NAN),
                          ('<f', LE_FLOAT_INF),
                          ('<f', LE_FLOAT_NAN)]:
            struct.unpack(fmt, data)

class RoundTestCase(unittest.TestCase):

    def test_inf_nan(self):
        self.assertRaises(OverflowError, round, INF)
        self.assertRaises(OverflowError, round, -INF)
        self.assertRaises(ValueError, round, NAN)
        self.assertRaises(TypeError, round, INF, 0.0)
        self.assertRaises(TypeError, round, -INF, 1.0)
        self.assertRaises(TypeError, round, NAN, "ceci n'est pas un integer")
        self.assertRaises(TypeError, round, -0.0, 1j)

    def test_large_n(self):
        for n in [34, 35]:                                                      ###
            self.assertEqual(round(123.456, n), 123.456)
            self.assertEqual(round(-123.456, n), -123.456)
            self.assertEqual(round(1e300, n), 1e300)
            self.assertEqual(round(1e-320, n), 1e-320)

    def test_small_n(self):
        for n in [-38, -39, -40]:                                               ###
            self.assertEqual(round(123.456, n), 0.0)
            self.assertEqual(round(-123.456, n), -0.0)

    def test_previous_round_bugs(self):
        # particular cases that have occurred in bug reports
        self.assertEqual(round(562949953421312.5, 1),
                          562949953421312.5)
        self.assertEqual(round(56294995342131.5, 3),
                         56294995342131.5)
        # round-half-even
        self.assertEqual(round(25.0, -1), 20.0)
        self.assertEqual(round(35.0, -1), 40.0)
        self.assertEqual(round(45.0, -1), 40.0)
        self.assertEqual(round(55.0, -1), 60.0)
        self.assertEqual(round(65.0, -1), 60.0)
        self.assertEqual(round(75.0, -1), 80.0)
        self.assertEqual(round(85.0, -1), 80.0)
        self.assertEqual(round(95.0, -1), 100.0)

    def test_format_specials(self):
        # Test formatting of nans and infs.

        def test(fmt, value, expected):
            # Test with both % and format().
            self.assertEqual(fmt % value, expected, fmt)

        for fmt in ['%e', '%f', '%g', '%.0e', '%.6f', '%.20g',
                    '%#e', '%#f', '%#g', '%#.20e', '%#.15f', '%#.3g']:
            pfmt = '%+' + fmt[1:]
            sfmt = '% ' + fmt[1:]
            test(fmt, INF, 'inf')
            test(fmt, -INF, '-inf')
            test(fmt, NAN, 'nan')
            test(fmt, -NAN, 'nan')
            # When asking for a sign, it's always provided. nans are
            #  always positive.
            test(pfmt, INF, '+inf')
            test(pfmt, -INF, '-inf')
            test(pfmt, NAN, '+nan')
            test(pfmt, -NAN, '+nan')
            # When using ' ' for a sign code, only infs can be negative.
            #  Others have a space.
            test(sfmt, INF, ' inf')
            test(sfmt, -INF, '-inf')
            test(sfmt, NAN, ' nan')
            test(sfmt, -NAN, ' nan')


# Beginning with Python 2.6 float has cross platform compatible
# ways to create and represent inf and nan
class InfNanTest(unittest.TestCase):
    def test_inf_from_str(self):
        self.assertTrue(isinf(float("inf")))
        self.assertTrue(isinf(float("+inf")))
        self.assertTrue(isinf(float("-inf")))
        self.assertTrue(isinf(float("infinity")))
        self.assertTrue(isinf(float("+infinity")))
        self.assertTrue(isinf(float("-infinity")))

        self.assertEqual(repr(float("inf")), "inf")
        self.assertEqual(repr(float("+inf")), "inf")
        self.assertEqual(repr(float("-inf")), "-inf")
        self.assertEqual(repr(float("infinity")), "inf")
        self.assertEqual(repr(float("+infinity")), "inf")
        self.assertEqual(repr(float("-infinity")), "-inf")

        self.assertEqual(repr(float("INF")), "inf")
        self.assertEqual(repr(float("+Inf")), "inf")
        self.assertEqual(repr(float("-iNF")), "-inf")
        self.assertEqual(repr(float("Infinity")), "inf")
        self.assertEqual(repr(float("+iNfInItY")), "inf")
        self.assertEqual(repr(float("-INFINITY")), "-inf")

        self.assertEqual(str(float("inf")), "inf")
        self.assertEqual(str(float("+inf")), "inf")
        self.assertEqual(str(float("-inf")), "-inf")
        self.assertEqual(str(float("infinity")), "inf")
        self.assertEqual(str(float("+infinity")), "inf")
        self.assertEqual(str(float("-infinity")), "-inf")

        self.assertRaises(ValueError, float, "info")
        self.assertRaises(ValueError, float, "+info")
        self.assertRaises(ValueError, float, "-info")
        self.assertRaises(ValueError, float, "in")
        self.assertRaises(ValueError, float, "+in")
        self.assertRaises(ValueError, float, "-in")
        self.assertRaises(ValueError, float, "infinit")
        self.assertRaises(ValueError, float, "+Infin")
        self.assertRaises(ValueError, float, "-INFI")
        self.assertRaises(ValueError, float, "infinitys")

        self.assertRaises(ValueError, float, "++Inf")
        self.assertRaises(ValueError, float, "-+inf")
        self.assertRaises(ValueError, float, "+-infinity")
        self.assertRaises(ValueError, float, "--Infinity")

    def test_inf_as_str(self):
        self.assertEqual(repr(1e300 * 1e300), "inf")
        self.assertEqual(repr(-1e300 * 1e300), "-inf")

        self.assertEqual(str(1e300 * 1e300), "inf")
        self.assertEqual(str(-1e300 * 1e300), "-inf")

    def test_nan_from_str(self):
        self.assertTrue(isnan(float("nan")))
        self.assertTrue(isnan(float("+nan")))
        self.assertTrue(isnan(float("-nan")))

        self.assertEqual(repr(float("nan")), "nan")
        self.assertEqual(repr(float("+nan")), "nan")
        self.assertEqual(repr(float("-nan")), "nan")

        self.assertEqual(repr(float("NAN")), "nan")
        self.assertEqual(repr(float("+NAn")), "nan")
        self.assertEqual(repr(float("-NaN")), "nan")

        self.assertEqual(str(float("nan")), "nan")
        self.assertEqual(str(float("+nan")), "nan")
        self.assertEqual(str(float("-nan")), "nan")

        self.assertRaises(ValueError, float, "nana")
        self.assertRaises(ValueError, float, "+nana")
        self.assertRaises(ValueError, float, "-nana")
        self.assertRaises(ValueError, float, "na")
        self.assertRaises(ValueError, float, "+na")
        self.assertRaises(ValueError, float, "-na")

        self.assertRaises(ValueError, float, "++nan")
        self.assertRaises(ValueError, float, "-+NAN")
        self.assertRaises(ValueError, float, "+-NaN")
        self.assertRaises(ValueError, float, "--nAn")

    def test_nan_as_str(self):
        self.assertEqual(repr(1e300 * 1e300 * 0), "nan")
        self.assertEqual(repr(-1e300 * 1e300 * 0), "nan")

        self.assertEqual(str(1e300 * 1e300 * 0), "nan")
        self.assertEqual(str(-1e300 * 1e300 * 0), "nan")

    def test_inf_signs(self):
        self.assertEqual(copysign(1.0, float('inf')), 1.0)
        self.assertEqual(copysign(1.0, float('-inf')), -1.0)

    def test_nan_signs(self):
        # When using the dtoa.c code, the sign of float('nan') should
        # be predictable.
        self.assertEqual(copysign(1.0, float('nan')), 1.0)
        self.assertEqual(copysign(1.0, float('-nan')), -1.0)


