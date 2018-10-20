#import builtins
#import copyreg
#import gc
#import itertools
#import math
#import pickle
#import sys
#import types
import unittest
#import weakref

#from copy import deepcopy
#from test import support


#############################################################################   ###
class ClassPropertiesAndMethods(unittest.TestCase):
    def test_supers(self):
        # Testing super...

        class A(object):
            def meth(self, a):
                return "A(%r)" % a

        self.assertEqual(A().meth(1), "A(1)")

        class B(A):
            def __init__(self):
                self.__super = super(B, self)
            def meth(self, a):
                return "B(%r)" % a + self.__super.meth(a)

        self.assertEqual(B().meth(2), "B(2)A(2)")

#        class C(A):
#            def meth(self, a):
#                return "C(%r)" % a + self.__super.meth(a)
#        C._C__super = super(C)
#
#        self.assertEqual(C().meth(3), "C(3)A(3)")
#
#        class D(C, B):
#            def meth(self, a):
#                return "D(%r)" % a + super(D, self).meth(a)
#
#        self.assertEqual(D().meth(4), "D(4)C(4)B(4)A(4)")
#
#        # Test for subclassing super
#
#        class mysuper(super):
#            def __init__(self, *args):
#                return super(mysuper, self).__init__(*args)
#
#        class E(D):
#            def meth(self, a):
#                return "E(%r)" % a + mysuper(E, self).meth(a)
#
#        self.assertEqual(E().meth(5), "E(5)D(5)C(5)B(5)A(5)")
#
#        class F(E):
#            def meth(self, a):
#                s = self.__super # == mysuper(F, self)
#                return "F(%r)[%s]" % (a, s.__class__.__name__) + s.meth(a)
#        F._F__super = mysuper(F)
#
#        self.assertEqual(F().meth(6), "F(6)[mysuper]E(6)D(6)C(6)B(6)A(6)")
#
#        # Make sure certain errors are raised
#
#        try:
#            super(D, 42)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't allow super(D, 42)")
#
#        try:
#            super(D, C())
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't allow super(D, C())")
#
#        try:
#            super(D).__get__(12)
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't allow super(D).__get__(12)")
#
#        try:
#            super(D).__get__(C())
#        except TypeError:
#            pass
#        else:
#            self.fail("shouldn't allow super(D).__get__(C())")
#
        # Make sure data descriptors can be overridden and accessed via super
        # (new feature in Python 2.3)

        class DDbase(object):
            def getx(self): return 42
            x = property(getx)

        class DDsub(DDbase):
            def getx(self): return "hello"
            x = property(getx)

        dd = DDsub()
        self.assertEqual(dd.x, "hello")
        self.assertEqual(super(DDsub, dd).x, 42)

        # Ensure that super() lookup of descriptor from classmethod
        # works (SF ID# 743627)

        class Base(object):
            aProp = property(lambda self: "foo")

#        class Sub(Base):
#            @classmethod
#            def test(klass):
#                return super(Sub,klass).aProp
#
#        self.assertEqual(Sub.test(), Base.aProp)
#
        # Verify that super() doesn't allow keyword args
        try:
            super(Base, kw=1)
        except TypeError:
            pass
        else:
            self.assertEqual("super shouldn't accept keyword args")

    def test_basic_inheritance(self):
        # Testing inheritance from basic types...

        class hexint(int):
            def __repr__(self):
                return hex(self)
            def __add__(self, other):
                return hexint(int.__add__(self, other))
            # (Note that overriding __radd__ doesn't work,
            # because the int type gets first dibs.)
#        self.assertEqual(repr(hexint(7) + 9), "0x10")
#        self.assertEqual(repr(hexint(1000) + 7), "0x3ef")
        a = hexint(12345)
        self.assertEqual(a, 12345)
#        self.assertEqual(int(a), 12345)
#        self.assertIs(int(a).__class__, int)
        self.assertEqual(hash(a), hash(12345))
        self.assertIs((+a).__class__, int)
        self.assertIs((a >> 0).__class__, int)
        self.assertIs((a << 0).__class__, int)
        self.assertIs((hexint(0) << 12).__class__, int)
        self.assertIs((hexint(0) >> 12).__class__, int)

