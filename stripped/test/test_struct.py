import array
import operator
import unittest
import struct
import sys

from test import support

try:                                                                            ###
    import binascii                                                             ###
except ImportError:                                                             ###
    class binascii:                                                             ###
        def unhexlify(data):                                                    ###
            return bytes([ int(data[i:i+2], 16) for i in range(0, len(data), 2) ])  ###
                                                                                ###
ISBIGENDIAN = sys.byteorder == "big"

integer_codes = 'b', 'B', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q'                ###
byteorders = '', '@', '<', '>', '!'                                             ###

def iter_integer_formats(byteorders=byteorders):
    for code in integer_codes:
        for byteorder in byteorders:
            if (byteorder in ('', '@') and code in ('q', 'Q') and
                not HAVE_LONG_LONG):
                continue
            if (byteorder not in ('', '@') and code in ('n', 'N')):
                continue
            yield code, byteorder

# Native 'q' packing isn't available on systems that don't have the C
# long long type.
try:
    struct.pack('q', 5)
except struct.error:
    HAVE_LONG_LONG = False
else:
    HAVE_LONG_LONG = True

def string_reverse(s):
    return bytes(reversed(s))                                                   ### only slices with step=1

def bigendian_to_native(value):
    if ISBIGENDIAN:
        return value
    else:
        return string_reverse(value)

