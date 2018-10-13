# Python test set -- math module
# XXXX Should not do tests around zero only

import unittest
import math

eps = 1E-04                                                                     ###
NAN = float('nan')
INF = float('inf')
NINF = float('-inf')

class MathTests(unittest.TestCase):

    def ftest(self, name, value, expected):
        if abs(value-expected) > eps:
            # Use %r instead of %f so the error message
            # displays full precision. Otherwise discrepancies
            # in the last few bits will lead to very confusing
            # error messages
            self.fail('%s returned %r, expected %r' %
                      (name, value, expected))

    def testConstants(self):
        self.ftest('pi', math.pi, 3.1415926)
        self.ftest('e', math.e, 2.7182818)

    def testAcos(self):
        self.assertRaises(TypeError, math.acos)
        self.ftest('acos(-1)', math.acos(-1), math.pi)
        self.ftest('acos(0)', math.acos(0), math.pi/2)
        self.ftest('acos(1)', math.acos(1), 0)
        self.assertTrue(math.isnan(math.acos(NAN)))

    def testAsin(self):
        self.assertRaises(TypeError, math.asin)
        self.ftest('asin(-1)', math.asin(-1), -math.pi/2)
        self.ftest('asin(0)', math.asin(0), 0)
        self.ftest('asin(1)', math.asin(1), math.pi/2)
        self.assertTrue(math.isnan(math.asin(NAN)))

    def testAtan(self):
        self.assertRaises(TypeError, math.atan)
        self.ftest('atan(-1)', math.atan(-1), -math.pi/4)
        self.ftest('atan(0)', math.atan(0), 0)
        self.ftest('atan(1)', math.atan(1), math.pi/4)
        self.ftest('atan(inf)', math.atan(INF), math.pi/2)
        self.ftest('atan(-inf)', math.atan(NINF), -math.pi/2)
        self.assertTrue(math.isnan(math.atan(NAN)))

    def testAtan2(self):
        self.assertRaises(TypeError, math.atan2)
        self.ftest('atan2(-1, 0)', math.atan2(-1, 0), -math.pi/2)
        self.ftest('atan2(-1, 1)', math.atan2(-1, 1), -math.pi/4)
        self.ftest('atan2(0, 1)', math.atan2(0, 1), 0)
        self.ftest('atan2(1, 1)', math.atan2(1, 1), math.pi/4)
        self.ftest('atan2(1, 0)', math.atan2(1, 0), math.pi/2)

        # math.atan2(0, x)
        self.ftest('atan2(0., -inf)', math.atan2(0., NINF), math.pi)
        self.ftest('atan2(0., -2.3)', math.atan2(0., -2.3), math.pi)
        self.ftest('atan2(0., -0.)', math.atan2(0., -0.), math.pi)
        self.assertEqual(math.atan2(0., 0.), 0.)
        self.assertEqual(math.atan2(0., 2.3), 0.)
        self.assertEqual(math.atan2(0., INF), 0.)
        self.assertTrue(math.isnan(math.atan2(0., NAN)))
        # math.atan2(-0, x)
        self.ftest('atan2(-0., -inf)', math.atan2(-0., NINF), -math.pi)
        self.ftest('atan2(-0., -2.3)', math.atan2(-0., -2.3), -math.pi)
        self.ftest('atan2(-0., -0.)', math.atan2(-0., -0.), -math.pi)
        self.assertEqual(math.atan2(-0., 0.), -0.)
        self.assertEqual(math.atan2(-0., 2.3), -0.)
        self.assertEqual(math.atan2(-0., INF), -0.)
        self.assertTrue(math.isnan(math.atan2(-0., NAN)))
        # math.atan2(INF, x)
        self.ftest('atan2(inf, -inf)', math.atan2(INF, NINF), math.pi*3/4)
        self.ftest('atan2(inf, -2.3)', math.atan2(INF, -2.3), math.pi/2)
        self.ftest('atan2(inf, -0.)', math.atan2(INF, -0.0), math.pi/2)
        self.ftest('atan2(inf, 0.)', math.atan2(INF, 0.0), math.pi/2)
        self.ftest('atan2(inf, 2.3)', math.atan2(INF, 2.3), math.pi/2)
        self.ftest('atan2(inf, inf)', math.atan2(INF, INF), math.pi/4)
        self.assertTrue(math.isnan(math.atan2(INF, NAN)))
        # math.atan2(NINF, x)
        self.ftest('atan2(-inf, -inf)', math.atan2(NINF, NINF), -math.pi*3/4)
        self.ftest('atan2(-inf, -2.3)', math.atan2(NINF, -2.3), -math.pi/2)
        self.ftest('atan2(-inf, -0.)', math.atan2(NINF, -0.0), -math.pi/2)
        self.ftest('atan2(-inf, 0.)', math.atan2(NINF, 0.0), -math.pi/2)
        self.ftest('atan2(-inf, 2.3)', math.atan2(NINF, 2.3), -math.pi/2)
        self.ftest('atan2(-inf, inf)', math.atan2(NINF, INF), -math.pi/4)
        self.assertTrue(math.isnan(math.atan2(NINF, NAN)))
        # math.atan2(+finite, x)
        self.ftest('atan2(2.3, -inf)', math.atan2(2.3, NINF), math.pi)
        self.ftest('atan2(2.3, -0.)', math.atan2(2.3, -0.), math.pi/2)
        self.ftest('atan2(2.3, 0.)', math.atan2(2.3, 0.), math.pi/2)
        self.assertEqual(math.atan2(2.3, INF), 0.)
        self.assertTrue(math.isnan(math.atan2(2.3, NAN)))
        # math.atan2(-finite, x)
        self.ftest('atan2(-2.3, -inf)', math.atan2(-2.3, NINF), -math.pi)
        self.ftest('atan2(-2.3, -0.)', math.atan2(-2.3, -0.), -math.pi/2)
        self.ftest('atan2(-2.3, 0.)', math.atan2(-2.3, 0.), -math.pi/2)
        self.assertEqual(math.atan2(-2.3, INF), -0.)
        self.assertTrue(math.isnan(math.atan2(-2.3, NAN)))
        # math.atan2(NAN, x)
        self.assertTrue(math.isnan(math.atan2(NAN, NINF)))
        self.assertTrue(math.isnan(math.atan2(NAN, -2.3)))
        self.assertTrue(math.isnan(math.atan2(NAN, -0.)))
        self.assertTrue(math.isnan(math.atan2(NAN, 0.)))
        self.assertTrue(math.isnan(math.atan2(NAN, 2.3)))
        self.assertTrue(math.isnan(math.atan2(NAN, INF)))
        self.assertTrue(math.isnan(math.atan2(NAN, NAN)))

    def testCeil(self):
        self.assertRaises(TypeError, math.ceil)
        self.assertEqual(int, type(math.ceil(0.5)))
        self.ftest('ceil(0.5)', math.ceil(0.5), 1)
        self.ftest('ceil(1.0)', math.ceil(1.0), 1)
        self.ftest('ceil(1.5)', math.ceil(1.5), 2)
        self.ftest('ceil(-0.5)', math.ceil(-0.5), 0)
        self.ftest('ceil(-1.0)', math.ceil(-1.0), -1)
        self.ftest('ceil(-1.5)', math.ceil(-1.5), -1)
        #self.assertEqual(math.ceil(INF), INF)
        #self.assertEqual(math.ceil(NINF), NINF)
        #self.assertTrue(math.isnan(math.ceil(NAN)))

    def testCopysign(self):
        self.assertEqual(math.copysign(1, 42), 1.0)
        self.assertEqual(math.copysign(0., 42), 0.0)
        self.assertEqual(math.copysign(1., -42), -1.0)
        self.assertEqual(math.copysign(3, 0.), 3.0)
        self.assertEqual(math.copysign(4., -0.), -4.0)

        self.assertRaises(TypeError, math.copysign)
        # copysign should let us distinguish signs of zeros
        self.assertEqual(math.copysign(1., 0.), 1.)
        self.assertEqual(math.copysign(1., -0.), -1.)
        self.assertEqual(math.copysign(INF, 0.), INF)
        self.assertEqual(math.copysign(INF, -0.), NINF)
        self.assertEqual(math.copysign(NINF, 0.), INF)
        self.assertEqual(math.copysign(NINF, -0.), NINF)
        # and of infinities
        self.assertEqual(math.copysign(1., INF), 1.)
        self.assertEqual(math.copysign(1., NINF), -1.)
        self.assertEqual(math.copysign(INF, INF), INF)
        self.assertEqual(math.copysign(INF, NINF), NINF)
        self.assertEqual(math.copysign(NINF, INF), INF)
        self.assertEqual(math.copysign(NINF, NINF), NINF)
        self.assertTrue(math.isnan(math.copysign(NAN, 1.)))
        self.assertTrue(math.isnan(math.copysign(NAN, INF)))
        self.assertTrue(math.isnan(math.copysign(NAN, NINF)))
        self.assertTrue(math.isnan(math.copysign(NAN, NAN)))
        # copysign(INF, NAN) may be INF or it may be NINF, since
        # we don't know whether the sign bit of NAN is set on any
        # given platform.
        self.assertTrue(math.isinf(math.copysign(INF, NAN)))
        # similarly, copysign(2., NAN) could be 2. or -2.
        self.assertEqual(abs(math.copysign(2., NAN)), 2.)

    def testCos(self):
        self.assertRaises(TypeError, math.cos)
        self.ftest('cos(-pi/2)', math.cos(-math.pi/2), 0)
        self.ftest('cos(0)', math.cos(0), 1)
        self.ftest('cos(pi/2)', math.cos(math.pi/2), 0)
        self.ftest('cos(pi)', math.cos(math.pi), -1)
        try:
            self.assertTrue(math.isnan(math.cos(INF)))
            self.assertTrue(math.isnan(math.cos(NINF)))
        except ValueError:
            self.assertRaises(ValueError, math.cos, INF)
            self.assertRaises(ValueError, math.cos, NINF)
        self.assertTrue(math.isnan(math.cos(NAN)))

    def testDegrees(self):
        self.assertRaises(TypeError, math.degrees)
        self.ftest('degrees(pi)', math.degrees(math.pi), 180.0)
        self.ftest('degrees(pi/2)', math.degrees(math.pi/2), 90.0)
        self.ftest('degrees(-pi/4)', math.degrees(-math.pi/4), -45.0)

    def testExp(self):
        self.assertRaises(TypeError, math.exp)
        self.ftest('exp(-1)', math.exp(-1), 1/math.e)
        self.ftest('exp(0)', math.exp(0), 1)
        self.ftest('exp(1)', math.exp(1), math.e)
        self.assertEqual(math.exp(INF), INF)
        self.assertEqual(math.exp(NINF), 0.)
        self.assertTrue(math.isnan(math.exp(NAN)))

    def testFabs(self):
        self.assertRaises(TypeError, math.fabs)
        self.ftest('fabs(-1)', math.fabs(-1), 1)
        self.ftest('fabs(0)', math.fabs(0), 0)
        self.ftest('fabs(1)', math.fabs(1), 1)

    def testFloor(self):
        self.assertRaises(TypeError, math.floor)
        self.assertEqual(int, type(math.floor(0.5)))
        self.ftest('floor(0.5)', math.floor(0.5), 0)
        self.ftest('floor(1.0)', math.floor(1.0), 1)
        self.ftest('floor(1.5)', math.floor(1.5), 1)
        self.ftest('floor(-0.5)', math.floor(-0.5), -1)
        self.ftest('floor(-1.0)', math.floor(-1.0), -1)
        self.ftest('floor(-1.5)', math.floor(-1.5), -2)
        # pow() relies on floor() to check for integers
        # This fails on some platforms - so check it here
        self.ftest('floor(1.23e37)', math.floor(1.23e37), 1.23e37)              ###
        self.ftest('floor(-1.23e37)', math.floor(-1.23e37), -1.23e37)           ###
        #self.assertEqual(math.ceil(INF), INF)
        #self.assertEqual(math.ceil(NINF), NINF)
        #self.assertTrue(math.isnan(math.floor(NAN)))

    def testFmod(self):
        self.assertRaises(TypeError, math.fmod)
        self.ftest('fmod(10, 1)', math.fmod(10, 1), 0.0)
        self.ftest('fmod(10, 0.5)', math.fmod(10, 0.5), 0.0)
        self.ftest('fmod(10, 1.5)', math.fmod(10, 1.5), 1.0)
        self.ftest('fmod(-10, 1)', math.fmod(-10, 1), -0.0)
        self.ftest('fmod(-10, 0.5)', math.fmod(-10, 0.5), -0.0)
        self.ftest('fmod(-10, 1.5)', math.fmod(-10, 1.5), -1.0)
        self.assertTrue(math.isnan(math.fmod(NAN, 1.)))
        self.assertTrue(math.isnan(math.fmod(1., NAN)))
        self.assertTrue(math.isnan(math.fmod(NAN, NAN)))
