import unittest

import datetime as datetime_module
from datetime import MINYEAR, MAXYEAR
from datetime import timedelta
from datetime import tzinfo
from datetime import time
from datetime import timezone
from datetime import date, datetime

OTHERSTUFF = (10, 34.5, "abc", {}, [], ())

#class FixedOffset(tzinfo):
#
#    def __init__(self, offset, name, dstoffset=42):
#        if isinstance(offset, int):
#            offset = timedelta(minutes=offset)
#        if isinstance(dstoffset, int):
#            dstoffset = timedelta(minutes=dstoffset)
#        self.__offset = offset
#        self.__name = name
#        self.__dstoffset = dstoffset
#    def __repr__(self):
#        return self.__name.lower()
#    def utcoffset(self, dt):
#        return self.__offset
#    def tzname(self, dt):
#        return self.__name
#    def dst(self, dt):
#        return self.__dstoffset


class HarmlessMixedComparison:
    # Test that __eq__ and __ne__ don't complain for mixed-type comparisons.

    # Subclasses must define 'theclass', and theclass(1, 1, 1) must be a
    # legit constructor.

    def test_harmless_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertFalse(me == ())
        self.assertTrue(me != ())
        self.assertFalse(() == me)
        self.assertTrue(() != me)

        self.assertIn(me, [1, 20, [], me])
        self.assertIn([], [me, 1, 20, []])

    def test_harmful_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertRaises(TypeError, lambda: me < ())
        self.assertRaises(TypeError, lambda: me <= ())
        self.assertRaises(TypeError, lambda: me > ())
        self.assertRaises(TypeError, lambda: me >= ())

        self.assertRaises(TypeError, lambda: () < me)
        self.assertRaises(TypeError, lambda: () <= me)
        self.assertRaises(TypeError, lambda: () > me)
        self.assertRaises(TypeError, lambda: () >= me)


# This line delimiter marks the code that was cut out from test_datetime4.py
# ----------------------------------------------------------------------------------------------------------------------
class SubclassTime(time):
    sub_var = 1

class TestTime(HarmlessMixedComparison, unittest.TestCase):

    theclass = time

    def test_basic_attributes(self):
        t = self.theclass(12, 0)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        t = self.theclass(12, 59, 59, 8000)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 59)
        self.assertEqual(t.second, 59)
        self.assertEqual(t.microsecond, 8000)

    def test_roundtrip(self):
        t = self.theclass(1, 2, 3, 4)

        # Verify t -> string -> time identity.
        s = repr(t)
        self.assertTrue(s.startswith('datetime.'))
        s = s[9:]
        t2 = eval(s)
        self.assertEqual(t, t2)

        # Verify identity via reconstructing from pieces.
        t2 = self.theclass(t.hour, t.minute, t.second,
                           t.microsecond)
        self.assertEqual(t, t2)

    def test_comparing(self):
        args = [1, 2, 3, 4]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        self.assertFalse(t1 != t2)
        self.assertFalse(t1 < t2)
        self.assertFalse(t1 > t2)

        for i in range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)   # this is larger than t1
            self.assertTrue(t1 < t2)
            self.assertTrue(t2 > t1)
            self.assertTrue(t1 <= t2)
            self.assertTrue(t2 >= t1)
            self.assertTrue(t1 != t2)
            self.assertTrue(t2 != t1)
            self.assertFalse(t1 == t2)
            self.assertFalse(t2 == t1)
            self.assertFalse(t1 > t2)
            self.assertFalse(t2 < t1)
            self.assertFalse(t1 >= t2)
            self.assertFalse(t2 <= t1)

        for badarg in OTHERSTUFF:
            self.assertEqual(t1 == badarg, False)
            self.assertEqual(t1 != badarg, True)
            self.assertEqual(badarg == t1, False)
            self.assertEqual(badarg != t1, True)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_bad_constructor_arguments(self):
        # bad hours
        self.theclass(0, 0)    # no exception
        self.theclass(23, 0)   # no exception
        self.assertRaises(ValueError, self.theclass, -1, 0)
        self.assertRaises(ValueError, self.theclass, 24, 0)
        # bad minutes
        self.theclass(23, 0)    # no exception
        self.theclass(23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, -1)
        self.assertRaises(ValueError, self.theclass, 23, 60)
        # bad seconds
        self.theclass(23, 59, 0)    # no exception
        self.theclass(23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 60)
        # bad microseconds
        self.theclass(23, 59, 59, 0)        # no exception
        self.theclass(23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, 1000000)

    def test_hash_equality(self):
        d = self.theclass(23, 30, 17)
        e = self.theclass(23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(0,  5, 17)
        e = self.theclass(0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_isoformat(self):
        t = self.theclass(4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "04:05:01.000123")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass()
        self.assertEqual(t.isoformat(), "00:00:00")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1)
        self.assertEqual(t.isoformat(), "00:00:00.000001")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10)
        self.assertEqual(t.isoformat(), "00:00:00.000010")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100)
        self.assertEqual(t.isoformat(), "00:00:00.000100")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1000)
        self.assertEqual(t.isoformat(), "00:00:00.001000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10000)
        self.assertEqual(t.isoformat(), "00:00:00.010000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100000)
        self.assertEqual(t.isoformat(), "00:00:00.100000")
        self.assertEqual(t.isoformat(), str(t))

    def test_1653736(self):
        # verify it doesn't accept extra keyword arguments
        t = self.theclass(second=1)
        self.assertRaises(TypeError, t.isoformat, foo=3)

    def test_strftime(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.strftime('%H %M %S %f'), "01 02 03 000004")
        # A naive object replaces %z and %Z with empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

    def test_format(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.__format__(''), str(t))

        # check that a derived class's __str__() gets called
        class A(self.theclass):
            def __str__(self):
                return 'A'
        a = A(1, 2, 3, 4)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        class B(self.theclass):
            def strftime(self, format_spec):
                return 'B'
        b = B(1, 2, 3, 4)
        self.assertEqual(b.__format__(''), str(t))

        for fmt in ['%H %M %S',
                    ]:
            self.assertEqual(t.__format__(fmt), t.strftime(fmt))
            self.assertEqual(a.__format__(fmt), t.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    def test_str(self):
        self.assertEqual(str(self.theclass(1, 2, 3, 4)), "01:02:03.000004")
        self.assertEqual(str(self.theclass(10, 2, 3, 4000)), "10:02:03.004000")
        self.assertEqual(str(self.theclass(0, 2, 3, 400000)), "00:02:03.400000")
        self.assertEqual(str(self.theclass(12, 2, 3, 0)), "12:02:03")
        self.assertEqual(str(self.theclass(23, 15, 0, 0)), "23:15:00")

    def test_repr(self):
        name = 'datetime.' + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1, 2, 3, 4)),
                         "%s(1, 2, 3, 4)" % name)
        self.assertEqual(repr(self.theclass(10, 2, 3, 4000)),
                         "%s(10, 2, 3, 4000)" % name)
        self.assertEqual(repr(self.theclass(0, 2, 3, 400000)),
                         "%s(0, 2, 3, 400000)" % name)
        self.assertEqual(repr(self.theclass(12, 2, 3, 0)),
                         "%s(12, 2, 3)" % name)
        self.assertEqual(repr(self.theclass(23, 15, 0, 0)),
                         "%s(23, 15)" % name)

    def test_resolution_info(self):
        self.assertIsInstance(self.theclass.min, self.theclass)
        self.assertIsInstance(self.theclass.max, self.theclass)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertTrue(self.theclass.max > self.theclass.min)