#        class octlong(int):
#            __slots__ = []
#            def __str__(self):
#                return oct(self)
#            def __add__(self, other):
#                return self.__class__(super(octlong, self).__add__(other))
#            __radd__ = __add__
#        self.assertEqual(str(octlong(3) + 5), "0o10")
#        # (Note that overriding __radd__ here only seems to work
#        # because the example uses a short int left argument.)
#        self.assertEqual(str(5 + octlong(3000)), "0o5675")
#        a = octlong(12345)
#        self.assertEqual(a, 12345)
#        self.assertEqual(int(a), 12345)
#        self.assertEqual(hash(a), hash(12345))
#        self.assertIs(int(a).__class__, int)
#        self.assertIs((+a).__class__, int)
#        self.assertIs((-a).__class__, int)
#        self.assertIs((-octlong(0)).__class__, int)
#        self.assertIs((a >> 0).__class__, int)
#        self.assertIs((a << 0).__class__, int)
#        self.assertIs((a - 0).__class__, int)
#        self.assertIs((a * 1).__class__, int)
#        self.assertIs((a ** 1).__class__, int)
#        self.assertIs((a // 1).__class__, int)
#        self.assertIs((1 * a).__class__, int)
#        self.assertIs((a | 0).__class__, int)
#        self.assertIs((a ^ 0).__class__, int)
#        self.assertIs((a & -1).__class__, int)
#        self.assertIs((octlong(0) << 12).__class__, int)
#        self.assertIs((octlong(0) >> 12).__class__, int)
#        self.assertIs(abs(octlong(0)).__class__, int)
#
        # Because octlong overrides __add__, we can't check the absence of +0
        # optimizations using octlong.
        class longclone(int):
            pass
        a = longclone(1)
        self.assertIs((a + 0).__class__, int)
#        self.assertIs((0 + a).__class__, int)

        # Check that negative clones don't segfault
        a = longclone(-1)
        self.assertEqual(a.__dict__, {})
#        self.assertEqual(int(a), -1)  # self.assertTrue PyNumber_Long() copies the sign bit

#        class precfloat(float):
#            __slots__ = ['prec']
#            def __init__(self, value=0.0, prec=12):
#                self.prec = int(prec)
#            def __repr__(self):
#                return "%.*g" % (self.prec, self)
#        self.assertEqual(repr(precfloat(1.1)), "1.1")
#        a = precfloat(12345)
#        self.assertEqual(a, 12345.0)
#        self.assertEqual(float(a), 12345.0)
#        self.assertIs(float(a).__class__, float)
#        self.assertEqual(hash(a), hash(12345.0))
#        self.assertIs((+a).__class__, float)
#
        class madcomplex(complex):
            def __repr__(self):
                return "%.17gj%+.17g" % (self.imag, self.real)
        a = madcomplex(-3, 4)
        self.assertEqual(repr(a), "4j-3")
        base = complex(-3, 4)
        self.assertEqual(base.__class__, complex)
        self.assertEqual(a, base)
#        self.assertEqual(complex(a), base)
#        self.assertEqual(complex(a).__class__, complex)
#        a = madcomplex(a)  # just trying another form of the constructor
#        self.assertEqual(repr(a), "4j-3")
#        self.assertEqual(a, base)
#        self.assertEqual(complex(a), base)
#        self.assertEqual(complex(a).__class__, complex)
#        self.assertEqual(hash(a), hash(base))
#        self.assertEqual((+a).__class__, complex)
#        self.assertEqual((a + 0).__class__, complex)
#        self.assertEqual(a + 0, base)
#        self.assertEqual((a - 0).__class__, complex)
#        self.assertEqual(a - 0, base)
#        self.assertEqual((a * 1).__class__, complex)
#        self.assertEqual(a * 1, base)
#        self.assertEqual((a / 1).__class__, complex)
#        self.assertEqual(a / 1, base)

        class madtuple(tuple):
            _rev = None
            def rev(self):
                if self._rev is not None:
                    return self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__(L)
                return self._rev
        a = madtuple((1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a, (1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a.rev(), madtuple((0,9,8,7,6,5,4,3,2,1)))
        self.assertEqual(a.rev().rev(), madtuple((1,2,3,4,5,6,7,8,9,0)))
        for i in range(512):
            t = madtuple(range(i))
            u = t.rev()
            v = u.rev()
            self.assertEqual(v, t)
        a = madtuple((1,2,3,4,5))
        self.assertEqual(tuple(a), (1,2,3,4,5))
        self.assertIs(tuple(a).__class__, tuple)
        self.assertEqual(hash(a), hash((1,2,3,4,5)))
        self.assertIs(a[:].__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a + ()).__class__, tuple)
        a = madtuple(())
        self.assertEqual(tuple(a), ())
        self.assertIs(tuple(a).__class__, tuple)
        self.assertIs((a + a).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 2).__class__, tuple)
        self.assertIs(a[:].__class__, tuple)

