import unittest
from test import support
from itertools import *
import sys
import operator
from functools import reduce
import sys
maxsize = 1023                                           ###
minsize = -maxsize-1

def lzip(*args):
    return list(zip(*args))

def onearg(x):
    'Test function of one argument'
    return 2*x

def errfunc(*args):
    'Test function that raises an error'
    raise ValueError

def gen3():
    'Non-restartable source sequence'
    for i in (0, 1, 2):
        yield i

def isEven(x):
    'Test predicate'
    return x%2==0

def isOdd(x):
    'Test predicate'
    return x%2==1

def tupleize(*args):
    return args

def irange(n):
    for i in range(n):
        yield i

class StopNow:
    'Class emulating an empty iterable.'
    def __iter__(self):
        return self
    def __next__(self):
        raise StopIteration

def take(n, seq):
    'Convenience function for partially consuming a long of infinite iterable'
    return list(islice(seq, n))

def prod(iterable):
    return reduce(operator.mul, iterable, 1)


# root level methods for pickling ability
def testR(r):
    return r[0]

def testR2(r):
    return r[2]

def underten(x):
    return x<10


class TestBasicOps(unittest.TestCase):


    def test_accumulate(self):
        self.assertEqual(list(accumulate(range(10))),               # one positional arg
                          [0, 1, 3, 6, 10, 15, 21, 28, 36, 45])
        self.assertEqual(list(accumulate(iterable=range(10))),      # kw arg
                          [0, 1, 3, 6, 10, 15, 21, 28, 36, 45])
        self.assertEqual(list(accumulate('abc')), ['a', 'ab', 'abc'])   # works with non-numeric
        self.assertEqual(list(accumulate([])), [])                  # empty iterable
        self.assertEqual(list(accumulate([7])), [7])                # iterable of length one
        self.assertRaises(TypeError, accumulate, range(10), 5, 6)   # too many args
        self.assertRaises(TypeError, accumulate)                    # too few args
        self.assertRaises(TypeError, accumulate, x=range(10))       # unexpected kwd arg
        self.assertRaises(TypeError, list, accumulate([1, []]))     # args that don't add

        s = [2, 8, 9, 5, 7, 0, 3, 4, 1, 6]
        self.assertEqual(list(accumulate(s, min)),
                         [2, 2, 2, 2, 2, 0, 0, 0, 0, 0])
        self.assertEqual(list(accumulate(s, max)),
                         [2, 8, 9, 9, 9, 9, 9, 9, 9, 9])
        self.assertEqual(list(accumulate(s, operator.mul)),
                         [2, 16, 144, 720, 5040, 0, 0, 0, 0, 0])
        with self.assertRaises(TypeError):
            list(accumulate(s, chr))                                # unary-operation

    def test_chain(self):

        def chain2(*iterables):
            'Pure python version in the docs'
            for it in iterables:
                for element in it:
                    yield element

        for c in (chain, chain2):
            self.assertEqual(list(c('abc', 'def')), list('abcdef'))
            self.assertEqual(list(c('abc')), list('abc'))
            self.assertEqual(list(c('')), [])
            self.assertEqual(take(4, c('abc', 'def')), list('abcd'))
            self.assertRaises(TypeError, list,c(2, 3))

    def test_combinations(self):
        self.assertRaises(TypeError, combinations, 'abc')       # missing r argument
        self.assertRaises(TypeError, combinations, 'abc', 2, 1) # too many arguments
        self.assertRaises(TypeError, combinations, None)        # pool is not iterable

        for op in [lambda a:a]:                                                 ###
            self.assertEqual(list(op(combinations('abc', 32))), [])     # r > n

            self.assertEqual(list(op(combinations('ABCD', 2))),
                             [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])
            testIntermediate = combinations('ABCD', 2)
            next(testIntermediate)
            self.assertEqual(list(op(testIntermediate)),
                             [('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])

            self.assertEqual(list(op(combinations(range(4), 3))),
                             [(0,1,2), (0,1,3), (0,2,3), (1,2,3)])
            testIntermediate = combinations(range(4), 3)
            next(testIntermediate)
            self.assertEqual(list(op(testIntermediate)),
                             [(0,1,3), (0,2,3), (1,2,3)])


        def combinations1(iterable, r):
            'Pure python version shown in the docs'
            pool = tuple(iterable)
            n = len(pool)
            if r > n:
                return
            indices = list(range(r))
            yield tuple(pool[i] for i in indices)
            while 1:
                for i in reversed(range(r)):
                    if indices[i] != i + n - r:
                        break
                else:
                    return
                indices[i] += 1
                for j in range(i+1, r):
                    indices[j] = indices[j-1] + 1
                yield tuple(pool[i] for i in indices)

        def combinations2(iterable, r):
            'Pure python version shown in the docs'
            pool = tuple(iterable)
            n = len(pool)
            for indices in permutations(range(n), r):
                if sorted(indices) == list(indices):
                    yield tuple(pool[i] for i in indices)


        for n in range(7):
            values = [5*x-12 for x in range(n)]
            for r in range(n+2):
                result = list(combinations(values, r))
                self.assertEqual(len(result), len(set(result)))         # no repeats
                self.assertEqual(result, sorted(result))                # lexicographic order
                for c in result:
                    self.assertEqual(len(c), r)                         # r-length combinations
                    self.assertEqual(len(set(c)), r)                    # no duplicate elements
                    self.assertEqual(list(c), sorted(c))                # keep original ordering
                    self.assertTrue(all(e in values for e in c))           # elements taken from input iterable
                    self.assertEqual(list(c),
                                     [e for e in values if e in c])      # comb is a subsequence of the input iterable
                self.assertEqual(result, list(combinations1(values, r))) # matches first pure python version
                self.assertEqual(result, list(combinations2(values, r))) # matches second pure python version


    def test_permutations(self):
        self.assertRaises(TypeError, permutations)              # too few arguments
        self.assertRaises(TypeError, permutations, 'abc', 2, 1) # too many arguments
        self.assertEqual(list(permutations('abc', 32)), [])     # r > n
        self.assertEqual(list(permutations(range(3), 2)),
                                           [(0,1), (0,2), (1,0), (1,2), (2,0), (2,1)])

        def permutations1(iterable, r=None):
            'Pure python version shown in the docs'
            pool = tuple(iterable)
            n = len(pool)
            r = n if r is None else r
            if r > n:
                return
            indices = list(range(n))
            cycles = list(range(n-r+1, n+1))[::-1]
            yield tuple(pool[i] for i in indices[:r])
            while n:
                for i in reversed(range(r)):
                    cycles[i] -= 1
                    if cycles[i] == 0:
                        indices[i:] = indices[i+1:] + indices[i:i+1]
                        cycles[i] = n - i
                    else:
                        j = cycles[i]
                        indices[i], indices[-j] = indices[-j], indices[i]
                        yield tuple(pool[i] for i in indices[:r])
                        break
                else:
                    return

        def permutations2(iterable, r=None):
            'Pure python version shown in the docs'
            pool = tuple(iterable)
            n = len(pool)
            r = n if r is None else r
            for indices in product(range(n), repeat=r):
                if len(set(indices)) == r:
                    yield tuple(pool[i] for i in indices)

        for n in range(4):                                                      ###
            values = [5*x-12 for x in range(n)]
            for r in range(n+2):
                result = list(permutations(values, r))
                self.assertEqual(len(result), len(set(result)))         # no repeats
                self.assertEqual(result, sorted(result))                # lexicographic order
                for p in result:
                    self.assertEqual(len(p), r)                         # r-length permutations
                    self.assertEqual(len(set(p)), r)                    # no duplicate elements
                    self.assertTrue(all(e in values for e in p))           # elements taken from input iterable
                self.assertEqual(result, list(permutations1(values, r))) # matches first pure python version
                self.assertEqual(result, list(permutations2(values, r))) # matches second pure python version
                if r == n:
                    self.assertEqual(result, list(permutations(values, None))) # test r as None
                    self.assertEqual(result, list(permutations(values)))       # test default r


    def test_compress(self):
        self.assertEqual(list(compress(data='ABCDEF', selectors=[1,0,1,0,1,1])), list('ACEF'))
        self.assertEqual(list(compress('ABCDEF', [1,0,1,0,1,1])), list('ACEF'))
        self.assertEqual(list(compress('ABCDEF', [0,0,0,0,0,0])), list(''))
        self.assertEqual(list(compress('ABCDEF', [1,1,1,1,1,1])), list('ABCDEF'))
        self.assertEqual(list(compress('ABCDEF', [1,0,1])), list('AC'))
        self.assertEqual(list(compress('ABC', [0,1,1,1,1,1])), list('BC'))


    def test_count(self):
        self.assertEqual(lzip('abc',count()), [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(lzip('abc',count(3)), [('a', 3), ('b', 4), ('c', 5)])
        self.assertEqual(take(2, lzip('abc',count(3))), [('a', 3), ('b', 4)])
        self.assertEqual(take(2, zip('abc',count(-1))), [('a', -1), ('b', 0)])
        self.assertEqual(take(2, zip('abc',count(-3))), [('a', -3), ('b', -2)])
        self.assertRaises(TypeError, count, 2, 3, 4)
        self.assertEqual(list(islice(count(maxsize-5), 10)),
                         list(range(maxsize-5, maxsize+5)))
        self.assertEqual(list(islice(count(-maxsize-5), 10)),
                         list(range(-maxsize-5, -maxsize+5)))
        self.assertEqual(list(islice(count(10, maxsize+5), 3)),
                         list(range(10, 10+3*(maxsize+5), maxsize+5)))

        #check proper internal error handling for large "step' sizes
        count(1, maxsize+5); sys.exc_info()

    def test_count_with_stride(self):
        self.assertEqual(lzip('abc',count(2,3)), [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(lzip('abc',count(start=2,step=3)),
                         [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(lzip('abc',count(step=-1)),
                         [('a', 0), ('b', -1), ('c', -2)])
        self.assertEqual(lzip('abc',count(2,0)), [('a', 2), ('b', 2), ('c', 2)])
        self.assertEqual(lzip('abc',count(2,1)), [('a', 2), ('b', 3), ('c', 4)])
        self.assertEqual(lzip('abc',count(2,3)), [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(take(3, count(2, 3.25-4j)), [2, 5.25-4j, 8.5-8j])
        self.assertEqual(repr(take(3, count(10, 2.5))), repr([10, 12.5, 15.0]))

    def test_cycle(self):
        self.assertEqual(take(10, cycle('abc')), list('abcabcabca'))
        self.assertEqual(list(cycle('')), [])
        self.assertRaises(TypeError, cycle)
        self.assertEqual(list(islice(cycle(gen3()),10)), [0,1,2,0,1,2,0,1,2,0])


    def test_groupby(self):
        # Check whether it accepts arguments correctly
        self.assertEqual([], list(groupby([])))
        self.assertEqual([], list(groupby([], key=id)))
        self.assertRaises(TypeError, list, groupby('abc', []))
        self.assertRaises(TypeError, groupby, None)
        self.assertRaises(TypeError, groupby, 'abc', lambda x:x, 10)

        # Check normal input
        s = [(0, 10, 20), (0, 11,21), (0,12,21), (1,13,21), (1,14,22),
             (2,15,22), (3,16,23), (3,17,23)]
        dup = []
        for k, g in groupby(s, lambda r:r[0]):
            for elem in g:
                self.assertEqual(k, elem[0])
                dup.append(elem)
        self.assertEqual(s, dup)

        # Check nested case
        dup = []
        for k, g in groupby(s, testR):
            for ik, ig in groupby(g, testR2):
                for elem in ig:
                    self.assertEqual(k, elem[0])
                    self.assertEqual(ik, elem[2])
                    dup.append(elem)
        self.assertEqual(s, dup)

        # Check case where inner iterator is not used
        keys = [k for k, g in groupby(s, testR)]
        expectedkeys = set([r[0] for r in s])
        self.assertEqual(set(keys), expectedkeys)
        self.assertEqual(len(keys), len(expectedkeys))

        # Exercise pipes and filters style
        s = 'abracadabra'
        # sort s | uniq
        r = [k for k, g in groupby(sorted(s))]
        self.assertEqual(r, ['a', 'b', 'c', 'd', 'r'])
        # sort s | uniq -d
        r = [k for k, g in groupby(sorted(s)) if list(islice(g,1,2))]
        self.assertEqual(r, ['a', 'b', 'r'])
        # sort s | uniq -c
        r = [(len(list(g)), k) for k, g in groupby(sorted(s))]
        self.assertEqual(r, [(5, 'a'), (2, 'b'), (1, 'c'), (1, 'd'), (2, 'r')])
        # sort s | uniq -c | sort -rn | head -3
        r = sorted([(len(list(g)) , k) for k, g in groupby(sorted(s))], reverse=True)[:3]
        self.assertEqual(r, [(5, 'a'), (2, 'r'), (2, 'b')])

        # iter.__next__ failure
        class ExpectedError(Exception):
            pass
        def delayed_raise(n=0):
            for i in range(n):
                yield 'yo'
            raise ExpectedError
        def gulp(iterable, keyp=None, func=list):
            return [func(g) for k, g in groupby(iterable, keyp)]

        # iter.__next__ failure on outer object
        self.assertRaises(ExpectedError, gulp, delayed_raise(0))
        # iter.__next__ failure on inner object
        self.assertRaises(ExpectedError, gulp, delayed_raise(1))

        # __eq__ failure
        class DummyCmp:
            def __eq__(self, dst):
                raise ExpectedError
        s = [DummyCmp(), DummyCmp(), None]

        # __eq__ failure on outer object
        self.assertRaises(ExpectedError, gulp, s, func=id)
        # __eq__ failure on inner object
        self.assertRaises(ExpectedError, gulp, s)


    def test_filter(self):
        self.assertEqual(list(filter(isEven, range(6))), [0,2,4])
        self.assertEqual(list(filter(None, [0,1,0,2,0])), [1,2])
        self.assertEqual(list(filter(bool, [0,1,0,2,0])), [1,2])
        self.assertEqual(take(4, filter(isEven, count())), [0,2,4,6])
        self.assertRaises(TypeError, filter)
        self.assertRaises(TypeError, filter, lambda x:x)
        self.assertRaises(TypeError, filter, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, filter, isEven, 3)
        self.assertRaises(TypeError, next, filter(range(6), range(6)))

    def test_filterfalse(self):
        self.assertEqual(list(filterfalse(isEven, range(6))), [1,3,5])
        self.assertEqual(list(filterfalse(None, [0,1,0,2,0])), [0,0,0])
        self.assertEqual(list(filterfalse(bool, [0,1,0,2,0])), [0,0,0])
        self.assertEqual(take(4, filterfalse(isEven, count())), [1,3,5,7])
        self.assertRaises(TypeError, filterfalse)
        self.assertRaises(TypeError, filterfalse, lambda x:x)
        self.assertRaises(TypeError, filterfalse, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, next, filterfalse(range(6), range(6)))

    def test_zip(self):
        # XXX This is rather silly now that builtin zip() calls zip()...
        ans = [(x,y) for x, y in zip('abc',count())]
        self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(list(zip('abc', range(6))), lzip('abc', range(6)))
        self.assertEqual(list(zip('abcdef', range(3))), lzip('abcdef', range(3)))
        self.assertEqual(take(3,zip('abcdef', count())), lzip('abcdef', range(3)))
        self.assertEqual(list(zip('abcdef')), lzip('abcdef'))
        self.assertEqual(list(zip()), lzip())
        self.assertRaises(TypeError, zip, 3)
        self.assertRaises(TypeError, zip, range(3), 3)
        self.assertEqual([tuple(list(pair)) for pair in zip('abc', 'def')],
                         lzip('abc', 'def'))
        self.assertEqual([pair for pair in zip('abc', 'def')],
                         lzip('abc', 'def'))

    def test_ziplongest(self):
        for args in [
                ['abc', range(6)],
                [range(6), 'abc'],
                [range(10), range(20,21), range(30,35)],                        ###
            ]:
            target = [tuple([arg[i] if i < len(arg) else None for arg in args])
                      for i in range(max(map(len, args)))]
            self.assertEqual(list(zip_longest(*args)), target)
            self.assertEqual(list(zip_longest(*args, **{})), target)
            target = [tuple((e is None and 'X' or e) for e in t) for t in target]   # Replace None fills with 'X'
            self.assertEqual(list(zip_longest(*args, **dict(fillvalue='X'))), target)

        self.assertEqual(take(3,zip_longest('abcdef', count())), list(zip('abcdef', range(3)))) # take 3 from infinite input

        self.assertEqual(list(zip_longest()), list(zip()))
        self.assertEqual(list(zip_longest([])), list(zip([])))
        self.assertEqual(list(zip_longest('abcdef')), list(zip('abcdef')))

        self.assertEqual(list(zip_longest('abc', 'defg', **{})),
                         list(zip(list('abc')+[None], 'defg'))) # empty keyword dict

        for stmt in [
            "zip_longest('abc', fv=1)",
            "zip_longest('abc', fillvalue=1, bogus_keyword=None)",
        ]:
            try:
                eval(stmt, globals(), locals())
            except TypeError:
                pass
            else:
                self.fail('Did not raise Type in:  ' + stmt)

        self.assertEqual([tuple(list(pair)) for pair in zip_longest('abc', 'def')],
                         list(zip('abc', 'def')))
        self.assertEqual([pair for pair in zip_longest('abc', 'def')],
                         list(zip('abc', 'def')))

    def test_product(self):
        for args, result in [
            ([], [()]),                     # zero iterables
            (['ab'], [('a',), ('b',)]),     # one iterable
            ]:
            self.assertEqual(list(product(*args)), result)
            for r in range(4):
                self.assertEqual(list(product(*(args*r))),
                                 list(product(*args, **dict(repeat=r))))

    def test_repeat(self):
        self.assertEqual(list(repeat(object='a', times=3)), ['a', 'a', 'a'])
        self.assertEqual(lzip(range(3),repeat('a')),
                         [(0, 'a'), (1, 'a'), (2, 'a')])
        self.assertEqual(list(repeat('a', 3)), ['a', 'a', 'a'])
        self.assertEqual(take(3, repeat('a')), ['a', 'a', 'a'])
        self.assertEqual(list(repeat('a', 0)), [])
        self.assertEqual(list(repeat('a', -3)), [])
        self.assertRaises(TypeError, repeat)
        self.assertRaises(TypeError, repeat, None, 3, 4)


    def test_map(self):
        self.assertEqual(list(map(operator.pow, range(3), range(1,7))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(map(tupleize, 'abc', range(5))),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(list(map(tupleize, 'abc', count())),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(take(2,map(tupleize, 'abc', count())),
                         [('a',0),('b',1)])
        self.assertEqual(list(map(operator.pow, [])), [])
        self.assertRaises(TypeError, map)
        self.assertRaises(TypeError, list, map(None, range(3), range(3)))
        self.assertRaises(TypeError, map, operator.neg)
        self.assertRaises(TypeError, next, map(10, range(5)))
        self.assertRaises(ValueError, next, map(errfunc, [4], [5]))
        self.assertRaises(TypeError, next, map(onearg, [4], [5]))


    def test_starmap(self):
        self.assertEqual(list(starmap(operator.pow, zip(range(3), range(1,7)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(take(3, starmap(operator.pow, zip(count(), count(1)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(starmap(operator.pow, [])), [])
        self.assertEqual(list(starmap(operator.pow, [iter([4,5])])), [4**5])
        self.assertRaises(TypeError, list, starmap(operator.pow, [None]))
        self.assertRaises(TypeError, starmap)
        self.assertRaises(TypeError, starmap, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, starmap(10, [(4,5)]))
        self.assertRaises(ValueError, next, starmap(errfunc, [(4,5)]))
        self.assertRaises(TypeError, next, starmap(onearg, [(4,5)]))


    def test_islice(self):
        for args in [          # islice(args) should agree with range(args)
                (10, 20, 3),
                (10, 3, 20),
                (10, 20),
                (10, 3),
                (20,)
                ]:
            self.assertEqual(list(islice(range(100), *args)),
                             list(range(*args)))

        for args, tgtargs in [  # Stop when seqn is exhausted
                ((10, 110, 3), ((10, 100, 3))),
                ((10, 110), ((10, 100))),
                ((110,), (100,))
                ]:
            self.assertEqual(list(islice(range(100), *args)),
                             list(range(*tgtargs)))

        # Test stop=None
        self.assertEqual(list(islice(range(10), None)), list(range(10)))
        self.assertEqual(list(islice(range(10), None, None)), list(range(10)))
        self.assertEqual(list(islice(range(10), None, None, None)), list(range(10)))
        self.assertEqual(list(islice(range(10), 2, None)), list(range(2, 10)))
        self.assertEqual(list(islice(range(10), 1, None, 2)), list(range(1, 10, 2)))

        # Test number of items consumed     SF #1171417
        it = iter(range(10))
        self.assertEqual(list(islice(it, 3)), list(range(3)))
        self.assertEqual(list(it), list(range(3, 10)))

        self.assertEqual(len(list(islice(count(), 1, 10, maxsize))), 1)

        # Issue #10323:  Less islice in a predictable state
        c = count()
        self.assertEqual(list(islice(c, 1, 3, 50)), [1])
        self.assertEqual(next(c), 3)


    def test_takewhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        self.assertEqual(list(takewhile(underten, data)), [1, 3, 5])
        self.assertEqual(list(takewhile(underten, [])), [])
        self.assertRaises(TypeError, takewhile)
        self.assertRaises(TypeError, takewhile, operator.pow)
        self.assertRaises(TypeError, takewhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, takewhile(10, [(4,5)]))
        self.assertRaises(ValueError, next, takewhile(errfunc, [(4,5)]))
        t = takewhile(bool, [1, 1, 1, 0, 0, 0])
        self.assertEqual(list(t), [1, 1, 1])
        self.assertRaises(StopIteration, next, t)


    def test_dropwhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        self.assertEqual(list(dropwhile(underten, data)), [20, 2, 4, 6, 8])
        self.assertEqual(list(dropwhile(underten, [])), [])
        self.assertRaises(TypeError, dropwhile)
        self.assertRaises(TypeError, dropwhile, operator.pow)
        self.assertRaises(TypeError, dropwhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, dropwhile(10, [(4,5)]))
        self.assertRaises(ValueError, next, dropwhile(errfunc, [(4,5)]))




    def test_StopIteration(self):
        self.assertRaises(StopIteration, next, zip())

        for f in (chain, cycle):                                                ###
            self.assertRaises(StopIteration, next, f([]))
            self.assertRaises(StopIteration, next, f(StopNow()))


        self.assertRaises(StopIteration, next, repeat(None, 0))


class TestExamples(unittest.TestCase):

    def test_accumulate(self):
        self.assertEqual(list(accumulate([1,2,3,4,5])), [1, 3, 6, 10, 15])


    def test_chain(self):
        self.assertEqual(''.join(chain('ABC', 'DEF')), 'ABCDEF')

    def test_combinations(self):
        self.assertEqual(list(combinations('ABCD', 2)),
                         [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])
        self.assertEqual(list(combinations(range(4), 3)),
                         [(0,1,2), (0,1,3), (0,2,3), (1,2,3)])

    def test_compress(self):
        self.assertEqual(list(compress('ABCDEF', [1,0,1,0,1,1])), list('ACEF'))

    def test_count(self):
        self.assertEqual(list(islice(count(10), 5)), [10, 11, 12, 13, 14])

    def test_cycle(self):
        self.assertEqual(list(islice(cycle('ABCD'), 12)), list('ABCDABCDABCD'))

    def test_dropwhile(self):
        self.assertEqual(list(dropwhile(lambda x: x<5, [1,4,6,4,1])), [6,4,1])

    def test_groupby(self):
        self.assertEqual([k for k, g in groupby('AAAABBBCCDAABBB')],
                         list('ABCDAB'))
        self.assertEqual([(list(g)) for k, g in groupby('AAAABBBCCD')],
                         [list('AAAA'), list('BBB'), list('CC'), list('D')])

    def test_filter(self):
        self.assertEqual(list(filter(lambda x: x%2, range(10))), [1,3,5,7,9])

    def test_filterfalse(self):
        self.assertEqual(list(filterfalse(lambda x: x%2, range(10))), [0,2,4,6,8])

    def test_map(self):
        self.assertEqual(list(map(pow, (2,3,10), (5,2,3))), [32, 9, 1000])

    def test_islice(self):
        self.assertEqual(list(islice('ABCDEFG', 2)), list('AB'))
        self.assertEqual(list(islice('ABCDEFG', 2, 4)), list('CD'))
        self.assertEqual(list(islice('ABCDEFG', 2, None)), list('CDEFG'))
        self.assertEqual(list(islice('ABCDEFG', 0, None, 2)), list('ACEG'))

    def test_zip(self):
        self.assertEqual(list(zip('ABCD', 'xy')), [('A', 'x'), ('B', 'y')])

    def test_zip_longest(self):
        self.assertEqual(list(zip_longest('ABCD', 'xy', fillvalue='-')),
                         [('A', 'x'), ('B', 'y'), ('C', '-'), ('D', '-')])

    def test_permutations(self):
        self.assertEqual(list(permutations('ABCD', 2)),
                         list(map(tuple, 'AB AC AD BA BC BD CA CB CD DA DB DC'.split())))
        self.assertEqual(list(permutations(range(3))),
                         [(0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0)])

    def test_product(self):
        self.assertEqual(list(product('ABCD', 'xy')),
                         list(map(tuple, 'Ax Ay Bx By Cx Cy Dx Dy'.split())))
        self.assertEqual(list(product(range(2), repeat=3)),
                        [(0,0,0), (0,0,1), (0,1,0), (0,1,1),
                         (1,0,0), (1,0,1), (1,1,0), (1,1,1)])

    def test_repeat(self):
        self.assertEqual(list(repeat(10, 3)), [10, 10, 10])

    def test_stapmap(self):
        self.assertEqual(list(starmap(pow, [(2,5), (3,2), (10,3)])),
                         [32, 9, 1000])

    def test_takewhile(self):
        self.assertEqual(list(takewhile(lambda x: x<5, [1,4,6,4,1])), [1,4])


class TestGC(unittest.TestCase):

    def makecycle(self, iterator, container):
        container.append(iterator)
        next(iterator)
        del container, iterator

    def test_accumulate(self):
        a = []
        self.makecycle(accumulate([1,2,a,3]), a)

    def test_chain(self):
        a = []
        self.makecycle(chain(a), a)

    def test_combinations(self):
        a = []
        self.makecycle(combinations([1,2,a,3], 3), a)

    def test_compress(self):
        a = []
        self.makecycle(compress('ABCDEF', [1,0,1,0,1,0]), a)

    def test_count(self):
        a = []
        Int = type('Int', (int,), dict(x=a))
        self.makecycle(count(Int(0), Int(1)), a)

    def test_cycle(self):
        a = []
        self.makecycle(cycle([a]*2), a)

    def test_dropwhile(self):
        a = []
        self.makecycle(dropwhile(bool, [0, a, a]), a)

    def test_groupby(self):
        a = []
        self.makecycle(groupby([a]*2, lambda x:x), a)

    def test_filter(self):
        a = []
        self.makecycle(filter(lambda x:True, [a]*2), a)

    def test_filterfalse(self):
        a = []
        self.makecycle(filterfalse(lambda x:False, a), a)

    def test_zip(self):
        a = []
        self.makecycle(zip([a]*2, [a]*3), a)

    def test_zip_longest(self):
        a = []
        self.makecycle(zip_longest([a]*2, [a]*3), a)
        b = [a, None]
        self.makecycle(zip_longest([a]*2, [a]*3, fillvalue=b), a)

    def test_map(self):
        a = []
        self.makecycle(map(lambda x:x, [a]*2), a)

    def test_islice(self):
        a = []
        self.makecycle(islice([a]*2, None), a)

    def test_permutations(self):
        a = []
        self.makecycle(permutations([1,2,a,3], 3), a)

    def test_product(self):
        a = []
        self.makecycle(product([1,2,a,3], repeat=3), a)

    def test_repeat(self):
        a = []
        self.makecycle(repeat(a), a)

    def test_starmap(self):
        a = []
        self.makecycle(starmap(lambda *t: t, [(a,a)]*2), a)

    def test_takewhile(self):
        a = []
        self.makecycle(takewhile(bool, [1, 0, a, a]), a)

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

def L(seqn):
    'Test multiple tiers of iterators'
    return chain(map(lambda x:x, R(Ig(G(seqn)))))


class TestVariousIteratorArgs(unittest.TestCase):

    def test_accumulate(self):
        s = [1,2,3,4,5]
        r = [1,3,6,10,15]
        n = len(s)
        for g in (G, I, Ig, L, R):
            self.assertEqual(list(accumulate(g(s))), r)
        self.assertEqual(list(accumulate(S(s))), [])
        self.assertRaises(ZeroDivisionError, list, accumulate(E(s)))

    def test_chain(self):
        for s in ("123", "", range(10), ('do', 1.2), range(20,30,5)):           ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(chain(g(s))), list(g(s)))
                self.assertEqual(list(chain(g(s), g(s))), list(g(s))+list(g(s)))
            self.assertRaises(TypeError, list, chain(X(s)))
            self.assertRaises(TypeError, list, chain(N(s)))
            self.assertRaises(ZeroDivisionError, list, chain(E(s)))

    def test_compress(self):
        for s in ("123", "", range(10), ('do', 1.2), range(20,30,5)):           ###
            n = len(s)
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(compress(g(s), repeat(1))), list(g(s)))
            self.assertRaises(TypeError, compress, X(s), repeat(1))
            self.assertRaises(ZeroDivisionError, list, compress(E(s), repeat(1)))

    def test_cycle(self):
        for s in ("123", "", range(10), ('do', 1.2), range(20,30,5)):           ###
            for g in (G, I, Ig, S, L, R):
                tgtlen = len(s) * 3
                expected = list(g(s))*3
                actual = list(islice(cycle(g(s)), tgtlen))
                self.assertEqual(actual, expected)
            self.assertRaises(ZeroDivisionError, list, cycle(E(s)))

    def test_groupby(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual([k for k, sb in groupby(g(s))], list(g(s)))
            self.assertRaises(TypeError, groupby, X(s))
            self.assertRaises(ZeroDivisionError, list, groupby(E(s)))

    def test_filter(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(filter(isEven, g(s))),
                                 [x for x in g(s) if isEven(x)])
            self.assertRaises(TypeError, filter, isEven, X(s))
            self.assertRaises(ZeroDivisionError, list, filter(isEven, E(s)))

    def test_filterfalse(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(filterfalse(isEven, g(s))),
                                 [x for x in g(s) if isOdd(x)])
            self.assertRaises(ZeroDivisionError, list, filterfalse(isEven, E(s)))

    def test_zip(self):
        for s in ("123", "", range(10), ('do', 1.2), range(20,30,5)):           ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(zip(g(s))), lzip(g(s)))
                self.assertEqual(list(zip(g(s), g(s))), lzip(g(s), g(s)))
            self.assertRaises(TypeError, zip, X(s))
            self.assertRaises(ZeroDivisionError, list, zip(E(s)))

    def test_ziplongest(self):
        for s in ("123", "", range(10), ('do', 1.2), range(20,30,5)):           ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(zip_longest(g(s))), list(zip(g(s))))
                self.assertEqual(list(zip_longest(g(s), g(s))), list(zip(g(s), g(s))))
            self.assertRaises(ZeroDivisionError, list, zip_longest(E(s)))

    def test_map(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,50,5)):      ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(map(onearg, g(s))),
                                 [onearg(x) for x in g(s)])
                self.assertEqual(list(map(operator.pow, g(s), g(s))),
                                 [x**x for x in g(s)])
            self.assertRaises(TypeError, map, onearg, X(s))
            self.assertRaises(ZeroDivisionError, list, map(onearg, E(s)))

    def test_islice(self):
        for s in ("12345", "", range(10), ('do', 1.2), range(20,30,5)):         ###
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(islice(g(s),1,None,2)), list(g(s))[1::2])
            self.assertRaises(ZeroDivisionError, list, islice(E(s), 10))

    def test_starmap(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                ss = lzip(s, s)
                self.assertEqual(list(starmap(operator.pow, g(ss))),
                                 [x**x for x in g(s)])
            self.assertRaises(ZeroDivisionError, list, starmap(operator.pow, E(ss)))

    def test_takewhile(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                tgt = []
                for elem in g(s):
                    if not isEven(elem): break
                    tgt.append(elem)
                self.assertEqual(list(takewhile(isEven, g(s))), tgt)
            self.assertRaises(ZeroDivisionError, list, takewhile(isEven, E(s)))

    def test_dropwhile(self):
        for s in (range(10), range(0), range(10), (7,11), range(20,30,5)):      ###
            for g in (G, I, Ig, S, L, R):
                tgt = []
                for elem in g(s):
                    if not tgt and isOdd(elem): continue
                    tgt.append(elem)
                self.assertEqual(list(dropwhile(isOdd, g(s))), tgt)
            self.assertRaises(ZeroDivisionError, list, dropwhile(isOdd, E(s)))



class RegressionTests(unittest.TestCase):



    def test_sf_950057(self):
        # Make sure that chain() and cycle() catch exceptions immediately
        # rather than when shifting between input sources

        def gen1():
            hist.append(0)
            yield 1
            hist.append(1)
            raise AssertionError
            hist.append(2)

        def gen2(x):
            hist.append(3)
            yield 2
            hist.append(4)
            if x:
                raise StopIteration

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(False)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(True)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, cycle(gen1()))
        self.assertEqual(hist, [0,1])

