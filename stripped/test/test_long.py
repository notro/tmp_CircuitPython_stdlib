import unittest

from test import sys                                                            ###

import random
import math

# SHIFT should match the value in longintrepr.h for best testing.
SHIFT = sys.int_info.bits_per_digit
BASE = 2 ** SHIFT
MASK = BASE - 1
KARATSUBA_CUTOFF = 70   # from longobject.c

# Max number of base BASE digits to use in test cases.  Doubling
# this will more than double the runtime.
MAXDIGITS = 5                                                                   ###

# build some special values
special = [0, 1, 2, BASE, BASE >> 1, 0x5555555555555555, 0xaaaaaaaaaaaaaaaa]
#  some solid strings of one bits
p2 = 4  # 0 and 1 already added
for i in range(2*SHIFT):
    special.append(p2 - 1)
    p2 = p2 << 1
del p2
# add complements & negations
special += [~x for x in special] + [-x for x in special]

DBL_MAX = sys.float_info.max
DBL_MAX_EXP = sys.float_info.max_exp
DBL_MIN_EXP = sys.float_info.min_exp
DBL_MANT_DIG = sys.float_info.mant_dig
DBL_MIN_OVERFLOW = 2**DBL_MAX_EXP - 2**(DBL_MAX_EXP - DBL_MANT_DIG - 1)


# Pure Python version of correctly-rounded integer-to-float conversion.
def int_to_float(n):
    """
    Correctly-rounded integer-to-float conversion.

    """
    # Constants, depending only on the floating-point format in use.
    # We use an extra 2 bits of precision for rounding purposes.
    PRECISION = sys.float_info.mant_dig + 2
    SHIFT_MAX = sys.float_info.max_exp - PRECISION
    Q_MAX = 1 << PRECISION
    ROUND_HALF_TO_EVEN_CORRECTION = [0, -1, -2, 1, 0, -1, 2, 1]

    # Reduce to the case where n is positive.
    if n == 0:
        return 0.0
    elif n < 0:
        return -int_to_float(-n)

    # Convert n to a 'floating-point' number q * 2**shift, where q is an
    # integer with 'PRECISION' significant bits.  When shifting n to create q,
    # the least significant bit of q is treated as 'sticky'.  That is, the
    # least significant bit of q is set if either the corresponding bit of n
    # was already set, or any one of the bits of n lost in the shift was set.
    shift = n.bit_length() - PRECISION
    q = n << -shift if shift < 0 else (n >> shift) | bool(n & ~(-1 << shift))

    # Round half to even (actually rounds to the nearest multiple of 4,
    # rounding ties to a multiple of 8).
    q += ROUND_HALF_TO_EVEN_CORRECTION[q & 7]

    # Detect overflow.
    if shift + (q == Q_MAX) > SHIFT_MAX:
        raise OverflowError("integer too large to convert to float")

    # Checks: q is exactly representable, and q**2**shift doesn't overflow.
    assert q % 4 == 0 and q // 4 <= 2**(sys.float_info.mant_dig)
    assert q * 2**shift <= sys.float_info.max

    # Some circularity here, since float(q) is doing an int-to-float
    # conversion.  But here q is of bounded size, and is exactly representable
    # as a float.  In a low-level C-like language, this operation would be a
    # simple cast (e.g., from unsigned long long to double).
    return math.ldexp(float(q), shift)