# Returns nan                                                                   ###
        self.assertEqual(math.fmod(3.0, INF), 3.0)
        self.assertEqual(math.fmod(-3.0, INF), -3.0)
        self.assertEqual(math.fmod(3.0, NINF), 3.0)
        self.assertEqual(math.fmod(-3.0, NINF), -3.0)
        self.assertEqual(math.fmod(0.0, 3.0), 0.0)
        self.assertEqual(math.fmod(0.0, NINF), 0.0)

    def testFrexp(self):
        self.assertRaises(TypeError, math.frexp)

        def testfrexp(name, result, expected):
            (mant, exp), (emant, eexp) = result, expected
            if abs(mant-emant) > eps or exp != eexp:
                self.fail('%s returned %r, expected %r'%\
                          (name, result, expected))

        testfrexp('frexp(-1)', math.frexp(-1), (-0.5, 1))
        testfrexp('frexp(0)', math.frexp(0), (0, 0))
        testfrexp('frexp(1)', math.frexp(1), (0.5, 1))
        testfrexp('frexp(2)', math.frexp(2), (0.5, 2))

        self.assertEqual(math.frexp(INF)[0], INF)
        self.assertEqual(math.frexp(NINF)[0], NINF)
        self.assertTrue(math.isnan(math.frexp(NAN)[0]))

    def testLdexp(self):
        self.assertRaises(TypeError, math.ldexp)
        self.ftest('ldexp(0,1)', math.ldexp(0,1), 0)
        self.ftest('ldexp(1,1)', math.ldexp(1,1), 2)
        self.ftest('ldexp(1,-1)', math.ldexp(1,-1), 0.5)
        self.ftest('ldexp(-1,1)', math.ldexp(-1,1), -2)
