# test the invariant that
#   iff a==b then hash(a)==hash(b)
#
# Also test that hash implementations are inherited as expected

import unittest


class HashEqualityTestCase(unittest.TestCase):

    def same_hash(self, *objlist):
        # Hash each object given and fail if
        # the hash values are not all the same.
        hashed = list(map(hash, objlist))
        for h in hashed[1:]:
            if h != hashed[0]:
                self.fail("hashed values differ: %r" % (objlist,))

    def test_numeric_literals(self):
        self.same_hash(1, 1, 1.0, 1.0+0.0j)
        self.same_hash(0, 0.0, 0.0+0.0j)
        self.same_hash(-1, -1.0, -1.0+0.0j)
        self.same_hash(-2, -2.0, -2.0+0.0j)

    def test_coerced_integers(self):
        self.same_hash(int(1), int(1), float(1), complex(1),
                       int('1'), float('1.0'))
        self.same_hash(int(-2**20), float(-2**20))                              ###
        self.same_hash(int(1-2**20), float(1-2**20))                            ###
        self.same_hash(int(2**20-1), float(2**20-1))                            ###

    def test_coerced_floats(self):
        self.same_hash(int(1.23e3), float(1.23e3))                              ###
        self.same_hash(float(0.5), complex(0.5, 0.0))


class DefaultHash(object): pass

_FIXED_HASH_VALUE = 42
class FixedHash(object):
    def __hash__(self):
        return _FIXED_HASH_VALUE

class OnlyEquality(object):
    def __eq__(self, other):
        return self is other

class OnlyInequality(object):
    def __ne__(self, other):
        return self is not other

class InheritedHashWithEquality(FixedHash, OnlyEquality): pass
class InheritedHashWithInequality(FixedHash, OnlyInequality): pass

class NoHash(object):
    __hash__ = None

class HashInheritanceTestCase(unittest.TestCase):
    default_expected = [object(),
                        DefaultHash(),
                        OnlyInequality(),
                       ]
    fixed_expected = [FixedHash(),
                      InheritedHashWithEquality(),
                      InheritedHashWithInequality(),
                      ]
    error_expected = [NoHash(),
                      OnlyEquality(),
                      ]

    def test_fixed_hash(self):
        for obj in self.fixed_expected:
            self.assertEqual(hash(obj), _FIXED_HASH_VALUE)

    def test_error_hash(self):
        for obj in self.error_expected:
            self.assertRaises(TypeError, hash, obj)