#        class madstring(str):
#            _rev = None
#            def rev(self):
#                if self._rev is not None:
#                    return self._rev
#                L = list(self)
#                L.reverse()
#                self._rev = self.__class__("".join(L))
#                return self._rev
#        s = madstring("abcdefghijklmnopqrstuvwxyz")
#        self.assertEqual(s, "abcdefghijklmnopqrstuvwxyz")
#        self.assertEqual(s.rev(), madstring("zyxwvutsrqponmlkjihgfedcba"))
#        self.assertEqual(s.rev().rev(), madstring("abcdefghijklmnopqrstuvwxyz"))
#        for i in range(256):
#            s = madstring("".join(map(chr, range(i))))
#            t = s.rev()
#            u = t.rev()
#            self.assertEqual(u, s)
#        s = madstring("12345")
#        self.assertEqual(str(s), "12345")
#        self.assertIs(str(s).__class__, str)
#
#        base = "\x00" * 5
#        s = madstring(base)
#        self.assertEqual(s, base)
#        self.assertEqual(str(s), base)
#        self.assertIs(str(s).__class__, str)
#        self.assertEqual(hash(s), hash(base))
#        self.assertEqual({s: 1}[base], 1)
#        self.assertEqual({base: 1}[s], 1)
#        self.assertIs((s + "").__class__, str)
#        self.assertEqual(s + "", base)
#        self.assertIs(("" + s).__class__, str)
#        self.assertEqual("" + s, base)
#        self.assertIs((s * 0).__class__, str)
#        self.assertEqual(s * 0, "")
#        self.assertIs((s * 1).__class__, str)
#        self.assertEqual(s * 1, base)
#        self.assertIs((s * 2).__class__, str)
#        self.assertEqual(s * 2, base + base)
#        self.assertIs(s[:].__class__, str)
#        self.assertEqual(s[:], base)
#        self.assertIs(s[0:0].__class__, str)
#        self.assertEqual(s[0:0], "")
#        self.assertIs(s.strip().__class__, str)
#        self.assertEqual(s.strip(), base)
#        self.assertIs(s.lstrip().__class__, str)
#        self.assertEqual(s.lstrip(), base)
#        self.assertIs(s.rstrip().__class__, str)
#        self.assertEqual(s.rstrip(), base)
#        identitytab = {}
#        self.assertIs(s.translate(identitytab).__class__, str)
#        self.assertEqual(s.translate(identitytab), base)
#        self.assertIs(s.replace("x", "x").__class__, str)
#        self.assertEqual(s.replace("x", "x"), base)
#        self.assertIs(s.ljust(len(s)).__class__, str)
#        self.assertEqual(s.ljust(len(s)), base)
#        self.assertIs(s.rjust(len(s)).__class__, str)
#        self.assertEqual(s.rjust(len(s)), base)
#        self.assertIs(s.center(len(s)).__class__, str)
#        self.assertEqual(s.center(len(s)), base)
#        self.assertIs(s.lower().__class__, str)
#        self.assertEqual(s.lower(), base)
#
#        class madunicode(str):
#            _rev = None
#            def rev(self):
#                if self._rev is not None:
#                    return self._rev
#                L = list(self)
#                L.reverse()
#                self._rev = self.__class__("".join(L))
#                return self._rev
#        u = madunicode("ABCDEF")
#        self.assertEqual(u, "ABCDEF")
#        self.assertEqual(u.rev(), madunicode("FEDCBA"))
#        self.assertEqual(u.rev().rev(), madunicode("ABCDEF"))
#        base = "12345"
#        u = madunicode(base)
#        self.assertEqual(str(u), base)
#        self.assertIs(str(u).__class__, str)
#        self.assertEqual(hash(u), hash(base))
#        self.assertEqual({u: 1}[base], 1)
#        self.assertEqual({base: 1}[u], 1)
#        self.assertIs(u.strip().__class__, str)
#        self.assertEqual(u.strip(), base)
#        self.assertIs(u.lstrip().__class__, str)
#        self.assertEqual(u.lstrip(), base)
#        self.assertIs(u.rstrip().__class__, str)
#        self.assertEqual(u.rstrip(), base)
#        self.assertIs(u.replace("x", "x").__class__, str)
#        self.assertEqual(u.replace("x", "x"), base)
#        self.assertIs(u.replace("xy", "xy").__class__, str)
#        self.assertEqual(u.replace("xy", "xy"), base)
#        self.assertIs(u.center(len(u)).__class__, str)
#        self.assertEqual(u.center(len(u)), base)
#        self.assertIs(u.ljust(len(u)).__class__, str)
#        self.assertEqual(u.ljust(len(u)), base)
#        self.assertIs(u.rjust(len(u)).__class__, str)
#        self.assertEqual(u.rjust(len(u)), base)
#        self.assertIs(u.lower().__class__, str)
#        self.assertEqual(u.lower(), base)
#        self.assertIs(u.upper().__class__, str)
#        self.assertEqual(u.upper(), base)
#        self.assertIs(u.capitalize().__class__, str)
#        self.assertEqual(u.capitalize(), base)
#        self.assertIs(u.title().__class__, str)
#        self.assertEqual(u.title(), base)
#        self.assertIs((u + "").__class__, str)
#        self.assertEqual(u + "", base)
#        self.assertIs(("" + u).__class__, str)
#        self.assertEqual("" + u, base)
#        self.assertIs((u * 0).__class__, str)
#        self.assertEqual(u * 0, "")
#        self.assertIs((u * 1).__class__, str)
#        self.assertEqual(u * 1, base)
#        self.assertIs((u * 2).__class__, str)
#        self.assertEqual(u * 2, base + base)
#        self.assertIs(u[:].__class__, str)
#        self.assertEqual(u[:], base)
#        self.assertIs(u[0:0].__class__, str)
#        self.assertEqual(u[0:0], "")
#
        class sublist(list):
            pass
        a = sublist(range(5))
        self.assertEqual(a, list(range(5)))
        a.append("hello")
        self.assertEqual(a, list(range(5)) + ["hello"])
        a[5] = 5
        self.assertEqual(a, list(range(6)))
        a.extend(range(6, 20))
        self.assertEqual(a, list(range(20)))
        a[-5:] = []
        self.assertEqual(a, list(range(15)))
        del a[10:15]
        self.assertEqual(len(a), 10)
        self.assertEqual(a, list(range(10)))
        self.assertEqual(list(a), list(range(10)))
        self.assertEqual(a[0], 0)
        self.assertEqual(a[9], 9)
        self.assertEqual(a[-10], 0)
        self.assertEqual(a[-1], 9)
        self.assertEqual(a[:5], list(range(5)))

        ## class CountedInput(file):
        ##    """Counts lines read by self.readline().
        ##
        ##     self.lineno is the 0-based ordinal of the last line read, up to
        ##     a maximum of one greater than the number of lines in the file.
        ##
        ##     self.ateof is true if and only if the final "" line has been read,
        ##     at which point self.lineno stops incrementing, and further calls
        ##     to readline() continue to return "".
        ##     """
        ##
        ##     lineno = 0
        ##     ateof = 0
        ##     def readline(self):
        ##         if self.ateof:
        ##             return ""
        ##         s = file.readline(self)
        ##         # Next line works too.
        ##         # s = super(CountedInput, self).readline()
        ##         self.lineno += 1
        ##         if s == "":
        ##             self.ateof = 1
        ##        return s
        ##
        ## f = file(name=support.TESTFN, mode='w')
        ## lines = ['a\n', 'b\n', 'c\n']
        ## try:
        ##     f.writelines(lines)
        ##     f.close()
        ##     f = CountedInput(support.TESTFN)
        ##     for (i, expected) in zip(range(1, 5) + [4], lines + 2 * [""]):
        ##         got = f.readline()
        ##         self.assertEqual(expected, got)
        ##         self.assertEqual(f.lineno, i)
        ##         self.assertEqual(f.ateof, (i > len(lines)))
        ##     f.close()
        ## finally:
        ##     try:
        ##         f.close()
        ##     except:
        ##         pass
        ##     support.unlink(support.TESTFN)

