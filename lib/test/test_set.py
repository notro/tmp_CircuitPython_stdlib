import unittest
from test import support
#import gc
#import weakref
import operator
import copy
#import pickle
#from random import randrange, shuffle
from random import randrange                                                    ###
import sys
#import warnings
import collections
#import collections.abc

class PassThru(Exception):
    pass

def check_pass_thru():
    raise PassThru
    yield 1

class BadCmp:
    def __hash__(self):
        return 1
    def __eq__(self, other):
        raise RuntimeError

class ReprWrapper:
    'Used to test self-referential repr() calls'
    def __repr__(self):
        return repr(self.value)

class HashCountingInt(int):
    'int-like object that counts the number of times __hash__ is called'
    def __init__(self, *args):
        self.hash_count = 0
    def __hash__(self):
        self.hash_count += 1
        return int.__hash__(self)

class TestJointOps:
    # Tests common to both set and frozenset

    def setUp(self):
        self.word = word = 'simsalabim'
        self.otherword = 'madagascar'
        self.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.s = self.thetype(word)
        self.d = dict.fromkeys(word)

    def test_new_or_init(self):
        self.assertRaises(TypeError, self.thetype, [], 2)
#        self.assertRaises(TypeError, set().__init__, a=1)

    def test_uniquification(self):
        actual = sorted(self.s)
        expected = sorted(self.d)
        self.assertEqual(actual, expected)
        self.assertRaises(PassThru, self.thetype, check_pass_thru())
        self.assertRaises(TypeError, self.thetype, [[]])

    def test_len(self):
        self.assertEqual(len(self.s), len(self.d))

