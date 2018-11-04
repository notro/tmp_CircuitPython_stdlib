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

#==============================================================================

class TestSubsets:

    case2method = {"<=": "issubset",
                   ">=": "issuperset",
                  }

    reverse = {"==": "==",
               "!=": "!=",
               "<":  ">",
               ">":  "<",
               "<=": ">=",
               ">=": "<=",
              }

    def test_issubset(self):
        x = self.left
        y = self.right
        def locals():                                                           ###
            return {'x':x, 'y':y}                                               ###
        for case in "!=", "==", "<", "<=", ">", ">=":
            expected = case in self.cases
            # Test the binary infix spelling.
            result = eval("x" + case + "y", locals())
            self.assertEqual(result, expected)
            # Test the "friendly" method-name spelling, if one exists.
            if case in TestSubsets.case2method:
                method = getattr(x, TestSubsets.case2method[case])
                result = method(y)
                self.assertEqual(result, expected)

            # Now do the same for the operands reversed.
            rcase = TestSubsets.reverse[case]
            result = eval("y" + rcase + "x", locals())
            self.assertEqual(result, expected)
            if rcase in TestSubsets.case2method:
                method = getattr(y, TestSubsets.case2method[rcase])
                result = method(x)
                self.assertEqual(result, expected)
#------------------------------------------------------------------------------

class TestSubsetEqualEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set()
    name  = "both empty"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

class TestSubsetEqualNonEmpty(TestSubsets, unittest.TestCase):
    left  = set([1, 2])
    right = set([1, 2])
    name  = "equal pair"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

class TestSubsetEmptyNonEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set([1, 2])
    name  = "one empty, one non-empty"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