#    def test_keywords(self):
#        # Testing keyword args to basic type constructors ...
#        self.assertEqual(int(x=1), 1)
#        self.assertEqual(float(x=2), 2.0)
#        self.assertEqual(int(x=3), 3)
#        self.assertEqual(complex(imag=42, real=666), complex(666, 42))
#        self.assertEqual(str(object=500), '500')
#        self.assertEqual(str(object=b'abc', errors='strict'), 'abc')
#        self.assertEqual(tuple(sequence=range(3)), (0, 1, 2))
#        self.assertEqual(list(sequence=(0, 1, 2)), list(range(3)))
#        # note: as of Python 2.3, dict() no longer has an "items" keyword arg
#
#        for constructor in (int, float, int, complex, str, str,
#                            tuple, list):
#            try:
#                constructor(bogus_keyword_arg=1)
#            except TypeError:
#                pass
#            else:
#                self.fail("expected TypeError from bogus keyword argument to %r"
#                            % constructor)
#
#    def test_str_subclass_as_dict_key(self):
#        # Testing a str subclass used as dict key ..
#
#        class cistr(str):
#            """Sublcass of str that computes __eq__ case-insensitively.
#
#            Also computes a hash code of the string in canonical form.
#            """
#
#            def __init__(self, value):
#                self.canonical = value.lower()
#                self.hashcode = hash(self.canonical)
#
#            def __eq__(self, other):
#                if not isinstance(other, cistr):
#                    other = cistr(other)
#                return self.canonical == other.canonical
#
#            def __hash__(self):
#                return self.hashcode
#
#        self.assertEqual(cistr('ABC'), 'abc')
#        self.assertEqual('aBc', cistr('ABC'))
#        self.assertEqual(str(cistr('ABC')), 'ABC')
#
#        d = {cistr('one'): 1, cistr('two'): 2, cistr('tHree'): 3}
#        self.assertEqual(d[cistr('one')], 1)
#        self.assertEqual(d[cistr('tWo')], 2)
#        self.assertEqual(d[cistr('THrEE')], 3)
#        self.assertIn(cistr('ONe'), d)
#        self.assertEqual(d.get(cistr('thrEE')), 3)
#
    def test_classic_comparisons(self):
        # Testing classic comparisons...
        class classic:
            pass

        for base in (classic, int, object):
            class C(base):
                def __init__(self, value):
                    self.value = int(value)
                def __eq__(self, other):
                    if isinstance(other, C):
                        return self.value == other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value == other
                    return NotImplemented
                def __ne__(self, other):
                    if isinstance(other, C):
                        return self.value != other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value != other
                    return NotImplemented
                def __lt__(self, other):
                    if isinstance(other, C):
                        return self.value < other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value < other
                    return NotImplemented
                def __le__(self, other):
                    if isinstance(other, C):
                        return self.value <= other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value <= other
                    return NotImplemented
                def __gt__(self, other):
                    if isinstance(other, C):
                        return self.value > other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value > other
                    return NotImplemented
                def __ge__(self, other):
                    if isinstance(other, C):
                        return self.value >= other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value >= other
                    return NotImplemented

            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            for x in 1, 2, 3:
                for y in 1, 2, 3:
                    locals = {'c':c, 'x':x, 'y':y}                              ###
                    for op in "<", "<=", "==", "!=", ">", ">=":
