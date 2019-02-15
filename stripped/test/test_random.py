import unittest
import random
import time
from math import log, exp, pi, sin                                              ###
from test import support

class TestBasicOps:
    # Superclass with tests common to all generators.
    # Subclasses must arrange for self.gen to retrieve the Random instance
    # to be tested.

    def randomlist(self, n):
        """Helper function to make a list of random numbers"""
        return [self.gen.random() for i in range(n)]

    @unittest.skip('Missing random.Random()')                                   ###
    def test_autoseed(self):
        self.gen.seed()
        state1 = self.gen.getstate()
        time.sleep(0.1)
        self.gen.seed()      # diffent seeds at different times
        state2 = self.gen.getstate()
        self.assertNotEqual(state1, state2)

    @unittest.skip('Missing random.Random()')                                   ###
    def test_saverestore(self):
        N = 1000
        self.gen.seed()
        state = self.gen.getstate()
        randseq = self.randomlist(N)
        self.gen.setstate(state)    # should regenerate the same sequence
        self.assertEqual(randseq, self.randomlist(N))

    @unittest.expectedFailure                                                   ###
    def test_seedargs(self):
        # Seed value with a negative hash.
        class MySeed(object):
            def __hash__(self):
                return -1729
        for arg in [None, 0, 0, 1, 1, -1, -1, 10**20, -(10**20),
                    3.14, 1+2j, 'a', tuple('abc'), MySeed()]:
            self.gen.seed(arg)
        for arg in [list(range(3)), dict(one=1)]:
            self.assertRaises(TypeError, self.gen.seed, arg)
        self.assertRaises(TypeError, self.gen.seed, 1, 2, 3, 4)
        self.assertRaises(TypeError, type(self.gen), [])

    @unittest.skip('Missing .shuffle()')                                        ###
    def test_shuffle(self):
        shuffle = self.gen.shuffle
        lst = []
        shuffle(lst)
        self.assertEqual(lst, [])
        lst = [37]
        shuffle(lst)
        self.assertEqual(lst, [37])
        seqs = [list(range(n)) for n in range(10)]
        shuffled_seqs = [list(range(n)) for n in range(10)]
        for shuffled_seq in shuffled_seqs:
            shuffle(shuffled_seq)
        for (seq, shuffled_seq) in zip(seqs, shuffled_seqs):
            self.assertEqual(len(seq), len(shuffled_seq))
            self.assertEqual(set(seq), set(shuffled_seq))
        # The above tests all would pass if the shuffle was a
        # no-op. The following non-deterministic test covers that.  It
        # asserts that the shuffled sequence of 1000 distinct elements
        # must be different from the original one. Although there is
        # mathematically a non-zero probability that this could
        # actually happen in a genuinely random shuffle, it is
        # completely negligible, given that the number of possible
        # permutations of 1000 objects is 1000! (factorial of 1000),
        # which is considerably larger than the number of atoms in the
        # universe...
        lst = list(range(1000))
        shuffled_lst = list(range(1000))
        shuffle(shuffled_lst)
        self.assertTrue(lst != shuffled_lst)
        shuffle(lst)
        self.assertTrue(lst != shuffled_lst)

    def test_choice(self):
        choice = self.gen.choice
        with self.assertRaises(IndexError):
            choice([])
        self.assertEqual(choice([50]), 50)
        self.assertIn(choice([25, 75]), [25, 75])

    @unittest.skip('Missing .sample()')                                         ###
    def test_sample(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # the sample is of the correct length and contains only unique items
        N = 100
        population = range(N)
        for k in range(N+1):
            s = self.gen.sample(population, k)
            self.assertEqual(len(s), k)
            uniq = set(s)
            self.assertEqual(len(uniq), k)
            self.assertTrue(uniq <= set(population))
        self.assertEqual(self.gen.sample([], 0), [])  # test edge case N==k==0
        # Exception raised if size of sample exceeds that of population
        self.assertRaises(ValueError, self.gen.sample, population, N+1)

    @unittest.skip('Missing .sample()')                                         ###
    def test_sample_distribution(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # sample generates all possible permutations
        n = 5
        pop = range(n)
        trials = 10000  # large num prevents false negatives without slowing normal case
        def factorial(n):
            if n == 0:
                return 1
            return n * factorial(n - 1)
        for k in range(n):
            expected = factorial(n) // factorial(n-k)
            perms = {}
            for i in range(trials):
                perms[tuple(self.gen.sample(pop, k))] = None
                if len(perms) == expected:
                    break
            else:
                self.fail()

    @unittest.skip('Missing .sample()')                                         ###
    def test_sample_inputs(self):
        # SF bug #801342 -- population can be any iterable defining __len__()
        self.gen.sample(set(range(20)), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(str('abcdefghijklmnopqrst'), 2)
        self.gen.sample(tuple('abcdefghijklmnopqrst'), 2)

    @unittest.skip('Missing .sample()')                                         ###
    def test_sample_on_dicts(self):
        self.assertRaises(TypeError, self.gen.sample, dict.fromkeys('abcdef'), 2)

    @unittest.skip('Missing .gauss()')                                          ###
    def test_gauss(self):
        # Ensure that the seed() method initializes all the hidden state.  In
        # particular, through 2.2.1 it failed to reset a piece of state used
        # by (and only by) the .gauss() method.

        for seed in 1, 12, 123, 1234, 12345, 123456, 654321:
            self.gen.seed(seed)
            x1 = self.gen.random()
            y1 = self.gen.gauss(0, 1)

            self.gen.seed(seed)
            x2 = self.gen.random()
            y2 = self.gen.gauss(0, 1)

            self.assertEqual(x1, x2)
            self.assertEqual(y1, y2)

    @unittest.skip('No pickle')                                                 ###
    def test_pickling(self):
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            state = pickle.dumps(self.gen, proto)
            origseq = [self.gen.random() for i in range(10)]
            newgen = pickle.loads(state)
            restoredseq = [newgen.random() for i in range(10)]
            self.assertEqual(origseq, restoredseq)

    @unittest.skip('No pickle')                                                 ###
    def test_bug_1727780(self):
        # verify that version-2-pickles can be loaded
        # fine, whether they are created on 32-bit or 64-bit
        # platforms, and that version-3-pickles load fine.
        files = [("randv2_32.pck", 780),
                 ("randv2_64.pck", 866),
                 ("randv3.pck", 343)]
        for file, value in files:
            f = open(support.findfile(file),"rb")
            r = pickle.load(f)
            f.close()
            self.assertEqual(int(r.random()*1000), value)

    @unittest.skip('OverflowError')                                             ###
    def test_bug_9025(self):
        # Had problem with an uneven distribution in int(n*random())
        # Verify the fix by checking that distributions fall within expectations.
        n = 100000
        randrange = self.gen.randrange
        k = sum(randrange(6755399441055744) % 3 == 2 for i in range(n))
        self.assertTrue(0.30 < k/n < .37, (k/n))

SystemRandom_available = False                                                  ###

@unittest.skipUnless(SystemRandom_available, "random.SystemRandom not available")
class SystemRandom_TestBasicOps(TestBasicOps, unittest.TestCase):
    pass                                                                        ###

class MersenneTwister_TestBasicOps(TestBasicOps, unittest.TestCase):
    gen = random                                                                ###

    @unittest.skip('Missing random.Random()')                                   ###
    def test_guaranteed_stable(self):
        # These sequences are guaranteed to stay the same across versions of python
        self.gen.seed(3456147, version=1)
        self.assertEqual([self.gen.random().hex() for i in range(4)],
            ['0x1.ac362300d90d2p-1', '0x1.9d16f74365005p-1',
             '0x1.1ebb4352e4c4dp-1', '0x1.1a7422abf9c11p-1'])
        self.gen.seed("the quick brown fox", version=2)
        self.assertEqual([self.gen.random().hex() for i in range(4)],
            ['0x1.1239ddfb11b7cp-3', '0x1.b3cbb5c51b120p-4',
             '0x1.8c4f55116b60fp-1', '0x1.63eb525174a27p-1'])

    @unittest.skip('Missing random.Random()')                                   ###
    def test_setstate_first_arg(self):
        self.assertRaises(ValueError, self.gen.setstate, (1, None, None))

    @unittest.skip('Missing random.Random()')                                   ###
    def test_setstate_middle_arg(self):
        # Wrong type, s/b tuple
        self.assertRaises(TypeError, self.gen.setstate, (2, None, None))
        # Wrong length, s/b 625
        self.assertRaises(ValueError, self.gen.setstate, (2, (1,2,3), None))
        # Wrong type, s/b tuple of 625 ints
        self.assertRaises(TypeError, self.gen.setstate, (2, ('a',)*625, None))
        # Last element s/b an int also
        self.assertRaises(TypeError, self.gen.setstate, (2, (0,)*624+('a',), None))
        # Last element s/b between 0 and 624
        with self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(625,), None))
        with self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(-1,), None))

        # Little trick to make "tuple(x % (2**32) for x in internalstate)"
        # raise ValueError. I cannot think of a simple way to achieve this, so
        # I am opting for using a generator as the middle argument of setstate
        # which attempts to cast a NaN to integer.
        state_values = self.gen.getstate()[1]
        state_values = list(state_values)
        state_values[-1] = float('nan')
        state = (int(x) for x in state_values)
        self.assertRaises(TypeError, self.gen.setstate, (2, state, None))

    @unittest.skip('MemoryError')                                               ###
    def test_referenceImplementation(self):
        # Compare the python implementation with results from the original
        # code.  Create 2000 53-bit precision random floats.  Compare only
        # the last ten entries to show that the independent implementations
        # are tracking.  Here is the main() function needed to create the
        # list of expected random numbers:
        #    void main(void){
        #         int i;
        #         unsigned long init[4]={61731, 24903, 614, 42143}, length=4;
        #         init_by_array(init, length);
        #         for (i=0; i<2000; i++) {
        #           printf("%.15f ", genrand_res53());
        #           if (i%5==4) printf("\n");
        #         }
        #     }
        expected = [0.45839803073713259,
                    0.86057815201978782,
                    0.92848331726782152,
                    0.35932681119782461,
                    0.081823493762449573,
                    0.14332226470169329,
                    0.084297823823520024,
                    0.53814864671831453,
                    0.089215024911993401,
                    0.78486196105372907]

        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        for a, e in zip(actual, expected):
            self.assertAlmostEqual(a,e,places=14)

    @unittest.skip('MemoryError')                                               ###
    def test_strong_reference_implementation(self):
        # Like test_referenceImplementation, but checks for exact bit-level
        # equality.  This should pass on any box where C double contains
        # at least 53 bits of precision (the underlying algorithm suffers
        # no rounding errors -- all results are exact).
        from math import ldexp

        expected = [0x0eab3258d2231f,
                    0x1b89db315277a5,
                    0x1db622a5518016,
                    0x0b7f9af0d575bf,
                    0x029e4c4db82240,
                    0x04961892f5d673,
                    0x02b291598e4589,
                    0x11388382c15694,
                    0x02dad977c9e1fe,
                    0x191d96d4d334c6]
        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        for a, e in zip(actual, expected):
            self.assertEqual(int(ldexp(a, 53)), e)

    def test_long_seed(self):
        # This is most interesting to run in debug mode, just to make sure
        # nothing blows up.  Under the covers, a dynamically resized array
        # is allocated, consuming space proportional to the number of bits
        # in the seed.  Unfortunately, that's a quadratic-time algorithm,
        # so don't make this horribly big.
        seed = (1 << (10000 * 8)) - 1  # about 10K bytes
        self.gen.seed(seed)

    @unittest.expectedFailure                                                   ###
    def test_53_bits_per_float(self):
        # This should pass whenever a C double has 53 bit precision.
        span = 2 ** 53
        cum = 0
        for i in range(100):
            cum |= int(self.gen.random() * span)
        self.assertEqual(cum, span-1)

    @unittest.skip('OverflowError')                                             ###
    def test_bigrand(self):
        # The randrange routine should build-up the required number of bits
        # in stages so that all bit positions are active.
        span = 2 ** 500
        cum = 0
        for i in range(100):
            r = self.gen.randrange(span)
            self.assertTrue(0 <= r < span)
            cum |= r
        self.assertEqual(cum, span-1)

    @unittest.skip('OverflowError')                                             ###
    def test_bigrand_ranges(self):
        for i in [40,80, 160, 200, 211, 250, 375, 512, 550]:
            start = self.gen.randrange(2 ** (i-2))
            stop = self.gen.randrange(2 ** i)
            if stop <= start:
                continue
            self.assertTrue(start <= self.gen.randrange(start, stop) < stop)

    def test_rangelimits(self):
        for start, stop in [(-2,0), ]:                                          ### Overflow
            self.assertEqual(set(range(start,stop)),
                set([self.gen.randrange(start,stop) for i in range(100)]))

    def test_genrandbits(self):
        # Verify ranges
        for k in range(1, 33):                                                  ###
            self.assertTrue(0 <= self.gen.getrandbits(k) < 2**k)

        # Verify all bits active
        getbits = self.gen.getrandbits
        for span in [1, 2, 3, 4, 31, 32, 32]:                                   ###
            cum = 0
            for i in range(100):
                cum |= getbits(span)
            self.assertEqual(cum, 2**span-1)

        # Verify argument checking
        self.assertRaises(TypeError, self.gen.getrandbits)
        self.assertRaises(TypeError, self.gen.getrandbits, 'a')
        self.assertRaises(TypeError, self.gen.getrandbits, 1, 2)
        self.assertRaises(ValueError, self.gen.getrandbits, 0)

    @unittest.expectedFailure                                                   ### i=49 => AssertionError: 49 != 50
    def test_randbelow_logic(self, _log=log, int=int):
        # check bitcount transition points:  2**i and 2**(i+1)-1
        # show that: k = int(1.001 + _log(n, 2))
        # is equal to or one greater than the number of bits in n
        for i in range(1, 1000):
            n = 1 << i # check an exact power of two
            numbits = i+1
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)
            self.assertEqual(n, 2**(k-1))

            n += n - 1      # check 1 below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertIn(k, [numbits, numbits+1])
            self.assertTrue(2**k > n > 2**(k-2))

            n -= n >> 15     # check a little farther below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)        # note the stronger assertion
            self.assertTrue(2**k > n > 2**(k-1))   # note the stronger assertion

    @unittest.skip('OverflowError')                                             ###
    def test_randrange_bug_1590891(self):
        start = 1000000000000
        stop = -100000000000000000000
        step = -200
        x = self.gen.randrange(start, stop, step)
        self.assertTrue(stop < x <= start)
        self.assertEqual((x+stop)%step, 0)


@unittest.skip('Not supported')                                                 ###
class TestDistributions(unittest.TestCase):
    pass                                                                        ###

@unittest.skip('Not supported')                                                 ###
class TestModule(unittest.TestCase):
    pass                                                                        ###