#    def test_contains(self):
#        for c in self.letters:
#            self.assertEqual(c in self.s, c in self.d)
#        self.assertRaises(TypeError, self.s.__contains__, [[]])
#        s = self.thetype([frozenset(self.letters)])
#        self.assertIn(self.thetype(self.letters), s)
#
    def test_union(self):
        u = self.s.union(self.otherword)
        for c in self.letters:
            self.assertEqual(c in u, c in self.d or c in self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(u), self.basetype)
        self.assertRaises(PassThru, self.s.union, check_pass_thru())
        self.assertRaises(TypeError, self.s.union, [[]])
        for C in set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').union(C('cdc')), set('abcd'))
            self.assertEqual(self.thetype('abcba').union(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').union(C('ccb')), set('abc'))
            self.assertEqual(self.thetype('abcba').union(C('ef')), set('abcef'))
#            self.assertEqual(self.thetype('abcba').union(C('ef'), C('fg')), set('abcefg'))
#
#        # Issue #6573
#        x = self.thetype()
#        self.assertEqual(x.union(set([1]), x, set([2])), self.thetype([1, 2]))

    def test_or(self):
        i = self.s.union(self.otherword)
        self.assertEqual(self.s | set(self.otherword), i)
        self.assertEqual(self.s | frozenset(self.otherword), i)
        try:
            self.s | self.otherword
        except TypeError:
            pass
        else:
            self.fail("s|t did not screen-out general iterables")

    def test_intersection(self):
        i = self.s.intersection(self.otherword)
        for c in self.letters:
            self.assertEqual(c in i, c in self.d and c in self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
#        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.intersection, check_pass_thru())
        for C in set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').intersection(C('cdc')), set('cc'))
            self.assertEqual(self.thetype('abcba').intersection(C('efgfe')), set(''))
            self.assertEqual(self.thetype('abcba').intersection(C('ccb')), set('bc'))
            self.assertEqual(self.thetype('abcba').intersection(C('ef')), set(''))
#            self.assertEqual(self.thetype('abcba').intersection(C('cbcf'), C('bag')), set('b'))
#        s = self.thetype('abcba')
#        z = s.intersection()
#        if self.thetype == frozenset():
#            self.assertEqual(id(s), id(z))
#        else:
#            self.assertNotEqual(id(s), id(z))

    def test_isdisjoint(self):
        def f(s1, s2):
            'Pure python equivalent of isdisjoint()'
            return not set(s1).intersection(s2)
        for larg in '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
            s1 = self.thetype(larg)
            for rarg in '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
                for C in set, frozenset, dict.fromkeys, str, list, tuple:
                    s2 = C(rarg)
                    actual = s1.isdisjoint(s2)
                    expected = f(s1, s2)
                    self.assertEqual(actual, expected)
                    self.assertTrue(actual is True or actual is False)

    def test_and(self):
        i = self.s.intersection(self.otherword)
        self.assertEqual(self.s & set(self.otherword), i)
        self.assertEqual(self.s & frozenset(self.otherword), i)
        try:
            self.s & self.otherword
        except TypeError:
            pass
        else:
            self.fail("s&t did not screen-out general iterables")

    def test_difference(self):
        i = self.s.difference(self.otherword)
        for c in self.letters:
            self.assertEqual(c in i, c in self.d and c not in self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference, [[]])
        for C in set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').difference(C('cdc')), set('ab'))
            self.assertEqual(self.thetype('abcba').difference(C('efgfe')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').difference(C('ef')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('a'), C('b')), set('c'))

    def test_sub(self):
        i = self.s.difference(self.otherword)
        self.assertEqual(self.s - set(self.otherword), i)
        self.assertEqual(self.s - frozenset(self.otherword), i)
        try:
            self.s - self.otherword
        except TypeError:
            pass
        else:
            self.fail("s-t did not screen-out general iterables")

    def test_symmetric_difference(self):
        i = self.s.symmetric_difference(self.otherword)
#        for c in self.letters:
#            self.assertEqual(c in i, (c in self.d) ^ (c in self.otherword))
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.symmetric_difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.symmetric_difference, [[]])
#        for C in set, frozenset, dict.fromkeys, str, list, tuple:
        for C in set, frozenset, dict.fromkeys:                                 ###
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('cdc')), set('abd'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ef')), set('abcef'))

#    def test_xor(self):
#        i = self.s.symmetric_difference(self.otherword)
#        self.assertEqual(self.s ^ set(self.otherword), i)
#        self.assertEqual(self.s ^ frozenset(self.otherword), i)
#        try:
#            self.s ^ self.otherword
#        except TypeError:
#            pass
#        else:
#            self.fail("s^t did not screen-out general iterables")
#
    def test_equality(self):
        self.assertEqual(self.s, set(self.word))
        self.assertEqual(self.s, frozenset(self.word))
        self.assertEqual(self.s == self.word, False)
        self.assertNotEqual(self.s, set(self.otherword))
        self.assertNotEqual(self.s, frozenset(self.otherword))
        self.assertEqual(self.s != self.word, True)

    def test_setOfFrozensets(self):
        t = map(frozenset, ['abcdef', 'bcd', 'bdcb', 'fed', 'fedccba'])
        s = self.thetype(t)
        self.assertEqual(len(s), 3)

    def test_sub_and_super(self):
        p, q, r = map(self.thetype, ['ab', 'abcde', 'def'])
        self.assertTrue(p < q)
        self.assertTrue(p <= q)
        self.assertTrue(q <= q)
        self.assertTrue(q > p)
        self.assertTrue(q >= p)
        self.assertFalse(q < r)
        self.assertFalse(q <= r)
        self.assertFalse(q > r)
        self.assertFalse(q >= r)
        self.assertTrue(set('a').issubset('abc'))
        self.assertTrue(set('abc').issuperset('a'))
        self.assertFalse(set('a').issubset('cbs'))
        self.assertFalse(set('cbs').issuperset('a'))

#    def test_pickling(self):
#        for i in range(pickle.HIGHEST_PROTOCOL + 1):
#            p = pickle.dumps(self.s, i)
#            dup = pickle.loads(p)
#            self.assertEqual(self.s, dup, "%s != %s" % (self.s, dup))
#            if type(self.s) not in (set, frozenset):
#                self.s.x = 10
#                p = pickle.dumps(self.s, i)
#                dup = pickle.loads(p)
#                self.assertEqual(self.s.x, dup.x)
#
#    def test_iterator_pickling(self):
#        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
#            itorg = iter(self.s)
#            data = self.thetype(self.s)
#            d = pickle.dumps(itorg, proto)
#            it = pickle.loads(d)
#            # Set iterators unpickle as list iterators due to the
#            # undefined order of set items.
#            # self.assertEqual(type(itorg), type(it))
#            self.assertIsInstance(it, collections.abc.Iterator)
#            self.assertEqual(self.thetype(it), data)
#
#            it = pickle.loads(d)
#            try:
#                drop = next(it)
#            except StopIteration:
#                continue
#            d = pickle.dumps(it, proto)
#            it = pickle.loads(d)
#            self.assertEqual(self.thetype(it), data - self.thetype((drop,)))
#
#    def test_deepcopy(self):
#        class Tracer:
#            def __init__(self, value):
#                self.value = value
#            def __hash__(self):
#                return self.value
#            def __deepcopy__(self, memo=None):
#                return Tracer(self.value + 1)
#        t = Tracer(10)
#        s = self.thetype([t])
#        dup = copy.deepcopy(s)
#        self.assertNotEqual(id(s), id(dup))
#        for elem in dup:
#            newt = elem
#        self.assertNotEqual(id(t), id(newt))
#        self.assertEqual(t.value + 1, newt.value)
#
#    def test_gc(self):
#        # Create a nest of cycles to exercise overall ref count check
#        class A:
#            pass
#        s = set(A() for i in range(1000))
#        for elem in s:
#            elem.cycle = s
#            elem.sub = elem
#            elem.set = set([elem])
#
    def test_subclass_with_custom_hash(self):
        # Bug #1257731
        class H(self.thetype):
            def __hash__(self):
                return int(id(self) & 0x7fffffff)
        s=H()
        f=set()
        f.add(s)
        self.assertIn(s, f)
        f.remove(s)
        f.add(s)
        f.discard(s)

    def test_badcmp(self):
        s = self.thetype([BadCmp()])
        # Detect comparison errors during insertion and lookup
        self.assertRaises(RuntimeError, self.thetype, [BadCmp(), BadCmp()])
        self.assertRaises(RuntimeError, s.__contains__, BadCmp())
        # Detect errors during mutating operations
        if hasattr(s, 'add'):
            self.assertRaises(RuntimeError, s.add, BadCmp())
            self.assertRaises(RuntimeError, s.discard, BadCmp())
            self.assertRaises(RuntimeError, s.remove, BadCmp())

#    def test_cyclical_repr(self):
#        w = ReprWrapper()
#        s = self.thetype([w])
#        w.value = s
#        if self.thetype == set:
#            self.assertEqual(repr(s), '{set(...)}')
#        else:
#            name = repr(s).partition('(')[0]    # strip class name
#            self.assertEqual(repr(s), '%s({%s(...)})' % (name, name))
#
#    def test_cyclical_print(self):
#        w = ReprWrapper()
#        s = self.thetype([w])
#        w.value = s
#        fo = open(support.TESTFN, "w")
#        try:
#            fo.write(str(s))
#            fo.close()
#            fo = open(support.TESTFN, "r")
#            self.assertEqual(fo.read(), repr(s))
#        finally:
#            fo.close()
#            support.unlink(support.TESTFN)
#
#    def test_do_not_rehash_dict_keys(self):
#        n = 10
#        d = dict.fromkeys(map(HashCountingInt, range(n)))
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        s = self.thetype(d)
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        s.difference(d)
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        if hasattr(s, 'symmetric_difference_update'):
#            s.symmetric_difference_update(d)
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        d2 = dict.fromkeys(set(d))
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        d3 = dict.fromkeys(frozenset(d))
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        d3 = dict.fromkeys(frozenset(d), 123)
#        self.assertEqual(sum(elem.hash_count for elem in d), n)
#        self.assertEqual(d3, dict.fromkeys(d, 123))
#
#    def test_container_iterator(self):
#        # Bug #3680: tp_traverse was not implemented for set iterator object
#        class C(object):
#            pass
#        obj = C()
#        ref = weakref.ref(obj)
#        container = set([obj, 1])
#        obj.x = iter(container)
#        del obj, container
#        gc.collect()
#        self.assertTrue(ref() is None, "Cycle was not collected")
#
class TestSet(TestJointOps, unittest.TestCase):
    thetype = set
    basetype = set

#    def test_init(self):
#        s = self.thetype()
#        s.__init__(self.word)
#        self.assertEqual(s, set(self.word))
#        s.__init__(self.otherword)
#        self.assertEqual(s, set(self.otherword))
#        self.assertRaises(TypeError, s.__init__, s, 2);
#        self.assertRaises(TypeError, s.__init__, 1);
#
    def test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertNotEqual(id(s), id(t))

    def test_set_literal(self):
        s = set([1,2,3])
        t = {1,2,3}
        self.assertEqual(s, t)

    def test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    def test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, set())
        self.assertEqual(len(self.s), 0)

    def test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))
        self.assertEqual(type(dup), self.basetype)

    def test_add(self):
        self.s.add('Q')
        self.assertIn('Q', self.s)
        dup = self.s.copy()
        self.s.add('Q')
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])

    def test_remove(self):
        self.s.remove('a')
        self.assertNotIn('a', self.s)
        self.assertRaises(KeyError, self.s.remove, 'Q')
        self.assertRaises(TypeError, self.s.remove, [])
        s = self.thetype([frozenset(self.word)])
