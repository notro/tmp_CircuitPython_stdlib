import test.support, unittest

class PowTest(unittest.TestCase):

    def powtest(self, type):
        if type != float:
            for i in range(-1000, 1000):
                self.assertEqual(pow(type(i), 0), 1)
                self.assertEqual(pow(type(i), 1), type(i))
                self.assertEqual(pow(type(0), 1), type(0))
                self.assertEqual(pow(type(1), 1), type(1))

            for i in range(-100, 100):
                self.assertEqual(pow(type(i), 3), i*i*i)

            pow2 = 1
            for i in range(0, 31):
                self.assertEqual(pow(2, i), pow2)
                if i != 30 : pow2 = pow2*2

            for othertype in (int,):
                for i in list(range(-10, 0)) + list(range(1, 10)):
                    ii = type(i)
                    for j in range(1, 11):
                        jj = -othertype(j)
                        pow(ii, jj)

        for othertype in int, float:
            for i in range(1, 100):
                zero = type(0)
                exp = -othertype(i/10.0)
                if exp == 0:
                    continue
                self.assertRaises(ZeroDivisionError, pow, zero, exp)

    def test_powint(self):
        self.powtest(int)

    def test_powlong(self):
        self.powtest(int)

    def test_powfloat(self):
        self.powtest(float)

    def test_bug643260(self):
        class TestRpow:
            def __rpow__(self, other):
                return None
        None ** TestRpow() # Won't fail when __rpow__ invoked.  SF bug #643260.

    def test_bug705231(self):
        # -1.0 raised to an integer should never blow up.  It did if the
        # platform pow() was buggy, and Python didn't worm around it.
        eq = self.assertEqual
        a = -1.0
        # The next two tests can still fail if the platform floor()
        # function doesn't treat all large inputs as integers
        # test_math should also fail if that is happening
        eq(pow(a, 1.23e167), 1.0)
        eq(pow(a, -1.23e167), 1.0)
        for b in range(-10, 11):
            eq(pow(a, float(b)), b & 1 and -1.0 or 1.0)
        for n in range(0, 50):                                                  ###
            fiveto = float(5 ** n)
            # For small n, fiveto will be odd.  Eventually we run out of
            # mantissa bits, though, and thereafer fiveto will be even.
            expected = fiveto % 2.0 and -1.0 or 1.0
            eq(pow(a, fiveto), expected)
            eq(pow(a, -fiveto), expected)
        eq(expected, 1.0)   # else we didn't push fiveto to evenness