class StructTest(unittest.TestCase):
    def test_consistence(self):

        sz = struct.calcsize('i')
        self.assertEqual(sz * 3, struct.calcsize('iii'))

        fmt = 'bbbbbbbbhhhhiillffd'                                             ###
        fmt3 = '3b3b18b12h6i6l6f3d'                                             ###
        sz = struct.calcsize(fmt)
        sz3 = struct.calcsize(fmt3)
        self.assertEqual(sz * 3, sz3)


    def test_transitiveness(self):
        b = 1
        h = 255
        i = 65535
        l = 65536
        f = 3.1415
        d = 3.1415

        for prefix in ('', '@', '<', '>', '!'):                                 ###
            for format in ('bhilfd', 'BHILfd'):                                 ###
                format = prefix + format
                s = struct.pack(format, b, h, i, l, f, d)                       ###
                bp, hp, ip, lp, fp, dp = struct.unpack(format, s)               ###
                self.assertEqual(bp, b)
                self.assertEqual(hp, h)
                self.assertEqual(ip, i)
                self.assertEqual(lp, l)
                self.assertEqual(int(100 * fp), int(100 * f))
                self.assertEqual(int(100 * dp), int(100 * d))

    def test_new_features(self):
        # Test some of the new features in detail
        # (format, argument, big-endian result, little-endian result, asymmetric)
        tests = [
            ('s', b'a', b'a', b'a', 0),
            ('0s', b'helloworld', b'', b'', 1),
            ('1s', b'helloworld', b'h', b'h', 1),
            ('9s', b'helloworld', b'helloworl', b'helloworl', 1),
            ('10s', b'helloworld', b'helloworld', b'helloworld', 0),
            ('11s', b'helloworld', b'helloworld\0', b'helloworld\0', 1),
            ('20s', b'helloworld', b'helloworld'+10*b'\0', b'helloworld'+10*b'\0', 1),
            ('b', 7, b'\7', b'\7', 0),
            ('b', -7, b'\371', b'\371', 0),
            ('B', 7, b'\7', b'\7', 0),
            ('B', 249, b'\371', b'\371', 0),
            ('h', 700, b'\002\274', b'\274\002', 0),
            ('h', -700, b'\375D', b'D\375', 0),
            ('H', 700, b'\002\274', b'\274\002', 0),
            ('H', 0x10000-700, b'\375D', b'D\375', 0),
            ('i', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('i', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('I', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('I', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('l', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('l', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('L', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('L', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('f', 2.0, b'@\000\000\000', b'\000\000\000@', 0),
            ('d', 2.0, b'@\000\000\000\000\000\000\000',
                       b'\000\000\000\000\000\000\000@', 0),
            ('f', -2.0, b'\300\000\000\000', b'\000\000\000\300', 0),
            ('d', -2.0, b'\300\000\000\000\000\000\000\000',
                        b'\000\000\000\000\000\000\000\300', 0),
        ]

        for fmt, arg, big, lil, asy in tests:
            for (xfmt, exp) in [('>'+fmt, big), ('!'+fmt, big), ('<'+fmt, lil),
                                                                      ]:        ###
                res = struct.pack(xfmt, arg)
                self.assertEqual(res, exp)
                self.assertEqual(struct.calcsize(xfmt), len(res))
                rev = struct.unpack(xfmt, res)[0]
                if rev != arg:
                    self.assertTrue(asy)

    def test_calcsize(self):
        expected_size = {
            'b': 1, 'B': 1,
            'h': 2, 'H': 2,
            'i': 4, 'I': 4,
            'l': 4, 'L': 4,
            'q': 8, 'Q': 8,
            }

        # standard integer sizes
        for code, byteorder in iter_integer_formats(('<', '>', '!')):           ###
            format = byteorder+code
            size = struct.calcsize(format)
            self.assertEqual(size, expected_size[code])

        # native integer sizes
        native_pairs = 'bB', 'hH', 'iI', 'lL'                                   ###
        if HAVE_LONG_LONG:
            native_pairs += 'qQ',
        for format_pair in native_pairs:
            for byteorder in '', '@':
                signed_size = struct.calcsize(byteorder + format_pair[0])
                unsigned_size = struct.calcsize(byteorder + format_pair[1])
                self.assertEqual(signed_size, unsigned_size)

        # bounds for native integer sizes
        self.assertEqual(struct.calcsize('b'), 1)
        self.assertLessEqual(2, struct.calcsize('h'))
        self.assertLessEqual(4, struct.calcsize('l'))
        self.assertLessEqual(struct.calcsize('h'), struct.calcsize('i'))
        self.assertLessEqual(struct.calcsize('i'), struct.calcsize('l'))
        if HAVE_LONG_LONG:
            self.assertLessEqual(8, struct.calcsize('q'))
            self.assertLessEqual(struct.calcsize('l'), struct.calcsize('q'))

    def test_integers(self):
        # Integer tests (bBhHiIlLqQnN).
        runs = 0                                                                ###
        failures = 0                                                            ###

        class IntTester(unittest.TestCase):
            def __init__(self, format):
                super(IntTester, self).__init__(methodName='test_one')
                self.format = format
                self.code = format[-1]
                self.byteorder = format[:-1]
                if not self.byteorder in byteorders:
                    raise ValueError("unrecognized packing byteorder: %s" %
                                     self.byteorder)
                self.bytesize = struct.calcsize(format)
                self.bitsize = self.bytesize * 8
                if self.code in tuple('bhilqn'):
                    self.signed = True
                    self.min_value = -(2**(self.bitsize-1))
                    self.max_value = 2**(self.bitsize-1) - 1
                elif self.code in tuple('BHILQN'):
                    self.signed = False
                    self.min_value = 0
                    self.max_value = 2**self.bitsize - 1
                else:
                    raise ValueError("unrecognized format code: %s" %
                                     self.code)

            def test_one(self, x, pack=struct.pack,
                                  unpack=struct.unpack,
                                  unhexlify=binascii.unhexlify):

                format = self.format
                if self.min_value <= x <= self.max_value:
                    runs += 1                                                   ###
                    expected = x
                    if self.signed and x < 0:
                        expected += 1 << self.bitsize
                    self.assertGreaterEqual(expected, 0)
                    expected = '%x' % expected
                    if len(expected) & 1:
                        expected = "0" + expected
                    expected = expected.encode('ascii')
                    expected = unhexlify(expected)
                    expected = (b"\x00" * (self.bytesize - len(expected)) +
                                expected)
                    if (self.byteorder == '<' or
                        self.byteorder in ('', '@', '=') and not ISBIGENDIAN):
                        expected = string_reverse(expected)
                    self.assertEqual(len(expected), self.bytesize)

                    # Pack work?
                    got = pack(format, x)
                    if got != expected:                                         ###
                        failures += 1                                           ###
                        #print('Failed: pack({!r}, {!r}): got={!r} != expected={!r}'.format(format, x, got, expected))  ###
                        got = expected                                          ###

                    # Unpack work?
                    retrieved = unpack(format, got)[0]
                    self.assertEqual(x, retrieved)


            def run(self):
                from random import randrange

                # Create all interesting powers of 2.
                values = []
                for exp in range(self.bitsize + 3):
                    values.append(1 << exp)

                # Add some random values.
                for i in range(self.bitsize):
                    val = 0
                    for j in range(self.bytesize):
                        val = (val << 8) | randrange(256)
                    values.append(val)

                # Values absorbed from other tests
                values.extend([300, 700000, sys.maxsize*4])

                # Try all those, and their negations, and +-1 from
                # them.  Note that this tests all power-of-2
                # boundaries in range, and a few out of range, plus
                # +-(2**n +- 1).
                for base in values:
                    for val in -base, base:
                        for incr in -1, 0, 1:
                            x = val + incr
                            self.test_one(x)

        for code, byteorder in iter_integer_formats():
            format = byteorder+code
            t = IntTester(format)
            t.run()

        if failures:                                                            ###
            self.fail(msg='Failing subtests: {} of {}'.format(failures, runs))  ###
                                                                                ###
    def test_705836(self):
        # SF bug 705836.  "<f" and ">f" had a severe rounding bug, where a carry
        # from the low-order discarded bits could propagate into the exponent
        # field, causing the result to be wrong by a factor of 2.
        import math

        for base in range(1, 33):
            # smaller <- largest representable float less than base.
            delta = 0.5
            while base - delta / 2.0 != base:
                delta /= 2.0
            smaller = base - delta
            # Packing this rounds away a solid string of trailing 1 bits.
            packed = struct.pack("<f", smaller)
            unpacked = struct.unpack("<f", packed)[0]
            # This failed at base = 2, 4, and 32, with unpacked = 1, 2, and
            # 16, respectively.
            self.assertAlmostEqual(base, unpacked, places=4)                    ###
            bigpacked = struct.pack(">f", smaller)
            self.assertEqual(bigpacked, string_reverse(packed))
            unpacked = struct.unpack(">f", bigpacked)[0]
            self.assertAlmostEqual(base, unpacked, places=4)                    ###

        # Largest finite IEEE single.
        big = (1 << 24) - 1
        big = math.ldexp(big, 127 - 23)
        packed = struct.pack(">f", big)
        unpacked = struct.unpack(">f", packed)[0]
        self.assertEqual(big, unpacked)


    def test_unpack_with_buffer(self):
        # SF bug 1563759: struct.unpack doesn't support buffer protocol objects
        data1 = array.array('B', b'\x12\x34\x56\x78')
        data2 = memoryview(b'\x12\x34\x56\x78') # XXX b'......XXXX......', 6, 4
        for data in [data1, data2]:
            value, = struct.unpack('>I', data)
            self.assertEqual(value, 0x12345678)

    def check_sizeof(self, format_str, number_of_codes):
        # The size of 'PyStructObject'
        totalsize = support.calcobjsize('2n3P')
        # The size taken up by the 'formatcode' dynamic array
        totalsize += struct.calcsize('P3n0P') * (number_of_codes + 1)
        support.check_sizeof(self, struct.Struct(format_str), totalsize)