#                        self.assertEqual(eval("c[x] %s c[y]" % op),
#                                     eval("x %s y" % op),
                        self.assertEqual(eval("c[x] %s c[y]" % op, locals),     ###
                                     eval("x %s y" % op, locals),               ###
                                     "x=%d, y=%d" % (x, y))
#                        self.assertEqual(eval("c[x] %s y" % op),
#                                     eval("x %s y" % op),
                        self.assertEqual(eval("c[x] %s y" % op, locals),        ###
                                     eval("x %s y" % op, locals),               ###
                                     "x=%d, y=%d" % (x, y))
#                        self.assertEqual(eval("x %s c[y]" % op),
#                                     eval("x %s y" % op),
#                                     "x=%d, y=%d" % (x, y))

    def test_rich_comparisons(self):
        # Testing rich comparisons...
        class Z(complex):
            pass
        z = Z(1)
        self.assertEqual(z, 1+0j)
#        self.assertEqual(1+0j, z)
        class ZZ(complex):
            def __eq__(self, other):
                try:
                    return abs(self - other) <= 1e-6
                except:
                    return NotImplemented
        zz = ZZ(1.0000003)
        self.assertEqual(zz, 1+0j)
#        self.assertEqual(1+0j, zz)

        class classic:
            pass
#        for base in (classic, int, object, list):
        for base in (classic, int, object):                                     ###
            class C(base):
                def __init__(self, value):
                    self.value = int(value)
                def __cmp__(self_, other):
                    self.fail("shouldn't call __cmp__")
                def __eq__(self, other):
                    if isinstance(other, C):
                        return self.value == other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value == other
                    return NotImplemented
                def __ne__(self, other):
                    if isinstance(other, C):
                        return self.value != other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value != other
                    return NotImplemented
                def __lt__(self, other):
                    if isinstance(other, C):
                        return self.value < other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value < other
                    return NotImplemented
                def __le__(self, other):
                    if isinstance(other, C):
                        return self.value <= other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value <= other
                    return NotImplemented
                def __gt__(self, other):
                    if isinstance(other, C):
                        return self.value > other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value > other
                    return NotImplemented
                def __ge__(self, other):
                    if isinstance(other, C):
                        return self.value >= other.value
                    if isinstance(other, int) or isinstance(other, int):
                        return self.value >= other
                    return NotImplemented
            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            for x in 1, 2, 3:
                for y in 1, 2, 3:
                    locals = {'c':c, 'x':x, 'y':y}                              ###
                    for op in "<", "<=", "==", "!=", ">", ">=":