#        self.assertIn(self.thetype(self.word), s)
#        s.remove(self.thetype(self.word))
#        self.assertNotIn(self.thetype(self.word), s)
#        self.assertRaises(KeyError, self.s.remove, self.thetype(self.word))

    def test_remove_keyerror_unpacking(self):
        # bug:  www.python.org/sf/1576657
        for v1 in ['Q', (1,)]:
            try:
                self.s.remove(v1)
            except KeyError as e:
                v2 = e.args[0]
                self.assertEqual(v1, v2)
            else:
                self.fail()

#    def test_remove_keyerror_set(self):
#        key = self.thetype([3, 4])
#        try:
#            self.s.remove(key)
#        except KeyError as e:
#            self.assertTrue(e.args[0] is key,
#                         "KeyError should be {0}, not {1}".format(key,
#                                                                  e.args[0]))
#        else:
#            self.fail()
#
#    def test_discard(self):
#        self.s.discard('a')
#        self.assertNotIn('a', self.s)
#        self.s.discard('Q')
#        self.assertRaises(TypeError, self.s.discard, [])
#        s = self.thetype([frozenset(self.word)])
#        self.assertIn(self.thetype(self.word), s)
#        s.discard(self.thetype(self.word))
#        self.assertNotIn(self.thetype(self.word), s)
#        s.discard(self.thetype(self.word))
#
    def test_pop(self):
        for i in range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    def test_update(self):
        retval = self.s.update(self.otherword)
        self.assertEqual(retval, None)
        for c in (self.word + self.otherword):
            self.assertIn(c, self.s)
        self.assertRaises(PassThru, self.s.update, check_pass_thru())
        self.assertRaises(TypeError, self.s.update, [[]])
        for p, q in (('cdc', 'abcd'), ('efgfe', 'abcefg'), ('ccb', 'abc'), ('ef', 'abcef')):
            for C in set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p)), None)
                self.assertEqual(s, set(q))
        for p in ('cdc', 'efgfe', 'ccb', 'ef', 'abcda'):
            q = 'ahi'
            for C in set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p), C(q)), None)
                self.assertEqual(s, set(s) | set(p) | set(q))

    def test_ior(self):
        self.s |= set(self.otherword)
        for c in (self.word + self.otherword):
            self.assertIn(c, self.s)

    def test_intersection_update(self):
        retval = self.s.intersection_update(self.otherword)
        self.assertEqual(retval, None)
        for c in (self.word + self.otherword):
            if c in self.otherword and c in self.word:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.intersection_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.intersection_update, [[]])
        for p, q in (('cdc', 'c'), ('efgfe', ''), ('ccb', 'bc'), ('ef', '')):
            for C in set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.intersection_update(C(p)), None)
                self.assertEqual(s, set(q))
                ss = 'abcba'
                s = self.thetype(ss)
                t = 'cbc'
