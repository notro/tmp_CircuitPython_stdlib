# Test hashlib module
#
# $Id$
#
#  Copyright (C) 2005-2010   Gregory P. Smith (greg@krypto.org)
#  Licensed to PSF under a Contributor Agreement.
#

import array
import hashlib
import itertools
import os
import sys
import unittest
from test import support


def hexstr(s):
    assert isinstance(s, bytes), repr(s)
    h = "0123456789abcdef"
    r = ''
    for i in s:
        r += h[(i >> 4) & 0xF] + h[i & 0xF]
    return r


class HashLibTestCase(unittest.TestCase):
    supported_hash_names = ( 'md5',)                                            ###

    def __init__(self, *args, **kwargs):
        algorithms = set()
        for algorithm in self.supported_hash_names:
            algorithms.add(algorithm.lower())
        self.constructors_to_test = {}
        for algorithm in algorithms:
            self.constructors_to_test[algorithm] = set()

        # For each algorithm, test the direct constructor and the use
        # of hashlib.new given the algorithm name.
        for algorithm, constructors in self.constructors_to_test.items():
            constructors.add(getattr(hashlib, algorithm))
            def _test_algorithm_via_hashlib_new(data=None, _alg=algorithm):
                if data is None:
                    return hashlib.new(_alg)
                return hashlib.new(_alg, data)
            constructors.add(_test_algorithm_via_hashlib_new)


        super(HashLibTestCase, self).__init__(*args, **kwargs)

    @property
    def hash_constructors(self):
        constructors = self.constructors_to_test.values()
        return itertools.chain(*constructors)                                   ###

    def test_hash_array(self):
        a = array.array("b", range(10))
        for cons in self.hash_constructors:
            c = cons(a)
            c.hexdigest()

    def test_unknown_hash(self):
        self.assertRaises(ValueError, hashlib.new, 'spam spam spam spam spam')
        self.assertRaises(TypeError, hashlib.new, 1)

    def test_hexdigest(self):
        for cons in self.hash_constructors:
            h = cons()
            self.assertIsInstance(h.digest(), bytes)
            self.assertEqual(hexstr(h.digest()), h.hexdigest())

    def test_name_attribute(self):
        for cons in self.hash_constructors:
            h = cons()
            self.assertIsInstance(h.name, str)
            self.assertIn(h.name, self.supported_hash_names)
            self.assertEqual(h.name, hashlib.new(h.name).name)

    def test_large_update(self):
        aas = b'a' * 128
        bees = b'b' * 127
        cees = b'c' * 126
        dees = b'd' * 2048 #  HASHLIB_GIL_MINSIZE

        for cons in self.hash_constructors:
            m1 = cons()
            m1.update(aas)
            m1.update(bees)
            m1.update(cees)
            m1.update(dees)

            m2 = cons()
            m2.update(aas + bees + cees + dees)
            self.assertEqual(m1.digest(), m2.digest())

            m3 = cons(aas + bees + cees + dees)
            self.assertEqual(m1.digest(), m3.digest())

            # verify copy() doesn't touch original
            m4 = cons(aas + bees + cees)
            m4_digest = m4.digest()
            m4_copy = m4.copy()
            m4_copy.update(dees)
            self.assertEqual(m1.digest(), m4_copy.digest())
            self.assertEqual(m4.digest(), m4_digest)

    def check(self, name, data, hexdigest):
        hexdigest = hexdigest.lower()
        constructors = self.constructors_to_test[name]
        # 2 is for hashlib.name(...) and hashlib.new(name, ...)
        self.assertGreaterEqual(len(constructors), 2)
        for hash_object_constructor in constructors:
            m = hash_object_constructor(data)
            computed = m.hexdigest()
            self.assertEqual(
                    computed, hexdigest,
                    "Hash algorithm %s constructed using %s returned hexdigest"
                    " %r for %d byte input data that should have hashed to %r."
                    % (name, hash_object_constructor,
                       computed, len(data), hexdigest))
            computed = m.digest()

    def check_blocksize_name(self, name, block_size=0, digest_size=0):
        constructors = self.constructors_to_test[name]
        for hash_object_constructor in constructors:
            m = hash_object_constructor()
            self.assertEqual(m.block_size, block_size)
            self.assertEqual(m.digest_size, digest_size)
            self.assertEqual(len(m.digest()), digest_size)
            self.assertEqual(m.name, name)

    def test_blocksize_name(self):
        self.check_blocksize_name('md5', 64, 16)

    def test_case_md5_0(self):
        self.check('md5', b'', 'd41d8cd98f00b204e9800998ecf8427e')

    def test_case_md5_1(self):
        self.check('md5', b'abc', '900150983cd24fb0d6963f7d28e17f72')

    def test_case_md5_2(self):
        self.check('md5',
                   b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
                   'd174ab98d277d9f5a5611c2c9f419d9f')

    def test_gil(self):
        # Check things work fine with an input larger than the size required
        # for multithreaded operation (which is hardwired to 2048).
        gil_minsize = 2048

        for cons in self.hash_constructors:
            m = cons()
            m.update(b'1')
            m.update(b'#' * gil_minsize)
            m.update(b'1')

            m = cons(b'x' * gil_minsize)
            m.update(b'1')

        m = hashlib.md5()
        m.update(b'1')
        m.update(b'#' * gil_minsize)
        m.update(b'1')
        self.assertEqual(m.hexdigest(), 'cb1e1a2cbc80be75e19935d621fb9b21')

        m = hashlib.md5(b'x' * gil_minsize)
        self.assertEqual(m.hexdigest(), 'cfb767f225d58469c5de3632a8803958')