class TestSubsetPartial(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([1, 2])
    name  = "one a non-empty proper subset of other"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

class TestSubsetNonOverlap(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([2])
    name  = "neither empty, neither contains"
    cases = "!="

#==============================================================================

class TestOnlySetsInBinaryOps:

    def test_eq_ne(self):
        # Unlike the others, this is testing that == and != *are* allowed.
        self.assertEqual(self.other == self.set, False)
        self.assertEqual(self.set == self.other, False)
        self.assertEqual(self.other != self.set, True)
        self.assertEqual(self.set != self.other, True)

    def test_ge_gt_le_lt(self):
        self.assertRaises(TypeError, lambda: self.set < self.other)
        self.assertRaises(TypeError, lambda: self.set <= self.other)
        self.assertRaises(TypeError, lambda: self.set > self.other)
        self.assertRaises(TypeError, lambda: self.set >= self.other)

        self.assertRaises(TypeError, lambda: self.other < self.set)
        self.assertRaises(TypeError, lambda: self.other <= self.set)
        self.assertRaises(TypeError, lambda: self.other > self.set)
        self.assertRaises(TypeError, lambda: self.other >= self.set)

    def test_update_operator(self):
        try:
            self.set |= self.other
        except TypeError:
            pass
        else:
            self.fail("expected TypeError")

    def test_update(self):
        if self.otherIsIterable:
            self.set.update(self.other)
        else:
            self.assertRaises(TypeError, self.set.update, self.other)

    def test_union(self):
        self.assertRaises(TypeError, lambda: self.set | self.other)
        self.assertRaises(TypeError, lambda: self.other | self.set)
        if self.otherIsIterable:
            self.set.union(self.other)
        else:
            self.assertRaises(TypeError, self.set.union, self.other)

    def test_intersection_update_operator(self):
        try:
            self.set &= self.other
        except TypeError:
            pass
        else:
            self.fail("expected TypeError")

    def test_intersection_update(self):
        if self.otherIsIterable:
            self.set.intersection_update(self.other)
        else:
            self.assertRaises(TypeError,
                              self.set.intersection_update,
                              self.other)

    def test_intersection(self):
        self.assertRaises(TypeError, lambda: self.set & self.other)
        self.assertRaises(TypeError, lambda: self.other & self.set)
        if self.otherIsIterable:
            self.set.intersection(self.other)
        else:
            self.assertRaises(TypeError, self.set.intersection, self.other)

    def test_sym_difference_update_operator(self):
        try:
            self.set ^= self.other
        except TypeError:
            pass
        else:
            self.fail("expected TypeError")

    def test_sym_difference_update(self):
        if self.otherIsIterable:
            self.set.symmetric_difference_update(self.other)
        else:
            self.assertRaises(TypeError,
                              self.set.symmetric_difference_update,
                              self.other)

    def test_sym_difference(self):
        self.assertRaises(TypeError, lambda: self.set ^ self.other)
        self.assertRaises(TypeError, lambda: self.other ^ self.set)
        if self.otherIsIterable:
            self.set.symmetric_difference(self.other)
        else:
            self.assertRaises(TypeError, self.set.symmetric_difference, self.other)

    def test_difference_update_operator(self):
        try:
            self.set -= self.other
        except TypeError:
            pass
        else:
            self.fail("expected TypeError")

    def test_difference_update(self):
        if self.otherIsIterable:
            self.set.difference_update(self.other)
        else:
            self.assertRaises(TypeError,
                              self.set.difference_update,
                              self.other)

    def test_difference(self):
        self.assertRaises(TypeError, lambda: self.set - self.other)
        self.assertRaises(TypeError, lambda: self.other - self.set)
        if self.otherIsIterable:
            self.set.difference(self.other)
        else:
            self.assertRaises(TypeError, self.set.difference, self.other)

#------------------------------------------------------------------------------

class TestOnlySetsNumeric(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 19
        self.otherIsIterable = False

#------------------------------------------------------------------------------

class TestOnlySetsDict(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = {1:2, 3:4}
        self.otherIsIterable = True

#------------------------------------------------------------------------------

class TestOnlySetsOperator(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = operator.add
        self.otherIsIterable = False

#------------------------------------------------------------------------------

class TestOnlySetsTuple(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = (2, 4, 6)
        self.otherIsIterable = True

#------------------------------------------------------------------------------

class TestOnlySetsString(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 'abc'
        self.otherIsIterable = True

#------------------------------------------------------------------------------

class TestOnlySetsGenerator(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        def gen():
            for i in range(0, 10, 2):
                yield i
        self.set   = set((1, 2, 3))
        self.other = gen()
        self.otherIsIterable = True

#==============================================================================

class TestCopying:

    def test_copy(self):
        dup = self.set.copy()
        dup_list = sorted(dup, key=repr)
        set_list = sorted(self.set, key=repr)
        self.assertEqual(len(dup_list), len(set_list))
        for i in range(len(dup_list)):
            self.assertTrue(dup_list[i] is set_list[i])

#    def test_deep_copy(self):
#        dup = copy.deepcopy(self.set)
#        ##print type(dup), repr(dup)
#        dup_list = sorted(dup, key=repr)
#        set_list = sorted(self.set, key=repr)
#        self.assertEqual(len(dup_list), len(set_list))
#        for i in range(len(dup_list)):
#            self.assertEqual(dup_list[i], set_list[i])

#------------------------------------------------------------------------------

class TestCopyingEmpty(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set()

#------------------------------------------------------------------------------

class TestCopyingSingleton(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set(["hello"])

#------------------------------------------------------------------------------

class TestCopyingTriple(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set(["zero", 0, None])

#------------------------------------------------------------------------------

class TestCopyingTuple(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set([(1, 2)])

#------------------------------------------------------------------------------

class TestCopyingNested(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set([((1, 2), (3, 4))])

#==============================================================================

class TestIdentities(unittest.TestCase):
    def setUp(self):
        self.a = set('abracadabra')
        self.b = set('alacazam')

    def test_binopsVsSubsets(self):
        a, b = self.a, self.b
        self.assertTrue(a - b < a)
        self.assertTrue(b - a < b)
        self.assertTrue(a & b < a)
        self.assertTrue(a & b < b)
        self.assertTrue(a | b > a)
        self.assertTrue(a | b > b)
        self.assertTrue(a ^ b < a | b)

    def test_commutativity(self):
        a, b = self.a, self.b
        self.assertEqual(a&b, b&a)
        self.assertEqual(a|b, b|a)
        self.assertEqual(a^b, b^a)
        if a != b:
            self.assertNotEqual(a-b, b-a)

    def test_summations(self):
        # check that sums of parts equal the whole
        a, b = self.a, self.b
        self.assertEqual((a-b)|(a&b)|(b-a), a|b)
        self.assertEqual((a&b)|(a^b), a|b)
        self.assertEqual(a|(b-a), a|b)
        self.assertEqual((a-b)|b, a|b)
        self.assertEqual((a-b)|(a&b), a)
        self.assertEqual((b-a)|(a&b), b)
        self.assertEqual((a-b)|(b-a), a^b)

    def test_exclusion(self):
        # check that inverse operations show non-overlap
        a, b, zero = self.a, self.b, set()
        self.assertEqual((a-b)&b, zero)
        self.assertEqual((b-a)&a, zero)
        self.assertEqual((a&b)&(a^b), zero)

# Tests derived from test_itertools.py =======================================

def R(seqn):
    'Regular generator'
    for i in seqn:
        yield i

class G:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        return self.seqn[i]

class I:
    'Sequence using iterator protocol'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class Ig:
    'Sequence using iterator protocol defined with a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        for val in self.seqn:
            yield val

class X:
    'Missing __getitem__ and __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __next__(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class N:
    'Iterator missing __next__()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self

class E:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        3 // 0

class S:
    'Test immediate stop'
    def __init__(self, seqn):
        pass
    def __iter__(self):
        return self
    def __next__(self):
        raise StopIteration

from itertools import chain
def L(seqn):
    'Test multiple tiers of iterators'
    return chain(map(lambda x:x, R(Ig(G(seqn)))))

class TestVariousIteratorArgs(unittest.TestCase):

    def test_constructor(self):
        for cons in (set, frozenset):
#            for s in ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            for s in ("123", "", range(100), ('do', 1.2), range(200,220,5)):    ###
                for g in (G, I, Ig, S, L, R):
                    self.assertEqual(sorted(cons(g(s)), key=repr), sorted(g(s), key=repr))
                self.assertRaises(TypeError, cons , X(s))
                self.assertRaises(TypeError, cons , N(s))
                self.assertRaises(ZeroDivisionError, cons , E(s))

    def test_inline_methods(self):
        s = set('november')
#        for data in ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
        for data in ("123", "", range(100), ('do', 1.2), range(200,220,5), 'december'):  ###
            for meth in (s.union, s.intersection, s.difference, s.symmetric_difference, s.isdisjoint):
                for g in (G, I, Ig, L, R):
                    expected = meth(data)
                    actual = meth(g(data))
                    if isinstance(expected, bool):
                        self.assertEqual(actual, expected)
                    else:
                        self.assertEqual(sorted(actual, key=repr), sorted(expected, key=repr))
                self.assertRaises(TypeError, meth, X(s))
                self.assertRaises(TypeError, meth, N(s))
                self.assertRaises(ZeroDivisionError, meth, E(s))

    def test_inplace_methods(self):
#        for data in ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
        for data in ("123", "", range(100), ('do', 1.2), range(200,220,5), 'december'):  ###
            for methname in ('update', 'intersection_update',
                             'difference_update', 'symmetric_difference_update'):
                for g in (G, I, Ig, S, L, R):
                    s = set('january')
                    t = s.copy()
                    getattr(s, methname)(list(g(data)))
                    getattr(t, methname)(g(data))
                    self.assertEqual(sorted(s, key=repr), sorted(t, key=repr))

                self.assertRaises(TypeError, getattr(set('january'), methname), X(data))
                self.assertRaises(TypeError, getattr(set('january'), methname), N(data))
                self.assertRaises(ZeroDivisionError, getattr(set('january'), methname), E(data))

class bad_eq:
    def __eq__(self, other):
        if be_bad:
            set2.clear()
            raise ZeroDivisionError
        return self is other
    def __hash__(self):
        return 0

class bad_dict_clear:
    def __eq__(self, other):
        if be_bad:
            dict2.clear()
        return self is other
    def __hash__(self):
        return 0

class TestWeirdBugs(unittest.TestCase):
    def test_8420_set_merge(self):
        # This used to segfault
        global be_bad, set2, dict2
        be_bad = False
        set1 = {bad_eq()}
        set2 = {bad_eq() for i in range(75)}
        be_bad = True
        self.assertRaises(ZeroDivisionError, set1.update, set2)

        be_bad = False
        set1 = {bad_dict_clear()}
        dict2 = {bad_dict_clear(): None}
        be_bad = True
        set1.symmetric_difference_update(dict2)

    def test_iter_and_mutate(self):
        # Issue #24581
        s = set(range(100))
        s.clear()
        s.update(range(100))
        si = iter(s)
        s.clear()
        a = list(range(100))
        s.update(range(100))
        list(si)

# Application tests (based on David Eppstein's graph recipes ====================================

def powerset(U):
    """Generates all subsets of a set or sequence U."""
    U = iter(U)
    try:
        x = frozenset([next(U)])
        for S in powerset(U):
            yield S
            yield S | x
    except StopIteration:
        yield frozenset()

def cube(n):
    """Graph of n-dimensional hypercube."""
    singletons = [frozenset([x]) for x in range(n)]
    return dict([(x, frozenset([x^s for s in singletons]))
                 for x in powerset(range(n))])

def linegraph(G):
    """Graph, the vertices of which are edges of G,
    with two vertices being adjacent iff the corresponding
    edges share a vertex."""
    L = {}
    for x in G:
        for y in G[x]:
            nx = [frozenset([x,z]) for z in G[x] if z != y]
            ny = [frozenset([y,z]) for z in G[y] if z != x]
            L[frozenset([x,y])] = frozenset(nx+ny)
    return L

def faces(G):
    'Return a set of faces in G.  Where a face is a set of vertices on that face'
    # currently limited to triangles,squares, and pentagons
    f = set()
    for v1, edges in G.items():
        for v2 in edges:
            for v3 in G[v2]:
                if v1 == v3:
                    continue
                if v1 in G[v3]:
                    f.add(frozenset([v1, v2, v3]))
                else:
                    for v4 in G[v3]:
                        if v4 == v2:
                            continue
                        if v1 in G[v4]:
                            f.add(frozenset([v1, v2, v3, v4]))
                        else:
                            for v5 in G[v4]:
                                if v5 == v3 or v5 == v2:
                                    continue
                                if v1 in G[v5]:
                                    f.add(frozenset([v1, v2, v3, v4, v5]))
    return f


class TestGraphs(unittest.TestCase):

    def test_cube(self):

        g = cube(3)                             # vert --> {v1, v2, v3}
        vertices1 = set(g)
        self.assertEqual(len(vertices1), 8)     # eight vertices
        for edge in g.values():
            self.assertEqual(len(edge), 3)      # each vertex connects to three edges
        vertices2 = set(v for edges in g.values() for v in edges)
        self.assertEqual(vertices1, vertices2)  # edge vertices in original set

        cubefaces = faces(g)
        self.assertEqual(len(cubefaces), 6)     # six faces
        for face in cubefaces:
            self.assertEqual(len(face), 4)      # each face is a square

    def test_cuboctahedron(self):

        # http://en.wikipedia.org/wiki/Cuboctahedron
        # 8 triangular faces and 6 square faces
        # 12 indentical vertices each connecting a triangle and square

        g = cube(3)
        cuboctahedron = linegraph(g)            # V( --> {V1, V2, V3, V4}
        self.assertEqual(len(cuboctahedron), 12)# twelve vertices

        vertices = set(cuboctahedron)
        for edges in cuboctahedron.values():
            self.assertEqual(len(edges), 4)     # each vertex connects to four other vertices
        othervertices = set(edge for edges in cuboctahedron.values() for edge in edges)
        self.assertEqual(vertices, othervertices)   # edge vertices in original set

#        cubofaces = faces(cuboctahedron)
#        facesizes = collections.defaultdict(int)
#        for face in cubofaces:
#            facesizes[len(face)] += 1
#        self.assertEqual(facesizes[3], 8)       # eight triangular faces
#        self.assertEqual(facesizes[4], 6)       # six square faces
#
        for vertex in cuboctahedron:
            edge = vertex                       # Cuboctahedron vertices are edges in Cube
            self.assertEqual(len(edge), 2)      # Two cube vertices define an edge
            for cubevert in edge:
                self.assertIn(cubevert, g)


#==============================================================================

#if __name__ == "__main__":
#    unittest.main()