#                        self.assertEqual(eval("c[x] %s c[y]" % op),
#                                         eval("x %s y" % op),
                        self.assertEqual(eval("c[x] %s c[y]" % op, locals),     ###
                                         eval("x %s y" % op, locals),           ###
                                         "x=%d, y=%d" % (x, y))
#                        self.assertEqual(eval("c[x] %s y" % op),
#                                         eval("x %s y" % op),
                        self.assertEqual(eval("c[x] %s y" % op, locals),        ###
                                         eval("x %s y" % op, locals),           ###
                                         "x=%d, y=%d" % (x, y))
#                        self.assertEqual(eval("x %s c[y]" % op),
#                                         eval("x %s y" % op),
#                                         "x=%d, y=%d" % (x, y))

#    def test_descrdoc(self):
#        # Testing descriptor doc strings...
#        from _io import FileIO
#        def check(descr, what):
#            self.assertEqual(descr.__doc__, what)
#        check(FileIO.closed, "True if the file is closed") # getset descriptor
#        check(complex.real, "the real part of a complex number") # member descriptor
#
#    def test_doc_descriptor(self):
#        # Testing __doc__ descriptor...
#        # SF bug 542984
#        class DocDescr(object):
#            def __get__(self, object, otype):
#                if object:
#                    object = object.__class__.__name__ + ' instance'
#                if otype:
#                    otype = otype.__name__
#                return 'object=%s; type=%s' % (object, otype)
#        class OldClass:
#            __doc__ = DocDescr()
#        class NewClass(object):
#            __doc__ = DocDescr()
#        self.assertEqual(OldClass.__doc__, 'object=None; type=OldClass')
#        self.assertEqual(OldClass().__doc__, 'object=OldClass instance; type=OldClass')
#        self.assertEqual(NewClass.__doc__, 'object=None; type=NewClass')
#        self.assertEqual(NewClass().__doc__, 'object=NewClass instance; type=NewClass')
#
#    def test_set_class(self):
#        # Testing __class__ assignment...
#        class C(object): pass
#        class D(object): pass
#        class E(object): pass
#        class F(D, E): pass
#        for cls in C, D, E, F:
#            for cls2 in C, D, E, F:
#                x = cls()
#                x.__class__ = cls2
#                self.assertIs(x.__class__, cls2)
#                x.__class__ = cls
#                self.assertIs(x.__class__, cls)
#        def cant(x, C):
#            try:
#                x.__class__ = C
#            except TypeError:
#                pass
#            else:
#                self.fail("shouldn't allow %r.__class__ = %r" % (x, C))
#            try:
#                delattr(x, "__class__")
#            except (TypeError, AttributeError):
#                pass
#            else:
#                self.fail("shouldn't allow del %r.__class__" % x)
#        cant(C(), list)
#        cant(list(), C)
#        cant(C(), 1)
#        cant(C(), object)
#        cant(object(), list)
#        cant(list(), object)
#        class Int(int): __slots__ = []
#        cant(2, Int)
#        cant(Int(), int)
#        cant(True, int)
#        cant(2, bool)
#        o = object()
#        cant(o, type(1))
#        cant(o, type(None))
#        del o
#        class G(object):
#            __slots__ = ["a", "b"]
#        class H(object):
#            __slots__ = ["b", "a"]
#        class I(object):
#            __slots__ = ["a", "b"]
#        class J(object):
#            __slots__ = ["c", "b"]
#        class K(object):
#            __slots__ = ["a", "b", "d"]
#        class L(H):
#            __slots__ = ["e"]
#        class M(I):
#            __slots__ = ["e"]
#        class N(J):
#            __slots__ = ["__weakref__"]
#        class P(J):
#            __slots__ = ["__dict__"]
#        class Q(J):
#            pass
#        class R(J):
#            __slots__ = ["__dict__", "__weakref__"]
#
#        for cls, cls2 in ((G, H), (G, I), (I, H), (Q, R), (R, Q)):
#            x = cls()
#            x.a = 1
#            x.__class__ = cls2
#            self.assertIs(x.__class__, cls2,
#                   "assigning %r as __class__ for %r silently failed" % (cls2, x))
#            self.assertEqual(x.a, 1)
#            x.__class__ = cls
#            self.assertIs(x.__class__, cls,
#                   "assigning %r as __class__ for %r silently failed" % (cls, x))
#            self.assertEqual(x.a, 1)
#        for cls in G, J, K, L, M, N, P, R, list, Int:
#            for cls2 in G, J, K, L, M, N, P, R, list, Int:
#                if cls is cls2:
#                    continue
#                cant(cls(), cls2)
#
#        # Issue5283: when __class__ changes in __del__, the wrong
#        # type gets DECREF'd.
#        class O(object):
#            pass
#        class A(object):
#            def __del__(self):
#                self.__class__ = O
#        l = [A() for x in range(100)]
#        del l
#
#    def test_set_dict(self):
#        # Testing __dict__ assignment...
#        class C(object): pass
#        a = C()
#        a.__dict__ = {'b': 1}
#        self.assertEqual(a.b, 1)
#        def cant(x, dict):
#            try:
#                x.__dict__ = dict
#            except (AttributeError, TypeError):
#                pass
#            else:
#                self.fail("shouldn't allow %r.__dict__ = %r" % (x, dict))
#        cant(a, None)
#        cant(a, [])
#        cant(a, 1)
#        del a.__dict__ # Deleting __dict__ is allowed
#
#        class Base(object):
#            pass
#        def verify_dict_readonly(x):
#            """
#            x has to be an instance of a class inheriting from Base.
#            """
#            cant(x, {})
#            try:
#                del x.__dict__
#            except (AttributeError, TypeError):
#                pass
#            else:
#                self.fail("shouldn't allow del %r.__dict__" % x)
#            dict_descr = Base.__dict__["__dict__"]
#            try:
#                dict_descr.__set__(x, {})
#            except (AttributeError, TypeError):
#                pass
#            else:
#                self.fail("dict_descr allowed access to %r's dict" % x)
#
#        # Classes don't allow __dict__ assignment and have readonly dicts
#        class Meta1(type, Base):
#            pass
#        class Meta2(Base, type):
#            pass
#        class D(object, metaclass=Meta1):
#            pass
#        class E(object, metaclass=Meta2):
#            pass
#        for cls in C, D, E:
#            verify_dict_readonly(cls)
#            class_dict = cls.__dict__
#            try:
#                class_dict["spam"] = "eggs"
#            except TypeError:
#                pass
#            else:
#                self.fail("%r's __dict__ can be modified" % cls)
#
#        # Modules also disallow __dict__ assignment
#        class Module1(types.ModuleType, Base):
#            pass
#        class Module2(Base, types.ModuleType):
#            pass
#        for ModuleType in Module1, Module2:
#            mod = ModuleType("spam")
#            verify_dict_readonly(mod)
#            mod.__dict__["spam"] = "eggs"
#
#        # Exception's __dict__ can be replaced, but not deleted
#        # (at least not any more than regular exception's __dict__ can
#        # be deleted; on CPython it is not the case, whereas on PyPy they
#        # can, just like any other new-style instance's __dict__.)
#        def can_delete_dict(e):
#            try:
#                del e.__dict__
#            except (TypeError, AttributeError):
#                return False
#            else:
#                return True
#        class Exception1(Exception, Base):
#            pass
#        class Exception2(Base, Exception):
#            pass
#        for ExceptionType in Exception, Exception1, Exception2:
#            e = ExceptionType()
#            e.__dict__ = {"a": 1}
#            self.assertEqual(e.a, 1)
#            self.assertEqual(can_delete_dict(e), can_delete_dict(ValueError()))
#
#    def test_binary_operator_override(self):
#        # Testing overrides of binary operations...
#        class I(int):
#            def __repr__(self):
#                return "I(%r)" % int(self)
#            def __add__(self, other):
#                return I(int(self) + int(other))
#            __radd__ = __add__
#            def __pow__(self, other, mod=None):
#                if mod is None:
#                    return I(pow(int(self), int(other)))
#                else:
#                    return I(pow(int(self), int(other), int(mod)))
#            def __rpow__(self, other, mod=None):
#                if mod is None:
#                    return I(pow(int(other), int(self), mod))
#                else:
#                    return I(pow(int(other), int(self), int(mod)))
#
#        self.assertEqual(repr(I(1) + I(2)), "I(3)")
#        self.assertEqual(repr(I(1) + 2), "I(3)")
#        self.assertEqual(repr(1 + I(2)), "I(3)")
#        self.assertEqual(repr(I(2) ** I(3)), "I(8)")
#        self.assertEqual(repr(2 ** I(3)), "I(8)")
#        self.assertEqual(repr(I(2) ** 3), "I(8)")
#        self.assertEqual(repr(pow(I(2), I(3), I(5))), "I(3)")
#        class S(str):
#            def __eq__(self, other):
#                return self.lower() == other.lower()
#
    def test_subclass_propagation(self):
        # Testing propagation of slot functions to subclasses...
        class A(object):
            pass
        class B(A):
            pass
        class C(A):
            pass
        class D(B, C):
            pass
        d = D()
        orig_hash = hash(d) # related to id(d) in platform-dependent ways
        A.__hash__ = lambda self: 42
        self.assertEqual(hash(d), 42)
        C.__hash__ = lambda self: 314