class LongTest(unittest.TestCase):

    # Get quasi-random long consisting of ndigits digits (in base BASE).
    # quasi == the most-significant digit will not be 0, and the number
    # is constructed to contain long strings of 0 and 1 bits.  These are
    # more likely than random bits to provoke digit-boundary errors.
    # The sign of the number is also random.

    def getran(self, ndigits):
        self.assertGreater(ndigits, 0)
        nbits_hi = ndigits * SHIFT
        nbits_lo = nbits_hi - SHIFT + 1
        answer = 0
        nbits = 0
        r = int(random.random() * (SHIFT * 2)) | 1  # force 1 bits to start
        while nbits < nbits_lo:
            bits = (r >> 1) + 1
            bits = min(bits, nbits_hi - nbits)
            self.assertTrue(1 <= bits <= SHIFT)
            nbits = nbits + bits
            answer = answer << bits
            if r & 1:
                answer = answer | ((1 << bits) - 1)
            r = int(random.random() * (SHIFT * 2))
        self.assertTrue(nbits_lo <= nbits <= nbits_hi)
        if random.random() < 0.5:
            answer = -answer
        return answer

    # Get random long consisting of ndigits random digits (relative to base
    # BASE).  The sign bit is also random.

    def getran2(ndigits):
        answer = 0
        for i in range(ndigits):
            answer = (answer << SHIFT) | random.randint(0, MASK)
        if random.random() < 0.5:
            answer = -answer
        return answer

    def check_division(self, x, y):
        eq = self.assertEqual
        if True:                                                                ###
            q, r = divmod(x, y)
            q2, r2 = x//y, x%y
            pab, pba = x*y, y*x
            eq(pab, pba, "multiplication does not commute")
            eq(q, q2, "divmod returns different quotient than /")
            eq(r, r2, "divmod returns different mod than %")
            eq(x, q*y + r, "x != q*y + r after divmod")
            if y > 0:
                self.assertTrue(0 <= r < y, "bad mod from divmod")
            else:
                self.assertTrue(y < r <= 0, "bad mod from divmod")

    def test_division(self):
        digits = list(range(1, MAXDIGITS+1)) + list(range(KARATSUBA_CUTOFF,
                                                      KARATSUBA_CUTOFF + 1))    ###
        digits.append(KARATSUBA_CUTOFF * 3)
        for lenx in digits:
            x = self.getran(lenx)
            for leny in digits:
                y = self.getran(leny) or 1
                self.check_division(x, y)

        # specific numbers chosen to exercise corner cases of the
        # current long division implementation

        # 30-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(1231948412290879395966702881,
                            1147341367131428698)
        self.check_division(815427756481275430342312021515587883,
                       707270836069027745)
        self.check_division(627976073697012820849443363563599041,
                       643588798496057020)
        self.check_division(1115141373653752303710932756325578065,
                       1038556335171453937726882627)
        # 30-bit cases that require the post-subtraction correction step
        self.check_division(922498905405436751940989320930368494,
                       949985870686786135626943396)
        self.check_division(768235853328091167204009652174031844,
                       1091555541180371554426545266)

        # 15-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(20172188947443, 615611397)
        self.check_division(1020908530270155025, 950795710)
        self.check_division(128589565723112408, 736393718)
        self.check_division(609919780285761575, 18613274546784)
        # 15-bit cases that require the post-subtraction correction step
        self.check_division(710031681576388032, 26769404391308)
        self.check_division(1933622614268221, 30212853348836)



    def test_karatsuba(self):
        digits = list(range(1, 5)) + list(range(KARATSUBA_CUTOFF,
                                                KARATSUBA_CUTOFF + 1))          ###

        bits = [digit * SHIFT for digit in digits]

        # Test products of long strings of 1 bits -- (2**x-1)*(2**y-1) ==
        # 2**(x+y) - 2**x - 2**y + 1, so the proper result is easy to check.
        for abits in bits:
            a = (1 << abits) - 1
            for bbits in bits:
                if bbits < abits:
                    continue
                if True:                                                        ###
                    b = (1 << bbits) - 1
                    x = a * b
                    y = ((1 << (abits + bbits)) -
                         (1 << abits) -
                         (1 << bbits) +
                         1)
                    self.assertEqual(x, y)

    def check_bitop_identities_1(self, x):
        eq = self.assertEqual
        if True:                                                                ###
            eq(x & 0, 0)
            eq(x | 0, x)
            eq(x ^ 0, x)
            eq(x & -1, x)
            eq(x | -1, -1)
            eq(x ^ -1, ~x)
            eq(x, ~~x)
            eq(x & x, x)
            eq(x | x, x)
            eq(x ^ x, 0)
            eq(x & ~x, 0)
            eq(x | ~x, -1)
            eq(x ^ ~x, -1)
            eq(-x, 1 + ~x)
            eq(-x, ~(x-1))
        for n in range(2*SHIFT):
            p2 = 2 ** n
            if True:                                                            ###
                eq(x << n >> n, x)
                eq(x // p2, x >> n)
                eq(x * p2, x << n)
                eq(x & -p2, x >> n << n)
                eq(x & -p2, x & ~(p2 - 1))

    def check_bitop_identities_2(self, x, y):
        eq = self.assertEqual
        if True:                                                                ###
            eq(x & y, y & x)
            eq(x | y, y | x)
            eq(x ^ y, y ^ x)
            eq(x ^ y ^ x, y)
            eq(x & y, ~(~x | ~y))
            eq(x | y, ~(~x & ~y))
            eq(x ^ y, (x | y) & ~(x & y))
            eq(x ^ y, (x & ~y) | (~x & y))
            eq(x ^ y, (x | y) & (~x | ~y))

    def check_bitop_identities_3(self, x, y, z):
        eq = self.assertEqual
        if True:                                                                ###
            eq((x & y) & z, x & (y & z))
            eq((x | y) | z, x | (y | z))
            eq((x ^ y) ^ z, x ^ (y ^ z))
            eq(x & (y | z), (x & y) | (x & z))
            eq(x | (y & z), (x | y) & (x | z))

    def test_bitop_identities(self):
        special = [0, 1, 2] #, BASE, BASE >> 1, 0x5555555555555555, 0xaaaaaaaaaaaaaaaa]    #########################
        for x in special:
            self.check_bitop_identities_1(x)
        digits = range(1, MAXDIGITS+1)
        for lenx in digits:
            x = self.getran(lenx)
            self.check_bitop_identities_1(x)
            for leny in digits:
                y = self.getran(leny)
                self.check_bitop_identities_2(x, y)
                self.check_bitop_identities_3(x, y, self.getran((lenx + leny)//2))

    def slow_format(self, x, base):
        digits = []
        sign = 0
        if x < 0:
            sign, x = 1, -x
        while x:
            x, r = divmod(x, base)
            digits.append(int(r))
        digits.reverse()
        digits = digits or [0]
        return '-'[:sign] + \
               {2: '0b', 8: '0o', 10: '', 16: '0x'}[base] + \
               "".join("0123456789abcdef"[i] for i in digits)

    def check_format_1(self, x):
        for base, mapper in (2, bin), (8, oct), (10, str), (10, repr), (16, hex):
            got = mapper(x)
            if True:                                                            ###
                expected = self.slow_format(x, base)
                self.assertEqual(got, expected)
            if True:                                                            ###
                self.assertEqual(int(got, 0), x)

    def test_format(self):
        for x in special:
            self.check_format_1(x)
        for i in range(10):
            for lenx in range(1, MAXDIGITS+1):
                x = self.getran(lenx)
                self.check_format_1(x)

    def test_long(self):
        # Check conversions from string
        LL = [
                ('1' + '0'*20, 10**20),
                ('1' + '0'*100, 10**100)
        ]
        for s, v in LL:
            for sign in "", "+", "-":
                for prefix in "", " ", "\t", "  \t\t  ":
                    ss = prefix + sign + s
                    vv = v
                    if sign == "-" and v is not ValueError:
                        vv = -v
                    try:
                        self.assertEqual(int(ss), vv)
                    except ValueError:
                        pass

        # trailing L should no longer be accepted...
        self.assertRaises(ValueError, int, '123L')
        self.assertRaises(ValueError, int, '123l')
        self.assertRaises(ValueError, int, '0L')
        self.assertRaises(ValueError, int, '-37L')
        self.assertRaises(ValueError, int, '0x32L', 16)
        self.assertRaises(ValueError, int, '1L', 21)
        # ... but it's just a normal digit if base >= 22
        self.assertEqual(int('1L', 22), 43)

        # tests with base 0
        self.assertEqual(int('000', 0), 0)
        self.assertEqual(int('0o123', 0), 83)
        self.assertEqual(int('0x123', 0), 291)
        self.assertEqual(int('0b100', 0), 4)
        self.assertEqual(int(' 0O123   ', 0), 83)
        self.assertEqual(int(' 0X123  ', 0), 291)
        self.assertEqual(int(' 0B100 ', 0), 4)
        self.assertEqual(int('0', 0), 0)
        self.assertEqual(int('+0', 0), 0)
        self.assertEqual(int('-0', 0), 0)
        self.assertEqual(int('00', 0), 0)

        # invalid bases
        invalid_bases = [-909,
                          ]
        for base in invalid_bases:
            self.assertRaises(ValueError, int, '42', base)


    def test_conversion(self):

        class JustLong:
            # test that __long__ no longer used in 3.x
            def __long__(self):
                return 42
        self.assertRaises(TypeError, int, JustLong())

    def check_float_conversion(self, n):
        # Check that int -> float conversion behaviour matches
        # that of the pure Python version above.
        try:
            actual = float(n)
        except OverflowError:
            actual = 'overflow'

        try:
            expected = int_to_float(n)
        except OverflowError:
            expected = 'overflow'

        msg = ("Error in conversion of integer {} to float.  "
               "Got {}, expected {}.".format(n, actual, expected))
        self.assertEqual(actual, expected, msg)

    def test_float_conversion(self):

        exact_values = [0, 1, 2,
                         2**53-3,
                         2**53-2,
                         2**53-1,
                         2**53,
                         2**53+2,
                         2**54-4,
                         2**54-2,
                         2**54,
                         2**54+4]
        for x in exact_values:
            self.assertEqual(float(x), x)
            self.assertEqual(float(-x), -x)

        # behaviour near extremes of floating-point range
        int_dbl_max = int(DBL_MAX)
        top_power = 2**DBL_MAX_EXP
        halfway = (int_dbl_max + top_power)//2
        self.assertEqual(float(int_dbl_max), DBL_MAX)
        self.assertEqual(float(int_dbl_max+1), DBL_MAX)
        self.assertEqual(float(halfway-1), DBL_MAX)
        self.assertEqual(float(1-halfway), -DBL_MAX)

    def test_logs(self):
        LOG10E = 0.4342944819032518                                             ###

        for exp in list(range(10)) + [20, 30]:                                  ###
            value = 10 ** exp
            # log10(value) == exp, so log(value) == log10(value)/log10(e) ==
            # exp/LOG10E
            expected = exp / LOG10E
            log = math.log(value)
            self.assertAlmostEqual(log, expected)

        for bad in -(1 << 10000), -2, 0:
            self.assertRaises(ValueError, math.log, bad)

    def test_mixed_compares(self):
        eq = self.assertEqual

        # We're mostly concerned with that mixing floats and ints does the
        # right stuff, even when ints are too large to fit in a float.
        # The safest way to check the results is to use an entirely different
        # method, which we do here via a skeletal rational class (which
        # represents all Python ints and floats exactly).
        class Rat:
            def __init__(self, value):
                if isinstance(value, int):
                    self.n = value
                    self.d = 1
                elif isinstance(value, float):
                    # Convert to exact rational equivalent.
                    f, e = math.frexp(abs(value))
                    assert f == 0 or 0.5 <= f < 1.0
                    # |value| = f * 2**e exactly

                    # Suck up CHUNK bits at a time; 28 is enough so that we suck
                    # up all bits in 2 iterations for all known binary double-
                    # precision formats, and small enough to fit in an int.
                    CHUNK = 28
                    top = 0
                    # invariant: |value| = (top + f) * 2**e exactly
                    while f:
                        f = math.ldexp(f, CHUNK)
                        digit = int(f)
                        assert digit >> CHUNK == 0
                        top = (top << CHUNK) | digit
                        f -= digit
                        assert 0.0 <= f < 1.0
                        e -= CHUNK

                    # Now |value| = top * 2**e exactly.
                    if e >= 0:
                        n = top << e
                        d = 1
                    else:
                        n = top
                        d = 1 << -e
                    if value < 0:
                        n = -n
                    self.n = n
                    self.d = d
                    assert float(n) / float(d) == value
                else:
                    raise TypeError("can't deal with %r" % value)

            def _cmp__(self, other):
                if not isinstance(other, Rat):
                    other = Rat(other)
                x, y = self.n * other.d, self.d * other.n
                return (x > y) - (x < y)
            def __eq__(self, other):
                return self._cmp__(other) == 0
            def __ne__(self, other):
                return self._cmp__(other) != 0
            def __ge__(self, other):
                return self._cmp__(other) >= 0
            def __gt__(self, other):
                return self._cmp__(other) > 0
            def __le__(self, other):
                return self._cmp__(other) <= 0
            def __lt__(self, other):
                return self._cmp__(other) < 0

        cases = [0, 0.001, 0.99, 1.0, 1.5, 1e20]                                ###
        # 2**48 is an important boundary in the internals.  2**53 is an
        # important boundary for IEEE double precision.
        for t in 2.0**48, 2.0**50, 2.0**53:
            cases.extend([t - 1.0, t - 0.3, t, t + 0.3, t + 1.0,
                          int(t-1), int(t), int(t+1)])
        cases.extend([-x for x in cases])
        for x in cases:
            Rx = Rat(x)
            for y in cases:
                Ry = Rat(y)
                Rcmp = (Rx > Ry) - (Rx < Ry)
                if True:                                                        ###
                    xycmp = (x > y) - (x < y)
                    eq(Rcmp, xycmp)
                    eq(x == y, Rcmp == 0)
                    eq(x != y, Rcmp != 0)
                    eq(x < y, Rcmp < 0)
                    eq(x <= y, Rcmp <= 0)
                    eq(x > y, Rcmp > 0)
                    eq(x >= y, Rcmp >= 0)

    def test_nan_inf(self):
        self.assertRaises(OverflowError, int, float('inf'))
        self.assertRaises(OverflowError, int, float('-inf'))
        self.assertRaises(ValueError, int, float('nan'))

    def test_small_ints(self):
        for i in range(-5, 257):
            self.assertIs(i, i + 0)
            self.assertIs(i, i * 1)
            self.assertIs(i, i - 0)
            self.assertIs(i, i // 1)
            self.assertIs(i, i & -1)
            self.assertIs(i, i | 0)
            self.assertIs(i, i ^ 0)
            self.assertIs(i, ~~i)
            self.assertIs(i, i**1)
            self.assertIs(i, int(str(i)))
            self.assertIs(i, i<<2>>2, str(i))

    def test_to_bytes(self):
        def check(tests, byteorder, signed=False):
            for test, expected in tests.items():
                try:
                    self.assertEqual(
                        test.to_bytes(len(expected), byteorder),                ### signed kw not implemented, false assumed
                        expected)
                except Exception as err:
                    raise AssertionError(
                        "failed to convert {0} with byteorder={1} and signed={2}"
                        .format(test, byteorder, signed)) from err

        # Convert integers to unsigned big-endian byte arrays.
        tests3 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x01\x00',
            32767: b'\x7f\xff',
            32768: b'\x80\x00',
            65535: b'\xff\xff',
            65536: b'\x01\x00\x00'
        }
        check(tests3, 'big', signed=False)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x00\x01',
            32767: b'\xff\x7f',
            32768: b'\x00\x80',
            65535: b'\xff\xff',
            65536: b'\x00\x00\x01'
        }
        check(tests4, 'little', signed=False)

        self.assertEqual((0).to_bytes(0, 'big'), b'')
        self.assertEqual((1).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x01')
        self.assertEqual((0).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x00')

    def test_from_bytes(self):
        def check(tests, byteorder, signed=False):
            for test, expected in tests.items():
                try:
                    self.assertEqual(
                        int.from_bytes(test, byteorder),                        ###
                        expected)
                except Exception as err:
                    raise AssertionError(
                        "failed to convert {0} with byteorder={1!r} and signed={2}"
                        .format(test, byteorder, signed)) from err

        # Convert unsigned big-endian byte arrays to integers.
        tests3 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x01\x00': 256,
            b'\x7f\xff': 32767,
            b'\x80\x00': 32768,
            b'\xff\xff': 65535,
            b'\x01\x00\x00': 65536,
        }
        check(tests3, 'big', signed=False)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x00\x01': 256,
            b'\xff\x7f': 32767,
            b'\x00\x80': 32768,
            b'\xff\xff': 65535,
            b'\x00\x00\x01': 65536,
        }
        check(tests4, 'little', signed=False)

        class myint(int):
            pass

        self.assertEqual(myint.from_bytes(b'\x01', 'big'), 1)
        self.assertEqual(myint.from_bytes(b'\x01', 'little'), 1)
        self.assertRaises(TypeError, int.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', True)
        self.assertRaises(TypeError, myint.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', True)

    def test_shift_bool(self):
        # Issue #21422: ensure that bool << int and bool >> int return int
        for value in (True, False):
            for shift in (0, 2):
                self.assertEqual(type(value << shift), int)
                self.assertEqual(type(value >> shift), int)