#                self.assertEqual(s.intersection_update(C(p), C(t)), None)
#                self.assertEqual(s, set('abcba')&set(p)&set(t))

    def test_iand(self):
        self.s &= set(self.otherword)
        for c in (self.word + self.otherword):
            if c in self.otherword and c in self.word:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

    def test_difference_update(self):
        retval = self.s.difference_update(self.otherword)
        self.assertEqual(retval, None)
        for c in (self.word + self.otherword):
            if c in self.word and c not in self.otherword:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.difference_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference_update, [[]])
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        for p, q in (('cdc', 'ab'), ('efgfe', 'abc'), ('ccb', 'a'), ('ef', 'abc')):
            for C in set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.difference_update(C(p)), None)
                self.assertEqual(s, set(q))

                s = self.thetype('abcdefghih')
                s.difference_update()
                self.assertEqual(s, self.thetype('abcdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('aba'))
                self.assertEqual(s, self.thetype('cdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('cdc'), C('aba'))
                self.assertEqual(s, self.thetype('efghih'))

    def test_isub(self):
        self.s -= set(self.otherword)
        for c in (self.word + self.otherword):
            if c in self.word and c not in self.otherword:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

#    def test_symmetric_difference_update(self):
#        retval = self.s.symmetric_difference_update(self.otherword)
#        self.assertEqual(retval, None)
#        for c in (self.word + self.otherword):
#            if (c in self.word) ^ (c in self.otherword):
#                self.assertIn(c, self.s)
#            else:
#                self.assertNotIn(c, self.s)
#        self.assertRaises(PassThru, self.s.symmetric_difference_update, check_pass_thru())
#        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
#        for p, q in (('cdc', 'abd'), ('efgfe', 'abcefg'), ('ccb', 'a'), ('ef', 'abcef')):
#            for C in set, frozenset, dict.fromkeys, str, list, tuple:
#                s = self.thetype('abcba')
#                self.assertEqual(s.symmetric_difference_update(C(p)), None)
#                self.assertEqual(s, set(q))
#
    def test_ixor(self):
        self.s ^= set(self.otherword)
        for c in (self.word + self.otherword):
            if (c in self.word) ^ (c in self.otherword):
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

    def test_inplace_on_self(self):
        t = self.s.copy()
        t |= t
        self.assertEqual(t, self.s)
        t &= t
        self.assertEqual(t, self.s)
        t -= t
        self.assertEqual(t, self.thetype())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, self.thetype())

#    def test_weakref(self):
#        s = self.thetype('gallahad')
#        p = weakref.proxy(s)
#        self.assertEqual(str(p), str(s))
#        s = None
#        self.assertRaises(ReferenceError, str, p)
#
#    def test_rich_compare(self):
#        class TestRichSetCompare:
#            def __gt__(self, some_set):
#                self.gt_called = True
#                return False
#            def __lt__(self, some_set):
#                self.lt_called = True
#                return False
#            def __ge__(self, some_set):
#                self.ge_called = True
#                return False
#            def __le__(self, some_set):
#                self.le_called = True
#                return False
#
#        # This first tries the builtin rich set comparison, which doesn't know
#        # how to handle the custom object. Upon returning NotImplemented, the
#        # corresponding comparison on the right object is invoked.
#        myset = {1, 2, 3}
#
#        myobj = TestRichSetCompare()
#        myset < myobj
#        self.assertTrue(myobj.gt_called)
#
#        myobj = TestRichSetCompare()
#        myset > myobj
#        self.assertTrue(myobj.lt_called)
#
#        myobj = TestRichSetCompare()
#        myset <= myobj
#        self.assertTrue(myobj.ge_called)
#
#        myobj = TestRichSetCompare()
#        myset >= myobj
#        self.assertTrue(myobj.le_called)
#
#    @unittest.skipUnless(hasattr(set, "test_c_api"),
#                         'C API test only available in a debug build')
#    def test_c_api(self):
#        self.assertEqual(set().test_c_api(), True)
#
#class SetSubclass(set):
#    pass
#
#class TestSetSubclass(TestSet):
#    thetype = SetSubclass
#    basetype = set
#
#class SetSubclassWithKeywordArgs(set):
#    def __init__(self, iterable=[], newarg=None):
#        set.__init__(self, iterable)
#
#class TestSetSubclassWithKeywordArgs(TestSet):
#
#    def test_keywords_in_subclass(self):
#        'SF bug #1486663 -- this used to erroneously raise a TypeError'
#        SetSubclassWithKeywordArgs(newarg=1)
#
class TestFrozenSet(TestJointOps, unittest.TestCase):
    thetype = frozenset
    basetype = frozenset

#    def test_init(self):
#        s = self.thetype(self.word)
#        s.__init__(self.otherword)
#        self.assertEqual(s, set(self.word))
#
#    def test_singleton_empty_frozenset(self):
#        f = frozenset()
#        efs = [frozenset(), frozenset([]), frozenset(()), frozenset(''),
#               frozenset(), frozenset([]), frozenset(()), frozenset(''),
#               frozenset(range(0)), frozenset(frozenset()),
#               frozenset(f), f]
#        # All of the empty frozensets should have just one id()
#        self.assertEqual(len(set(map(id, efs))), 1)
#
#    def test_constructor_identity(self):
#        s = self.thetype(range(3))
#        t = self.thetype(s)
#        self.assertEqual(id(s), id(t))
#
#    def test_hash(self):
#        self.assertEqual(hash(self.thetype('abcdeb')),
#                         hash(self.thetype('ebecda')))
#
#        # make sure that all permutations give the same hash value
#        n = 100
#        seq = [randrange(n) for i in range(n)]
#        results = set()
#        for i in range(200):
#            shuffle(seq)
#            results.add(hash(self.thetype(seq)))
#        self.assertEqual(len(results), 1)
#
#    def test_copy(self):
#        dup = self.s.copy()
#        self.assertEqual(id(self.s), id(dup))
#
    def test_frozen_as_dictkey(self):
        seq = list(range(10)) + list('abcdefg') + ['apple']
        key1 = self.thetype(seq)
        key2 = self.thetype(reversed(seq))
        self.assertEqual(key1, key2)
        self.assertNotEqual(id(key1), id(key2))
        d = {}
        d[key1] = 42
        self.assertEqual(d[key2], 42)

    def test_hash_caching(self):
        f = self.thetype('abcdcda')
        self.assertEqual(hash(f), hash(f))

#    def test_hash_effectiveness(self):
#        n = 13
#        hashvalues = set()
#        addhashvalue = hashvalues.add
#        elemmasks = [(i+1, 1<<i) for i in range(n)]
#        for i in range(2**n):
#            addhashvalue(hash(frozenset([e for e, m in elemmasks if m&i])))
#        self.assertEqual(len(hashvalues), 2**n)
#
#class FrozenSetSubclass(frozenset):
#    pass
#
#class TestFrozenSetSubclass(TestFrozenSet):
#    thetype = FrozenSetSubclass
#    basetype = frozenset
#
#    def test_constructor_identity(self):
#        s = self.thetype(range(3))
#        t = self.thetype(s)
#        self.assertNotEqual(id(s), id(t))
#
#    def test_copy(self):
#        dup = self.s.copy()
#        self.assertNotEqual(id(self.s), id(dup))
#
#    def test_nested_empty_constructor(self):
#        s = self.thetype()
#        t = self.thetype(s)
#        self.assertEqual(s, t)
#
#    def test_singleton_empty_frozenset(self):
#        Frozenset = self.thetype
#        f = frozenset()
#        F = Frozenset()
#        efs = [Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
#               Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
#               Frozenset(range(0)), Frozenset(Frozenset()),
#               Frozenset(frozenset()), f, F, Frozenset(f), Frozenset(F)]
#        # All empty frozenset subclass instances should have different ids
#        self.assertEqual(len(set(map(id, efs))), len(efs))
#