#        self.assertEqual(hash(d), 314)
        B.__hash__ = lambda self: 144
        self.assertEqual(hash(d), 144)
        D.__hash__ = lambda self: 100
        self.assertEqual(hash(d), 100)
        D.__hash__ = None
        self.assertRaises(TypeError, hash, d)
        del D.__hash__
        self.assertEqual(hash(d), 144)
        B.__hash__ = None
        self.assertRaises(TypeError, hash, d)
        del B.__hash__
#        self.assertEqual(hash(d), 314)
        C.__hash__ = None
#        self.assertRaises(TypeError, hash, d)
        del C.__hash__
        self.assertEqual(hash(d), 42)
        A.__hash__ = None
        self.assertRaises(TypeError, hash, d)
        del A.__hash__
        self.assertEqual(hash(d), orig_hash)
        d.foo = 42
        d.bar = 42
        self.assertEqual(d.foo, 42)
        self.assertEqual(d.bar, 42)
#        def __getattribute__(self, name):
#            if name == "foo":
#                return 24
#            return object.__getattribute__(self, name)
#        A.__getattribute__ = __getattribute__
#        self.assertEqual(d.foo, 24)
#        self.assertEqual(d.bar, 42)
#        def __getattr__(self, name):
#            if name in ("spam", "foo", "bar"):
#                return "hello"
#            raise AttributeError(name)
#        B.__getattr__ = __getattr__
#        self.assertEqual(d.spam, "hello")
#        self.assertEqual(d.foo, 24)
#        self.assertEqual(d.bar, 42)
#        del A.__getattribute__
#        self.assertEqual(d.foo, 42)
#        del d.foo
#        self.assertEqual(d.foo, "hello")
#        self.assertEqual(d.bar, 42)
#        del B.__getattr__
#        try:
#            d.foo
#        except AttributeError:
#            pass
#        else:
#            self.fail("d.foo should be undefined now")
#
#        # Test a nasty bug in recurse_down_subclasses()
#        class A(object):
#            pass
#        class B(A):
#            pass
#        del B
#        support.gc_collect()
#        A.__setitem__ = lambda *a: None # crash

#    def test_buffer_inheritance(self):
#        # Testing that buffer interface is inherited ...
#
#        import binascii
#        # SF bug [#470040] ParseTuple t# vs subclasses.
#
#        class MyBytes(bytes):
#            pass
#        base = b'abc'
#        m = MyBytes(base)
#        # b2a_hex uses the buffer interface to get its argument's value, via
#        # PyArg_ParseTuple 't#' code.
#        self.assertEqual(binascii.b2a_hex(m), binascii.b2a_hex(base))
#
#        class MyInt(int):
#            pass
#        m = MyInt(42)
#        try:
#            binascii.b2a_hex(m)
#            self.fail('subclass of int should not have a buffer interface')
#        except TypeError:
#            pass
#