# Returns inf                                                                   ###
        self.assertEqual(math.ldexp(1., -1000000), 0.)
        self.assertEqual(math.ldexp(-1., -1000000), -0.)
        self.assertEqual(math.ldexp(INF, 30), INF)
        self.assertEqual(math.ldexp(NINF, -213), NINF)
        self.assertTrue(math.isnan(math.ldexp(NAN, 0)))

        # large second argument
        for n in [10**5, 10**10, 10**20, 10**40]:
            self.assertEqual(math.ldexp(INF, -n), INF)
            self.assertEqual(math.ldexp(NINF, -n), NINF)
            self.assertEqual(math.ldexp(1., -n), 0.)
            self.assertEqual(math.ldexp(-1., -n), -0.)
            self.assertEqual(math.ldexp(0., -n), 0.)
            self.assertEqual(math.ldexp(-0., -n), -0.)
            self.assertTrue(math.isnan(math.ldexp(NAN, -n)))

            self.assertEqual(math.ldexp(0., n), 0.)
            self.assertEqual(math.ldexp(-0., n), -0.)
            self.assertEqual(math.ldexp(INF, n), INF)
            self.assertEqual(math.ldexp(NINF, n), NINF)
            self.assertTrue(math.isnan(math.ldexp(NAN, n)))

    def testLog(self):
        self.assertRaises(TypeError, math.log)
        self.ftest('log(1/e)', math.log(1/math.e), -1)
        self.ftest('log(1)', math.log(1), 0)
        self.ftest('log(e)', math.log(math.e), 1)
        self.ftest('log(32,2)', math.log(32,2), 5)
        self.ftest('log(10**30, 10)', math.log(10**30, 10), 30)                 ###
        self.ftest('log(10**20, 10**10)', math.log(10**20, 10**10), 2)          ###
        self.assertRaises(ValueError, math.log, -1.5)
        self.assertRaises(ValueError, math.log, -10**1000)
        self.assertRaises(ValueError, math.log, NINF)
        self.assertEqual(math.log(INF), INF)
        self.assertTrue(math.isnan(math.log(NAN)))

    def testModf(self):
        self.assertRaises(TypeError, math.modf)

        def testmodf(name, result, expected):
            (v1, v2), (e1, e2) = result, expected
            if abs(v1-e1) > eps or abs(v2-e2):
                self.fail('%s returned %r, expected %r'%\
                          (name, result, expected))

        testmodf('modf(1.5)', math.modf(1.5), (0.5, 1.0))
        testmodf('modf(-1.5)', math.modf(-1.5), (-0.5, -1.0))

        self.assertEqual(math.modf(INF), (0.0, INF))
        self.assertEqual(math.modf(NINF), (-0.0, NINF))

        modf_nan = math.modf(NAN)
        self.assertTrue(math.isnan(modf_nan[1]))

    def testPow(self):
        self.assertRaises(TypeError, math.pow)
        self.ftest('pow(0,1)', math.pow(0,1), 0)
        self.ftest('pow(1,0)', math.pow(1,0), 1)
        self.ftest('pow(2,1)', math.pow(2,1), 2)
        self.ftest('pow(2,-1)', math.pow(2,-1), 0.5)
        self.assertEqual(math.pow(INF, 1), INF)
        self.assertEqual(math.pow(NINF, 1), NINF)
        self.assertEqual((math.pow(1, INF)), 1.)
        self.assertEqual((math.pow(1, NINF)), 1.)
        self.assertTrue(math.isnan(math.pow(NAN, 1)))
        self.assertTrue(math.isnan(math.pow(2, NAN)))
        self.assertTrue(math.isnan(math.pow(0, NAN)))
        self.assertEqual(math.pow(1, NAN), 1)

        # pow(0., x)
        self.assertEqual(math.pow(0., INF), 0.)
        self.assertEqual(math.pow(0., 3.), 0.)
        self.assertEqual(math.pow(0., 2.3), 0.)
        self.assertEqual(math.pow(0., 2.), 0.)
        self.assertEqual(math.pow(0., 0.), 1.)
        self.assertEqual(math.pow(0., -0.), 1.)
        self.assertTrue(math.isnan(math.pow(0., NAN)))

        # pow(INF, x)
        self.assertEqual(math.pow(INF, INF), INF)
        self.assertEqual(math.pow(INF, 3.), INF)
        self.assertEqual(math.pow(INF, 2.3), INF)
        self.assertEqual(math.pow(INF, 2.), INF)
        self.assertEqual(math.pow(INF, 0.), 1.)
        self.assertEqual(math.pow(INF, -0.), 1.)
        self.assertEqual(math.pow(INF, -2.), 0.)
        self.assertEqual(math.pow(INF, -2.3), 0.)
        self.assertEqual(math.pow(INF, -3.), 0.)
        self.assertEqual(math.pow(INF, NINF), 0.)
        self.assertTrue(math.isnan(math.pow(INF, NAN)))

        # pow(-0., x)
        self.assertEqual(math.pow(-0., INF), 0.)
        self.assertEqual(math.pow(-0., 3.), -0.)
        self.assertEqual(math.pow(-0., 2.3), 0.)
        self.assertEqual(math.pow(-0., 2.), 0.)
        self.assertEqual(math.pow(-0., 0.), 1.)
        self.assertEqual(math.pow(-0., -0.), 1.)
        self.assertTrue(math.isnan(math.pow(-0., NAN)))

        # pow(NINF, x)
        self.assertEqual(math.pow(NINF, INF), INF)
        self.assertEqual(math.pow(NINF, 3.), NINF)
        self.assertEqual(math.pow(NINF, 2.3), INF)
        self.assertEqual(math.pow(NINF, 2.), INF)
        self.assertEqual(math.pow(NINF, 0.), 1.)
        self.assertEqual(math.pow(NINF, -0.), 1.)
        self.assertEqual(math.pow(NINF, -2.), 0.)
        self.assertEqual(math.pow(NINF, -2.3), 0.)
        self.assertEqual(math.pow(NINF, -3.), -0.)
        self.assertEqual(math.pow(NINF, NINF), 0.)
        self.assertTrue(math.isnan(math.pow(NINF, NAN)))

        # pow(-1, x)
        self.assertEqual(math.pow(-1., INF), 1.)
        self.assertEqual(math.pow(-1., 3.), -1.)
        self.assertEqual(math.pow(-1., 2.), 1.)
        self.assertEqual(math.pow(-1., 0.), 1.)
        self.assertEqual(math.pow(-1., -0.), 1.)
        self.assertEqual(math.pow(-1., -2.), 1.)
        self.assertEqual(math.pow(-1., -3.), -1.)
        self.assertEqual(math.pow(-1., NINF), 1.)
        self.assertTrue(math.isnan(math.pow(-1., NAN)))

        # pow(1, x)
        self.assertEqual(math.pow(1., INF), 1.)
        self.assertEqual(math.pow(1., 3.), 1.)
        self.assertEqual(math.pow(1., 2.3), 1.)
        self.assertEqual(math.pow(1., 2.), 1.)
        self.assertEqual(math.pow(1., 0.), 1.)
        self.assertEqual(math.pow(1., -0.), 1.)
        self.assertEqual(math.pow(1., -2.), 1.)
        self.assertEqual(math.pow(1., -2.3), 1.)
        self.assertEqual(math.pow(1., -3.), 1.)
        self.assertEqual(math.pow(1., NINF), 1.)
        self.assertEqual(math.pow(1., NAN), 1.)

        # pow(x, 0) should be 1 for any x
        self.assertEqual(math.pow(2.3, 0.), 1.)
        self.assertEqual(math.pow(-2.3, 0.), 1.)
        self.assertEqual(math.pow(NAN, 0.), 1.)
        self.assertEqual(math.pow(2.3, -0.), 1.)
        self.assertEqual(math.pow(-2.3, -0.), 1.)
        self.assertEqual(math.pow(NAN, -0.), 1.)

        # pow(x, NINF)
        self.assertEqual(math.pow(1.9, NINF), 0.)
        self.assertEqual(math.pow(1.1, NINF), 0.)
        self.assertEqual(math.pow(0.9, NINF), INF)
        self.assertEqual(math.pow(0.1, NINF), INF)
        self.assertEqual(math.pow(-0.1, NINF), INF)
        self.assertEqual(math.pow(-0.9, NINF), INF)
        self.assertEqual(math.pow(-1.1, NINF), 0.)
        self.assertEqual(math.pow(-1.9, NINF), 0.)

        # pow(x, INF)
        self.assertEqual(math.pow(1.9, INF), INF)
        self.assertEqual(math.pow(1.1, INF), INF)
        self.assertEqual(math.pow(0.9, INF), 0.)
        self.assertEqual(math.pow(0.1, INF), 0.)
        self.assertEqual(math.pow(-0.1, INF), 0.)
        self.assertEqual(math.pow(-0.9, INF), 0.)
        self.assertEqual(math.pow(-1.1, INF), INF)
        self.assertEqual(math.pow(-1.9, INF), INF)

        # pow(x, y) should work for x negative, y an integer
        self.ftest('(-2.)**3.', math.pow(-2.0, 3.0), -8.0)
        self.ftest('(-2.)**2.', math.pow(-2.0, 2.0), 4.0)
        self.ftest('(-2.)**1.', math.pow(-2.0, 1.0), -2.0)
        self.ftest('(-2.)**0.', math.pow(-2.0, 0.0), 1.0)
        self.ftest('(-2.)**-0.', math.pow(-2.0, -0.0), 1.0)
        self.ftest('(-2.)**-1.', math.pow(-2.0, -1.0), -0.5)
        self.ftest('(-2.)**-2.', math.pow(-2.0, -2.0), 0.25)
        self.ftest('(-2.)**-3.', math.pow(-2.0, -3.0), -0.125)

        # the following tests have been commented out since they don't
        # really belong here:  the implementation of ** for floats is
        # independent of the implementation of math.pow
        #self.assertEqual(1**NAN, 1)
        #self.assertEqual(1**INF, 1)
        #self.assertEqual(1**NINF, 1)
        #self.assertEqual(1**0, 1)
        #self.assertEqual(1.**NAN, 1)
        #self.assertEqual(1.**INF, 1)
        #self.assertEqual(1.**NINF, 1)
        #self.assertEqual(1.**0, 1)

    def testRadians(self):
        self.assertRaises(TypeError, math.radians)
        self.ftest('radians(180)', math.radians(180), math.pi)
        self.ftest('radians(90)', math.radians(90), math.pi/2)
        self.ftest('radians(-45)', math.radians(-45), -math.pi/4)

    def testSin(self):
        self.assertRaises(TypeError, math.sin)
        self.ftest('sin(0)', math.sin(0), 0)
        self.ftest('sin(pi/2)', math.sin(math.pi/2), 1)
        self.ftest('sin(-pi/2)', math.sin(-math.pi/2), -1)
        try:
            self.assertTrue(math.isnan(math.sin(INF)))
            self.assertTrue(math.isnan(math.sin(NINF)))
        except ValueError:
            self.assertRaises(ValueError, math.sin, INF)
            self.assertRaises(ValueError, math.sin, NINF)
        self.assertTrue(math.isnan(math.sin(NAN)))

    def testSqrt(self):
        self.assertRaises(TypeError, math.sqrt)
        self.ftest('sqrt(0)', math.sqrt(0), 0)
        self.ftest('sqrt(1)', math.sqrt(1), 1)
        self.ftest('sqrt(4)', math.sqrt(4), 2)
        self.assertEqual(math.sqrt(INF), INF)
        self.assertRaises(ValueError, math.sqrt, NINF)
        self.assertTrue(math.isnan(math.sqrt(NAN)))

    def testTan(self):
        self.assertRaises(TypeError, math.tan)
        self.ftest('tan(0)', math.tan(0), 0)
        self.ftest('tan(pi/4)', math.tan(math.pi/4), 1)
        self.ftest('tan(-pi/4)', math.tan(-math.pi/4), -1)
        try:
            self.assertTrue(math.isnan(math.tan(INF)))
            self.assertTrue(math.isnan(math.tan(NINF)))
        except:
            self.assertRaises(ValueError, math.tan, INF)
            self.assertRaises(ValueError, math.tan, NINF)
        self.assertTrue(math.isnan(math.tan(NAN)))

    def test_trunc(self):
        self.assertEqual(math.trunc(1), 1)
        self.assertEqual(math.trunc(-1), -1)
        self.assertEqual(type(math.trunc(1)), int)
        self.assertEqual(type(math.trunc(1.5)), int)
        self.assertEqual(math.trunc(1.5), 1)
        self.assertEqual(math.trunc(-1.5), -1)
        self.assertEqual(math.trunc(1.999999), 1)
        self.assertEqual(math.trunc(-1.999999), -1)
        self.assertEqual(math.trunc(-0.999999), -0)
        self.assertEqual(math.trunc(-100.999), -100)

        self.assertRaises(TypeError, math.trunc)
        self.assertRaises(TypeError, math.trunc, 1, 2)

    def testIsfinite(self):
        self.assertTrue(math.isfinite(0.0))
        self.assertTrue(math.isfinite(-0.0))
        self.assertTrue(math.isfinite(1.0))
        self.assertTrue(math.isfinite(-1.0))
        self.assertFalse(math.isfinite(float("nan")))
        self.assertFalse(math.isfinite(float("inf")))
        self.assertFalse(math.isfinite(float("-inf")))

    def testIsnan(self):
        self.assertTrue(math.isnan(float("nan")))
        self.assertTrue(math.isnan(float("inf")* 0.))
        self.assertFalse(math.isnan(float("inf")))
        self.assertFalse(math.isnan(0.))
        self.assertFalse(math.isnan(1.))

    def testIsinf(self):
        self.assertTrue(math.isinf(float("inf")))
        self.assertTrue(math.isinf(float("-inf")))
        self.assertTrue(math.isinf(1E400))
        self.assertTrue(math.isinf(-1E400))
        self.assertFalse(math.isinf(float("nan")))
        self.assertFalse(math.isinf(0.))
        self.assertFalse(math.isinf(1.))