#    def test_pickling(self):
#        args = 20, 59, 16, 64**2
#        orig = self.theclass(*args)
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#
#    def test_pickling_subclass_time(self):
#        args = 20, 59, 16, 64**2
#        orig = SubclassTime(*args)
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#
    def test_bool(self):
        cls = self.theclass
        self.assertTrue(cls(1))
        self.assertTrue(cls(0, 1))
        self.assertTrue(cls(0, 0, 1))
        self.assertTrue(cls(0, 0, 0, 1))
        self.assertFalse(cls(0))
        self.assertFalse(cls())

    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        for name, newval in (("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    def test_subclass_time(self):

        class C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                return result

            def newmeth(self, start):
                return start + self.hour + self.second

        args = 4, 5, 6

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.isoformat(), dt2.isoformat())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)

    def test_backdoor_resistance(self):
        # see TestDate.test_backdoor_resistance().
        base = '2:59.0'
        for hour_byte in ' ', '9', chr(24), '\xff':
            self.assertRaises(TypeError, self.theclass,
                                         hour_byte + base[1:])

## A mixin for classes with a tzinfo= argument.  Subclasses must define
## theclass as a class atribute, and theclass(1, 1, 1, tzinfo=whatever)
## must be legit (which is true for time and datetime).
#class TZInfoBase:
#
#    def test_argument_passing(self):
#        cls = self.theclass
#        # A datetime passes itself on, a time passes None.
#        class introspective(tzinfo):
#            def tzname(self, dt):    return dt and "real" or "none"
#            def utcoffset(self, dt):
#                return timedelta(minutes = dt and 42 or -42)
#            dst = utcoffset
#
#        obj = cls(1, 2, 3, tzinfo=introspective())
#
#        expected = cls is time and "none" or "real"
#        self.assertEqual(obj.tzname(), expected)
#
#        expected = timedelta(minutes=(cls is time and -42 or 42))
#        self.assertEqual(obj.utcoffset(), expected)
#        self.assertEqual(obj.dst(), expected)
#
#    def test_bad_tzinfo_classes(self):
#        cls = self.theclass
#        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=12)
#
#        class NiceTry(object):
#            def __init__(self): pass
#            def utcoffset(self, dt): pass
#        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=NiceTry)
#
#        class BetterTry(tzinfo):
#            def __init__(self): pass
#            def utcoffset(self, dt): pass
#        b = BetterTry()
#        t = cls(1, 1, 1, tzinfo=b)
#        self.assertIs(t.tzinfo, b)
#
#    def test_utc_offset_out_of_bounds(self):
#        class Edgy(tzinfo):
#            def __init__(self, offset):
#                self.offset = timedelta(minutes=offset)
#            def utcoffset(self, dt):
#                return self.offset
#
#        cls = self.theclass
#        for offset, legit in ((-1440, False),
#                              (-1439, True),
#                              (1439, True),
#                              (1440, False)):
#            if cls is time:
#                t = cls(1, 2, 3, tzinfo=Edgy(offset))
#            elif cls is datetime:
#                t = cls(6, 6, 6, 1, 2, 3, tzinfo=Edgy(offset))
#            else:
#                assert 0, "impossible"
#            if legit:
#                aofs = abs(offset)
#                h, m = divmod(aofs, 60)
#                tag = "%c%02d:%02d" % (offset < 0 and '-' or '+', h, m)
#                if isinstance(t, datetime):
#                    t = t.timetz()
#                self.assertEqual(str(t), "01:02:03" + tag)
#            else:
#                self.assertRaises(ValueError, str, t)
#
#    def test_tzinfo_classes(self):
#        cls = self.theclass
#        class C1(tzinfo):
#            def utcoffset(self, dt): return None
#            def dst(self, dt): return None
#            def tzname(self, dt): return None
#        for t in (cls(1, 1, 1),
#                  cls(1, 1, 1, tzinfo=None),
#                  cls(1, 1, 1, tzinfo=C1())):
#            self.assertIsNone(t.utcoffset())
#            self.assertIsNone(t.dst())
#            self.assertIsNone(t.tzname())
#
#        class C3(tzinfo):
#            def utcoffset(self, dt): return timedelta(minutes=-1439)
#            def dst(self, dt): return timedelta(minutes=1439)
#            def tzname(self, dt): return "aname"
#        t = cls(1, 1, 1, tzinfo=C3())
#        self.assertEqual(t.utcoffset(), timedelta(minutes=-1439))
#        self.assertEqual(t.dst(), timedelta(minutes=1439))
#        self.assertEqual(t.tzname(), "aname")
#
#        # Wrong types.
#        class C4(tzinfo):
#            def utcoffset(self, dt): return "aname"
#            def dst(self, dt): return 7
#            def tzname(self, dt): return 0
#        t = cls(1, 1, 1, tzinfo=C4())
#        self.assertRaises(TypeError, t.utcoffset)
#        self.assertRaises(TypeError, t.dst)
#        self.assertRaises(TypeError, t.tzname)
#
#        # Offset out of range.
#        class C6(tzinfo):
#            def utcoffset(self, dt): return timedelta(hours=-24)
#            def dst(self, dt): return timedelta(hours=24)
#        t = cls(1, 1, 1, tzinfo=C6())
#        self.assertRaises(ValueError, t.utcoffset)
#        self.assertRaises(ValueError, t.dst)
#
#        # Not a whole number of minutes.
#        class C7(tzinfo):
#            def utcoffset(self, dt): return timedelta(seconds=61)
#            def dst(self, dt): return timedelta(microseconds=-81)
#        t = cls(1, 1, 1, tzinfo=C7())
#        self.assertRaises(ValueError, t.utcoffset)
#        self.assertRaises(ValueError, t.dst)
#
#    def test_aware_compare(self):
#        cls = self.theclass
#
#        # Ensure that utcoffset() gets ignored if the comparands have
#        # the same tzinfo member.
#        class OperandDependentOffset(tzinfo):
#            def utcoffset(self, t):
#                if t.minute < 10:
#                    # d0 and d1 equal after adjustment
#                    return timedelta(minutes=t.minute)
#                else:
#                    # d2 off in the weeds
#                    return timedelta(minutes=59)
#
#        base = cls(8, 9, 10, tzinfo=OperandDependentOffset())
#        d0 = base.replace(minute=3)
#        d1 = base.replace(minute=9)
#        d2 = base.replace(minute=11)
#        for x in d0, d1, d2:
#            for y in d0, d1, d2:
#                for op in lt, le, gt, ge, eq, ne:
#                    got = op(x, y)
#                    expected = op(x.minute, y.minute)
#                    self.assertEqual(got, expected)
#
#        # However, if they're different members, uctoffset is not ignored.
#        # Note that a time can't actually have an operand-depedent offset,
#        # though (and time.utcoffset() passes None to tzinfo.utcoffset()),
#        # so skip this test for time.
#        if cls is not time:
#            d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
#            d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
#            d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
#            for x in d0, d1, d2:
#                for y in d0, d1, d2:
#                    got = (x > y) - (x < y)
#                    if (x is d0 or x is d1) and (y is d0 or y is d1):
#                        expected = 0
#                    elif x is y is d2:
#                        expected = 0
#                    elif x is d2:
#                        expected = -1
#                    else:
#                        assert y is d2
#                        expected = 1
#                    self.assertEqual(got, expected)
#
#
## Testing time objects with a non-None tzinfo.
#class TestTimeTZ(TestTime, TZInfoBase, unittest.TestCase):
#    theclass = time
#
#    def test_empty(self):
#        t = self.theclass()
#        self.assertEqual(t.hour, 0)
#        self.assertEqual(t.minute, 0)
#        self.assertEqual(t.second, 0)
#        self.assertEqual(t.microsecond, 0)
#        self.assertIsNone(t.tzinfo)
#
#    def test_zones(self):
#        est = FixedOffset(-300, "EST", 1)
#        utc = FixedOffset(0, "UTC", -2)
#        met = FixedOffset(60, "MET", 3)
#        t1 = time( 7, 47, tzinfo=est)
#        t2 = time(12, 47, tzinfo=utc)
#        t3 = time(13, 47, tzinfo=met)
#        t4 = time(microsecond=40)
#        t5 = time(microsecond=40, tzinfo=utc)
#
#        self.assertEqual(t1.tzinfo, est)
#        self.assertEqual(t2.tzinfo, utc)
#        self.assertEqual(t3.tzinfo, met)
#        self.assertIsNone(t4.tzinfo)
#        self.assertEqual(t5.tzinfo, utc)
#
#        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
#        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
#        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
#        self.assertIsNone(t4.utcoffset())
#        self.assertRaises(TypeError, t1.utcoffset, "no args")
#
#        self.assertEqual(t1.tzname(), "EST")
#        self.assertEqual(t2.tzname(), "UTC")
#        self.assertEqual(t3.tzname(), "MET")
#        self.assertIsNone(t4.tzname())
#        self.assertRaises(TypeError, t1.tzname, "no args")
#
#        self.assertEqual(t1.dst(), timedelta(minutes=1))
#        self.assertEqual(t2.dst(), timedelta(minutes=-2))
#        self.assertEqual(t3.dst(), timedelta(minutes=3))
#        self.assertIsNone(t4.dst())
#        self.assertRaises(TypeError, t1.dst, "no args")
#
#        self.assertEqual(hash(t1), hash(t2))
#        self.assertEqual(hash(t1), hash(t3))
#        self.assertEqual(hash(t2), hash(t3))
#
#        self.assertEqual(t1, t2)
#        self.assertEqual(t1, t3)
#        self.assertEqual(t2, t3)
#        self.assertNotEqual(t4, t5) # mixed tz-aware & naive
#        self.assertRaises(TypeError, lambda: t4 < t5) # mixed tz-aware & naive
#        self.assertRaises(TypeError, lambda: t5 < t4) # mixed tz-aware & naive
#
#        self.assertEqual(str(t1), "07:47:00-05:00")
#        self.assertEqual(str(t2), "12:47:00+00:00")
#        self.assertEqual(str(t3), "13:47:00+01:00")
#        self.assertEqual(str(t4), "00:00:00.000040")
#        self.assertEqual(str(t5), "00:00:00.000040+00:00")
#
#        self.assertEqual(t1.isoformat(), "07:47:00-05:00")
#        self.assertEqual(t2.isoformat(), "12:47:00+00:00")
#        self.assertEqual(t3.isoformat(), "13:47:00+01:00")
#        self.assertEqual(t4.isoformat(), "00:00:00.000040")
#        self.assertEqual(t5.isoformat(), "00:00:00.000040+00:00")
#
#        d = 'datetime.time'
#        self.assertEqual(repr(t1), d + "(7, 47, tzinfo=est)")
#        self.assertEqual(repr(t2), d + "(12, 47, tzinfo=utc)")
#        self.assertEqual(repr(t3), d + "(13, 47, tzinfo=met)")
#        self.assertEqual(repr(t4), d + "(0, 0, 0, 40)")
#        self.assertEqual(repr(t5), d + "(0, 0, 0, 40, tzinfo=utc)")
#
#        self.assertEqual(t1.strftime("%H:%M:%S %%Z=%Z %%z=%z"),
#                                     "07:47:00 %Z=EST %z=-0500")
#        self.assertEqual(t2.strftime("%H:%M:%S %Z %z"), "12:47:00 UTC +0000")
#        self.assertEqual(t3.strftime("%H:%M:%S %Z %z"), "13:47:00 MET +0100")
#
#        yuck = FixedOffset(-1439, "%z %Z %%z%%Z")
#        t1 = time(23, 59, tzinfo=yuck)
#        self.assertEqual(t1.strftime("%H:%M %%Z='%Z' %%z='%z'"),
#                                     "23:59 %Z='%z %Z %%z%%Z' %z='-2359'")
#
#        # Check that an invalid tzname result raises an exception.
#        class Badtzname(tzinfo):
#            tz = 42
#            def tzname(self, dt): return self.tz
#        t = time(2, 3, 4, tzinfo=Badtzname())
#        self.assertEqual(t.strftime("%H:%M:%S"), "02:03:04")
#        self.assertRaises(TypeError, t.strftime, "%Z")
#
#        # Issue #6697:
#        if '_Fast' in str(type(self)):
#            Badtzname.tz = '\ud800'
#            self.assertRaises(ValueError, t.strftime, "%Z")
#
#    def test_hash_edge_cases(self):
#        # Offsets that overflow a basic time.
#        t1 = self.theclass(0, 1, 2, 3, tzinfo=FixedOffset(1439, ""))
#        t2 = self.theclass(0, 0, 2, 3, tzinfo=FixedOffset(1438, ""))
#        self.assertEqual(hash(t1), hash(t2))
#
#        t1 = self.theclass(23, 58, 6, 100, tzinfo=FixedOffset(-1000, ""))
#        t2 = self.theclass(23, 48, 6, 100, tzinfo=FixedOffset(-1010, ""))
#        self.assertEqual(hash(t1), hash(t2))
#
#    def test_pickling(self):
#        # Try one without a tzinfo.
#        args = 20, 59, 16, 64**2
#        orig = self.theclass(*args)
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#
#        # Try one with a tzinfo.
#        tinfo = PicklableFixedOffset(-300, 'cookie')
#        orig = self.theclass(5, 6, 7, tzinfo=tinfo)
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
#            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
#            self.assertEqual(derived.tzname(), 'cookie')
#
#    def test_more_bool(self):
#        # Test cases with non-None tzinfo.
#        cls = self.theclass
#
#        t = cls(0, tzinfo=FixedOffset(-300, ""))
#        self.assertTrue(t)
#
#        t = cls(5, tzinfo=FixedOffset(-300, ""))
#        self.assertTrue(t)
#
#        t = cls(5, tzinfo=FixedOffset(300, ""))
#        self.assertFalse(t)
#
#        t = cls(23, 59, tzinfo=FixedOffset(23*60 + 59, ""))
#        self.assertFalse(t)
#
#        # Mostly ensuring this doesn't overflow internally.
#        t = cls(0, tzinfo=FixedOffset(23*60 + 59, ""))
#        self.assertTrue(t)
#
#        # But this should yield a value error -- the utcoffset is bogus.
#        t = cls(0, tzinfo=FixedOffset(24*60, ""))
#        self.assertRaises(ValueError, lambda: bool(t))
#
#        # Likewise.
#        t = cls(0, tzinfo=FixedOffset(-24*60, ""))
#        self.assertRaises(ValueError, lambda: bool(t))
#
#    def test_replace(self):
#        cls = self.theclass
#        z100 = FixedOffset(100, "+100")
#        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
#        args = [1, 2, 3, 4, z100]
#        base = cls(*args)
#        self.assertEqual(base, base.replace())
#
#        i = 0
#        for name, newval in (("hour", 5),
#                             ("minute", 6),
#                             ("second", 7),
#                             ("microsecond", 8),
#                             ("tzinfo", zm200)):
#            newargs = args[:]
#            newargs[i] = newval
#            expected = cls(*newargs)
#            got = base.replace(**{name: newval})
#            self.assertEqual(expected, got)
#            i += 1
#
#        # Ensure we can get rid of a tzinfo.
#        self.assertEqual(base.tzname(), "+100")
#        base2 = base.replace(tzinfo=None)
#        self.assertIsNone(base2.tzinfo)
#        self.assertIsNone(base2.tzname())
#
#        # Ensure we can add one.
#        base3 = base2.replace(tzinfo=z100)
#        self.assertEqual(base, base3)
#        self.assertIs(base.tzinfo, base3.tzinfo)
#
#        # Out of bounds.
#        base = cls(1)
#        self.assertRaises(ValueError, base.replace, hour=24)
#        self.assertRaises(ValueError, base.replace, minute=-1)
#        self.assertRaises(ValueError, base.replace, second=100)
#        self.assertRaises(ValueError, base.replace, microsecond=1000000)
#
#    def test_mixed_compare(self):
#        t1 = time(1, 2, 3)
#        t2 = time(1, 2, 3)
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=None)
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=FixedOffset(None, ""))
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
#        self.assertNotEqual(t1, t2)
#
#        # In time w/ identical tzinfo objects, utcoffset is ignored.
#        class Varies(tzinfo):
#            def __init__(self):
#                self.offset = timedelta(minutes=22)
#            def utcoffset(self, t):
#                self.offset += timedelta(minutes=1)
#                return self.offset
#
#        v = Varies()
#        t1 = t2.replace(tzinfo=v)
#        t2 = t2.replace(tzinfo=v)
#        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
#        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
#        self.assertEqual(t1, t2)
#
#        # But if they're not identical, it isn't ignored.
#        t2 = t2.replace(tzinfo=Varies())
#        self.assertTrue(t1 < t2)  # t1's offset counter still going up
#
#    def test_subclass_timetz(self):
#
#        class C(self.theclass):
#            theAnswer = 42
#
#            def __new__(cls, *args, **kws):
#                temp = kws.copy()
#                extra = temp.pop('extra')
#                result = self.theclass.__new__(cls, *args, **temp)
#                result.extra = extra
#                return result
#
#            def newmeth(self, start):
#                return start + self.hour + self.second
#
#        args = 4, 5, 6, 500, FixedOffset(-300, "EST", 1)
#
#        dt1 = self.theclass(*args)
#        dt2 = C(*args, **{'extra': 7})
#
#        self.assertEqual(dt2.__class__, C)
#        self.assertEqual(dt2.theAnswer, 42)
#        self.assertEqual(dt2.extra, 7)
#        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
#        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)
#
#
## Testing datetime objects with a non-None tzinfo.
#
#class TestDateTimeTZ(TestDateTime, TZInfoBase, unittest.TestCase):
#    theclass = datetime
#
#    def test_trivial(self):
#        dt = self.theclass(1, 2, 3, 4, 5, 6, 7)
#        self.assertEqual(dt.year, 1)
#        self.assertEqual(dt.month, 2)
#        self.assertEqual(dt.day, 3)
#        self.assertEqual(dt.hour, 4)
#        self.assertEqual(dt.minute, 5)
#        self.assertEqual(dt.second, 6)
#        self.assertEqual(dt.microsecond, 7)
#        self.assertEqual(dt.tzinfo, None)
#
#    def test_even_more_compare(self):
#        # The test_compare() and test_more_compare() inherited from TestDate
#        # and TestDateTime covered non-tzinfo cases.
#
#        # Smallest possible after UTC adjustment.
#        t1 = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
#        # Largest possible after UTC adjustment.
#        t2 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
#                           tzinfo=FixedOffset(-1439, ""))
#
#        # Make sure those compare correctly, and w/o overflow.
#        self.assertTrue(t1 < t2)
#        self.assertTrue(t1 != t2)
#        self.assertTrue(t2 > t1)
#
#        self.assertEqual(t1, t1)
#        self.assertEqual(t2, t2)
#
#        # Equal afer adjustment.
#        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""))
#        t2 = self.theclass(2, 1, 1, 3, 13, tzinfo=FixedOffset(3*60+13+2, ""))
#        self.assertEqual(t1, t2)
#
#        # Change t1 not to subtract a minute, and t1 should be larger.
#        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(0, ""))
#        self.assertTrue(t1 > t2)
#
#        # Change t1 to subtract 2 minutes, and t1 should be smaller.
#        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(2, ""))
#        self.assertTrue(t1 < t2)
#
#        # Back to the original t1, but make seconds resolve it.
#        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
#                           second=1)
#        self.assertTrue(t1 > t2)
#
#        # Likewise, but make microseconds resolve it.
#        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
#                           microsecond=1)
#        self.assertTrue(t1 > t2)
#
#        # Make t2 naive and it should differ.
#        t2 = self.theclass.min
#        self.assertNotEqual(t1, t2)
#        self.assertEqual(t2, t2)
#
#        # It's also naive if it has tzinfo but tzinfo.utcoffset() is None.
#        class Naive(tzinfo):
#            def utcoffset(self, dt): return None
#        t2 = self.theclass(5, 6, 7, tzinfo=Naive())
#        self.assertNotEqual(t1, t2)
#        self.assertEqual(t2, t2)
#
#        # OTOH, it's OK to compare two of these mixing the two ways of being
#        # naive.
#        t1 = self.theclass(5, 6, 7)
#        self.assertEqual(t1, t2)
#
#        # Try a bogus uctoffset.
#        class Bogus(tzinfo):
#            def utcoffset(self, dt):
#                return timedelta(minutes=1440) # out of bounds
#        t1 = self.theclass(2, 2, 2, tzinfo=Bogus())
#        t2 = self.theclass(2, 2, 2, tzinfo=FixedOffset(0, ""))
#        self.assertRaises(ValueError, lambda: t1 == t2)
#
#    def test_pickling(self):
#        # Try one without a tzinfo.
#        args = 6, 7, 23, 20, 59, 1, 64**2
#        orig = self.theclass(*args)
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#
#        # Try one with a tzinfo.
#        tinfo = PicklableFixedOffset(-300, 'cookie')
#        orig = self.theclass(*args, **{'tzinfo': tinfo})
#        derived = self.theclass(1, 1, 1, tzinfo=FixedOffset(0, "", 0))
#        for pickler, unpickler, proto in pickle_choices:
#            green = pickler.dumps(orig, proto)
#            derived = unpickler.loads(green)
#            self.assertEqual(orig, derived)
#            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
#            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
#            self.assertEqual(derived.tzname(), 'cookie')
#
#    def test_extreme_hashes(self):
#        # If an attempt is made to hash these via subtracting the offset
#        # then hashing a datetime object, OverflowError results.  The
#        # Python implementation used to blow up here.
#        t = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
#        hash(t)
#        t = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
#                          tzinfo=FixedOffset(-1439, ""))
#        hash(t)
#
#        # OTOH, an OOB offset should blow up.
#        t = self.theclass(5, 5, 5, tzinfo=FixedOffset(-1440, ""))
#        self.assertRaises(ValueError, hash, t)
#
#    def test_zones(self):
#        est = FixedOffset(-300, "EST")
#        utc = FixedOffset(0, "UTC")
#        met = FixedOffset(60, "MET")
#        t1 = datetime(2002, 3, 19,  7, 47, tzinfo=est)
#        t2 = datetime(2002, 3, 19, 12, 47, tzinfo=utc)
#        t3 = datetime(2002, 3, 19, 13, 47, tzinfo=met)
#        self.assertEqual(t1.tzinfo, est)
#        self.assertEqual(t2.tzinfo, utc)
#        self.assertEqual(t3.tzinfo, met)
#        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
#        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
#        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
#        self.assertEqual(t1.tzname(), "EST")
#        self.assertEqual(t2.tzname(), "UTC")
#        self.assertEqual(t3.tzname(), "MET")
#        self.assertEqual(hash(t1), hash(t2))
#        self.assertEqual(hash(t1), hash(t3))
#        self.assertEqual(hash(t2), hash(t3))
#        self.assertEqual(t1, t2)
#        self.assertEqual(t1, t3)
#        self.assertEqual(t2, t3)
#        self.assertEqual(str(t1), "2002-03-19 07:47:00-05:00")
#        self.assertEqual(str(t2), "2002-03-19 12:47:00+00:00")
#        self.assertEqual(str(t3), "2002-03-19 13:47:00+01:00")
#        d = 'datetime.datetime(2002, 3, 19, '
#        self.assertEqual(repr(t1), d + "7, 47, tzinfo=est)")
#        self.assertEqual(repr(t2), d + "12, 47, tzinfo=utc)")
#        self.assertEqual(repr(t3), d + "13, 47, tzinfo=met)")
#
#    def test_combine(self):
#        met = FixedOffset(60, "MET")
#        d = date(2002, 3, 4)
#        tz = time(18, 45, 3, 1234, tzinfo=met)
#        dt = datetime.combine(d, tz)
#        self.assertEqual(dt, datetime(2002, 3, 4, 18, 45, 3, 1234,
#                                        tzinfo=met))
#
#    def test_extract(self):
#        met = FixedOffset(60, "MET")
#        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234, tzinfo=met)
#        self.assertEqual(dt.date(), date(2002, 3, 4))
#        self.assertEqual(dt.time(), time(18, 45, 3, 1234))
#        self.assertEqual(dt.timetz(), time(18, 45, 3, 1234, tzinfo=met))
#
#    def test_tz_aware_arithmetic(self):
#        import random
#
#        now = self.theclass.now()
#        tz55 = FixedOffset(-330, "west 5:30")
#        timeaware = now.time().replace(tzinfo=tz55)
#        nowaware = self.theclass.combine(now.date(), timeaware)
#        self.assertIs(nowaware.tzinfo, tz55)
#        self.assertEqual(nowaware.timetz(), timeaware)
#
#        # Can't mix aware and non-aware.
#        self.assertRaises(TypeError, lambda: now - nowaware)
#        self.assertRaises(TypeError, lambda: nowaware - now)
#
#        # And adding datetime's doesn't make sense, aware or not.
#        self.assertRaises(TypeError, lambda: now + nowaware)
#        self.assertRaises(TypeError, lambda: nowaware + now)
#        self.assertRaises(TypeError, lambda: nowaware + nowaware)
#
#        # Subtracting should yield 0.
#        self.assertEqual(now - now, timedelta(0))
#        self.assertEqual(nowaware - nowaware, timedelta(0))
#
#        # Adding a delta should preserve tzinfo.
#        delta = timedelta(weeks=1, minutes=12, microseconds=5678)
#        nowawareplus = nowaware + delta
#        self.assertIs(nowaware.tzinfo, tz55)
#        nowawareplus2 = delta + nowaware
#        self.assertIs(nowawareplus2.tzinfo, tz55)
#        self.assertEqual(nowawareplus, nowawareplus2)
#
#        # that - delta should be what we started with, and that - what we
#        # started with should be delta.
#        diff = nowawareplus - delta
#        self.assertIs(diff.tzinfo, tz55)
#        self.assertEqual(nowaware, diff)
#        self.assertRaises(TypeError, lambda: delta - nowawareplus)
#        self.assertEqual(nowawareplus - nowaware, delta)
#
#        # Make up a random timezone.
#        tzr = FixedOffset(random.randrange(-1439, 1440), "randomtimezone")
#        # Attach it to nowawareplus.
#        nowawareplus = nowawareplus.replace(tzinfo=tzr)
#        self.assertIs(nowawareplus.tzinfo, tzr)
#        # Make sure the difference takes the timezone adjustments into account.
#        got = nowaware - nowawareplus
#        # Expected:  (nowaware base - nowaware offset) -
#        #            (nowawareplus base - nowawareplus offset) =
#        #            (nowaware base - nowawareplus base) +
#        #            (nowawareplus offset - nowaware offset) =
#        #            -delta + nowawareplus offset - nowaware offset
#        expected = nowawareplus.utcoffset() - nowaware.utcoffset() - delta
#        self.assertEqual(got, expected)
#
#        # Try max possible difference.
#        min = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, "min"))
#        max = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
#                            tzinfo=FixedOffset(-1439, "max"))
#        maxdiff = max - min
#        self.assertEqual(maxdiff, self.theclass.max - self.theclass.min +
#                                  timedelta(minutes=2*1439))
#        # Different tzinfo, but the same offset
#        tza = timezone(HOUR, 'A')
#        tzb = timezone(HOUR, 'B')
#        delta = min.replace(tzinfo=tza) - max.replace(tzinfo=tzb)
#        self.assertEqual(delta, self.theclass.min - self.theclass.max)
#
#    def test_tzinfo_now(self):
#        meth = self.theclass.now
#        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
#        base = meth()
#        # Try with and without naming the keyword.
#        off42 = FixedOffset(42, "42")
#        another = meth(off42)
#        again = meth(tz=off42)
#        self.assertIs(another.tzinfo, again.tzinfo)
#        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
#        # Bad argument with and w/o naming the keyword.
#        self.assertRaises(TypeError, meth, 16)
#        self.assertRaises(TypeError, meth, tzinfo=16)
#        # Bad keyword name.
#        self.assertRaises(TypeError, meth, tinfo=off42)
#        # Too many args.
#        self.assertRaises(TypeError, meth, off42, off42)
#
#        # We don't know which time zone we're in, and don't have a tzinfo
#        # class to represent it, so seeing whether a tz argument actually
#        # does a conversion is tricky.
#        utc = FixedOffset(0, "utc", 0)
#        for weirdtz in [FixedOffset(timedelta(hours=15, minutes=58), "weirdtz", 0),
#                        timezone(timedelta(hours=15, minutes=58), "weirdtz"),]:
#            for dummy in range(3):
#                now = datetime.now(weirdtz)
#                self.assertIs(now.tzinfo, weirdtz)
#                utcnow = datetime.utcnow().replace(tzinfo=utc)
#                now2 = utcnow.astimezone(weirdtz)
#                if abs(now - now2) < timedelta(seconds=30):
#                    break
#                # Else the code is broken, or more than 30 seconds passed between
#                # calls; assuming the latter, just try again.
#            else:
#                # Three strikes and we're out.
#                self.fail("utcnow(), now(tz), or astimezone() may be broken")
#
#    def test_tzinfo_fromtimestamp(self):
#        import time
#        meth = self.theclass.fromtimestamp
#        ts = time.time()
#        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
#        base = meth(ts)
#        # Try with and without naming the keyword.
#        off42 = FixedOffset(42, "42")
#        another = meth(ts, off42)
#        again = meth(ts, tz=off42)
#        self.assertIs(another.tzinfo, again.tzinfo)
#        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
#        # Bad argument with and w/o naming the keyword.
#        self.assertRaises(TypeError, meth, ts, 16)
#        self.assertRaises(TypeError, meth, ts, tzinfo=16)
#        # Bad keyword name.
#        self.assertRaises(TypeError, meth, ts, tinfo=off42)
#        # Too many args.
#        self.assertRaises(TypeError, meth, ts, off42, off42)
#        # Too few args.
#        self.assertRaises(TypeError, meth)
#
#        # Try to make sure tz= actually does some conversion.
#        timestamp = 1000000000
#        utcdatetime = datetime.utcfromtimestamp(timestamp)
#        # In POSIX (epoch 1970), that's 2001-09-09 01:46:40 UTC, give or take.
#        # But on some flavor of Mac, it's nowhere near that.  So we can't have
#        # any idea here what time that actually is, we can only test that
#        # relative changes match.
#        utcoffset = timedelta(hours=-15, minutes=39) # arbitrary, but not zero
#        tz = FixedOffset(utcoffset, "tz", 0)
#        expected = utcdatetime + utcoffset
#        got = datetime.fromtimestamp(timestamp, tz)
#        self.assertEqual(expected, got.replace(tzinfo=None))
#
#    def test_tzinfo_utcnow(self):
#        meth = self.theclass.utcnow
#        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
#        base = meth()
#        # Try with and without naming the keyword; for whatever reason,
#        # utcnow() doesn't accept a tzinfo argument.
#        off42 = FixedOffset(42, "42")
#        self.assertRaises(TypeError, meth, off42)
#        self.assertRaises(TypeError, meth, tzinfo=off42)
#
#    def test_tzinfo_utcfromtimestamp(self):
#        import time
#        meth = self.theclass.utcfromtimestamp
#        ts = time.time()
#        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
#        base = meth(ts)
#        # Try with and without naming the keyword; for whatever reason,
#        # utcfromtimestamp() doesn't accept a tzinfo argument.
#        off42 = FixedOffset(42, "42")
#        self.assertRaises(TypeError, meth, ts, off42)
#        self.assertRaises(TypeError, meth, ts, tzinfo=off42)
#
#    def test_tzinfo_timetuple(self):
#        # TestDateTime tested most of this.  datetime adds a twist to the
#        # DST flag.
#        class DST(tzinfo):
#            def __init__(self, dstvalue):
#                if isinstance(dstvalue, int):
#                    dstvalue = timedelta(minutes=dstvalue)
#                self.dstvalue = dstvalue
#            def dst(self, dt):
#                return self.dstvalue
#
#        cls = self.theclass
#        for dstvalue, flag in (-33, 1), (33, 1), (0, 0), (None, -1):
#            d = cls(1, 1, 1, 10, 20, 30, 40, tzinfo=DST(dstvalue))
#            t = d.timetuple()
#            self.assertEqual(1, t.tm_year)
#            self.assertEqual(1, t.tm_mon)
#            self.assertEqual(1, t.tm_mday)
#            self.assertEqual(10, t.tm_hour)
#            self.assertEqual(20, t.tm_min)
#            self.assertEqual(30, t.tm_sec)
#            self.assertEqual(0, t.tm_wday)
#            self.assertEqual(1, t.tm_yday)
#            self.assertEqual(flag, t.tm_isdst)
#
#        # dst() returns wrong type.
#        self.assertRaises(TypeError, cls(1, 1, 1, tzinfo=DST("x")).timetuple)
#
#        # dst() at the edge.
#        self.assertEqual(cls(1,1,1, tzinfo=DST(1439)).timetuple().tm_isdst, 1)
#        self.assertEqual(cls(1,1,1, tzinfo=DST(-1439)).timetuple().tm_isdst, 1)
#
#        # dst() out of range.
#        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(1440)).timetuple)
#        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(-1440)).timetuple)
#
#    def test_utctimetuple(self):
#        class DST(tzinfo):
#            def __init__(self, dstvalue=0):
#                if isinstance(dstvalue, int):
#                    dstvalue = timedelta(minutes=dstvalue)
#                self.dstvalue = dstvalue
#            def dst(self, dt):
#                return self.dstvalue
#
#        cls = self.theclass
#        # This can't work:  DST didn't implement utcoffset.
#        self.assertRaises(NotImplementedError,
#                          cls(1, 1, 1, tzinfo=DST(0)).utcoffset)
#
#        class UOFS(DST):
#            def __init__(self, uofs, dofs=None):
#                DST.__init__(self, dofs)
#                self.uofs = timedelta(minutes=uofs)
#            def utcoffset(self, dt):
#                return self.uofs
#
#        for dstvalue in -33, 33, 0, None:
#            d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=UOFS(-53, dstvalue))
#            t = d.utctimetuple()
#            self.assertEqual(d.year, t.tm_year)
#            self.assertEqual(d.month, t.tm_mon)
#            self.assertEqual(d.day, t.tm_mday)
#            self.assertEqual(11, t.tm_hour) # 20mm + 53mm = 1hn + 13mm
#            self.assertEqual(13, t.tm_min)
#            self.assertEqual(d.second, t.tm_sec)
#            self.assertEqual(d.weekday(), t.tm_wday)
#            self.assertEqual(d.toordinal() - date(1, 1, 1).toordinal() + 1,
#                             t.tm_yday)
#            # Ensure tm_isdst is 0 regardless of what dst() says: DST
#            # is never in effect for a UTC time.
#            self.assertEqual(0, t.tm_isdst)
#
#        # For naive datetime, utctimetuple == timetuple except for isdst
#        d = cls(1, 2, 3, 10, 20, 30, 40)
#        t = d.utctimetuple()
#        self.assertEqual(t[:-1], d.timetuple()[:-1])
#        self.assertEqual(0, t.tm_isdst)
#        # Same if utcoffset is None
#        class NOFS(DST):
#            def utcoffset(self, dt):
#                return None
#        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=NOFS())
#        t = d.utctimetuple()
#        self.assertEqual(t[:-1], d.timetuple()[:-1])
#        self.assertEqual(0, t.tm_isdst)
#        # Check that bad tzinfo is detected
#        class BOFS(DST):
#            def utcoffset(self, dt):
#                return "EST"
#        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=BOFS())
#        self.assertRaises(TypeError, d.utctimetuple)
#
#        # Check that utctimetuple() is the same as
#        # astimezone(utc).timetuple()
#        d = cls(2010, 11, 13, 14, 15, 16, 171819)
#        for tz in [timezone.min, timezone.utc, timezone.max]:
#            dtz = d.replace(tzinfo=tz)
#            self.assertEqual(dtz.utctimetuple()[:-1],
#                             dtz.astimezone(timezone.utc).timetuple()[:-1])
#        # At the edges, UTC adjustment can produce years out-of-range
#        # for a datetime object.  Ensure that an OverflowError is
#        # raised.
#        tiny = cls(MINYEAR, 1, 1, 0, 0, 37, tzinfo=UOFS(1439))
#        # That goes back 1 minute less than a full day.
#        self.assertRaises(OverflowError, tiny.utctimetuple)
#
#        huge = cls(MAXYEAR, 12, 31, 23, 59, 37, 999999, tzinfo=UOFS(-1439))
#        # That goes forward 1 minute less than a full day.
#        self.assertRaises(OverflowError, huge.utctimetuple)
#        # More overflow cases
#        tiny = cls.min.replace(tzinfo=timezone(MINUTE))
#        self.assertRaises(OverflowError, tiny.utctimetuple)
#        huge = cls.max.replace(tzinfo=timezone(-MINUTE))
#        self.assertRaises(OverflowError, huge.utctimetuple)
#
#    def test_tzinfo_isoformat(self):
#        zero = FixedOffset(0, "+00:00")
#        plus = FixedOffset(220, "+03:40")
#        minus = FixedOffset(-231, "-03:51")
#        unknown = FixedOffset(None, "")
#
#        cls = self.theclass
#        datestr = '0001-02-03'
#        for ofs in None, zero, plus, minus, unknown:
#            for us in 0, 987001:
#                d = cls(1, 2, 3, 4, 5, 59, us, tzinfo=ofs)
#                timestr = '04:05:59' + (us and '.987001' or '')
#                ofsstr = ofs is not None and d.tzname() or ''
#                tailstr = timestr + ofsstr
#                iso = d.isoformat()
#                self.assertEqual(iso, datestr + 'T' + tailstr)
#                self.assertEqual(iso, d.isoformat('T'))
#                self.assertEqual(d.isoformat('k'), datestr + 'k' + tailstr)
#                self.assertEqual(d.isoformat('\u1234'), datestr + '\u1234' + tailstr)
#                self.assertEqual(str(d), datestr + ' ' + tailstr)
#
#    def test_replace(self):
#        cls = self.theclass
#        z100 = FixedOffset(100, "+100")
#        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
#        args = [1, 2, 3, 4, 5, 6, 7, z100]
#        base = cls(*args)
#        self.assertEqual(base, base.replace())
#
#        i = 0
#        for name, newval in (("year", 2),
#                             ("month", 3),
#                             ("day", 4),
#                             ("hour", 5),
#                             ("minute", 6),
#                             ("second", 7),
#                             ("microsecond", 8),
#                             ("tzinfo", zm200)):
#            newargs = args[:]
#            newargs[i] = newval
#            expected = cls(*newargs)
#            got = base.replace(**{name: newval})
#            self.assertEqual(expected, got)
#            i += 1
#
#        # Ensure we can get rid of a tzinfo.
#        self.assertEqual(base.tzname(), "+100")
#        base2 = base.replace(tzinfo=None)
#        self.assertIsNone(base2.tzinfo)
#        self.assertIsNone(base2.tzname())
#
#        # Ensure we can add one.
#        base3 = base2.replace(tzinfo=z100)
#        self.assertEqual(base, base3)
#        self.assertIs(base.tzinfo, base3.tzinfo)
#
#        # Out of bounds.
#        base = cls(2000, 2, 29)
#        self.assertRaises(ValueError, base.replace, year=2001)
#
#    def test_more_astimezone(self):
#        # The inherited test_astimezone covered some trivial and error cases.
#        fnone = FixedOffset(None, "None")
#        f44m = FixedOffset(44, "44")
#        fm5h = FixedOffset(-timedelta(hours=5), "m300")
#
#        dt = self.theclass.now(tz=f44m)
#        self.assertIs(dt.tzinfo, f44m)
#        # Replacing with degenerate tzinfo raises an exception.
#        self.assertRaises(ValueError, dt.astimezone, fnone)
#        # Replacing with same tzinfo makes no change.
#        x = dt.astimezone(dt.tzinfo)
#        self.assertIs(x.tzinfo, f44m)
#        self.assertEqual(x.date(), dt.date())
#        self.assertEqual(x.time(), dt.time())
#
#        # Replacing with different tzinfo does adjust.
#        got = dt.astimezone(fm5h)
#        self.assertIs(got.tzinfo, fm5h)
#        self.assertEqual(got.utcoffset(), timedelta(hours=-5))
#        expected = dt - dt.utcoffset()  # in effect, convert to UTC
#        expected += fm5h.utcoffset(dt)  # and from there to local time
#        expected = expected.replace(tzinfo=fm5h) # and attach new tzinfo
#        self.assertEqual(got.date(), expected.date())
#        self.assertEqual(got.time(), expected.time())
#        self.assertEqual(got.timetz(), expected.timetz())
#        self.assertIs(got.tzinfo, expected.tzinfo)
#        self.assertEqual(got, expected)
#
#    @support.run_with_tz('UTC')
#    def test_astimezone_default_utc(self):
#        dt = self.theclass.now(timezone.utc)
#        self.assertEqual(dt.astimezone(None), dt)
#        self.assertEqual(dt.astimezone(), dt)
#
#    # Note that offset in TZ variable has the opposite sign to that
#    # produced by %z directive.
#    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
#    def test_astimezone_default_eastern(self):
#        dt = self.theclass(2012, 11, 4, 6, 30, tzinfo=timezone.utc)
#        local = dt.astimezone()
#        self.assertEqual(dt, local)
#        self.assertEqual(local.strftime("%z %Z"), "-0500 EST")
#        dt = self.theclass(2012, 11, 4, 5, 30, tzinfo=timezone.utc)
#        local = dt.astimezone()
#        self.assertEqual(dt, local)
#        self.assertEqual(local.strftime("%z %Z"), "-0400 EDT")
#
#    def test_aware_subtract(self):
#        cls = self.theclass
#
#        # Ensure that utcoffset() is ignored when the operands have the
#        # same tzinfo member.
#        class OperandDependentOffset(tzinfo):
#            def utcoffset(self, t):
#                if t.minute < 10:
#                    # d0 and d1 equal after adjustment
#                    return timedelta(minutes=t.minute)
#                else:
#                    # d2 off in the weeds
#                    return timedelta(minutes=59)
#
#        base = cls(8, 9, 10, 11, 12, 13, 14, tzinfo=OperandDependentOffset())
#        d0 = base.replace(minute=3)
#        d1 = base.replace(minute=9)
#        d2 = base.replace(minute=11)
#        for x in d0, d1, d2:
#            for y in d0, d1, d2:
#                got = x - y
#                expected = timedelta(minutes=x.minute - y.minute)
#                self.assertEqual(got, expected)
#
#        # OTOH, if the tzinfo members are distinct, utcoffsets aren't
#        # ignored.
#        base = cls(8, 9, 10, 11, 12, 13, 14)
#        d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
#        d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
#        d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
#        for x in d0, d1, d2:
#            for y in d0, d1, d2:
#                got = x - y
#                if (x is d0 or x is d1) and (y is d0 or y is d1):
#                    expected = timedelta(0)
#                elif x is y is d2:
#                    expected = timedelta(0)
#                elif x is d2:
#                    expected = timedelta(minutes=(11-59)-0)
#                else:
#                    assert y is d2
#                    expected = timedelta(minutes=0-(11-59))
#                self.assertEqual(got, expected)
#
#    def test_mixed_compare(self):
#        t1 = datetime(1, 2, 3, 4, 5, 6, 7)
#        t2 = datetime(1, 2, 3, 4, 5, 6, 7)
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=None)
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=FixedOffset(None, ""))
#        self.assertEqual(t1, t2)
#        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
#        self.assertNotEqual(t1, t2)
#
#        # In datetime w/ identical tzinfo objects, utcoffset is ignored.
#        class Varies(tzinfo):
#            def __init__(self):
#                self.offset = timedelta(minutes=22)
#            def utcoffset(self, t):
#                self.offset += timedelta(minutes=1)
#                return self.offset
#
#        v = Varies()
#        t1 = t2.replace(tzinfo=v)
#        t2 = t2.replace(tzinfo=v)
#        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
#        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
#        self.assertEqual(t1, t2)
#
#        # But if they're not identical, it isn't ignored.
#        t2 = t2.replace(tzinfo=Varies())
#        self.assertTrue(t1 < t2)  # t1's offset counter still going up
#
#    def test_subclass_datetimetz(self):
#
#        class C(self.theclass):
#            theAnswer = 42
#
#            def __new__(cls, *args, **kws):
#                temp = kws.copy()
#                extra = temp.pop('extra')
#                result = self.theclass.__new__(cls, *args, **temp)
#                result.extra = extra
#                return result
#
#            def newmeth(self, start):
#                return start + self.hour + self.year
#
#        args = 2002, 12, 31, 4, 5, 6, 500, FixedOffset(-300, "EST", 1)
#
#        dt1 = self.theclass(*args)
#        dt2 = C(*args, **{'extra': 7})
#
#        self.assertEqual(dt2.__class__, C)
#        self.assertEqual(dt2.theAnswer, 42)
#        self.assertEqual(dt2.extra, 7)
#        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
#        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.year - 7)
#
# ----------------------------------------------------------------------------------------------------------------------
# This line delimiter marks the code that was moved to test_datetime6.py
