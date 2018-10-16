import unittest

import test.string_tests
#import test.buffer_tests

# bytearray doesn't support _any_ of the things tested...                       ###
#class BytearrayPEP3137Test(unittest.TestCase,
#                       test.buffer_tests.MixinBytesBufferCommonTests):
#    def marshal(self, x):
#        return bytearray(x)
#
#    def test_returns_new_copy(self):
#        val = self.marshal(b'1234')
#        # On immutable types these MAY return a reference to themselves
#        # but on mutable types like bytearray they MUST return a new copy.
#        for methname in ('zfill', 'rjust', 'ljust', 'center'):
#            method = getattr(val, methname)
#            newval = method(3)
#            self.assertEqual(val, newval)
#            self.assertTrue(val is not newval,
#                            methname+' returned self on a mutable object')
#        for expr in ('val.split()[0]', 'val.rsplit()[0]',
#                     'val.partition(b".")[0]', 'val.rpartition(b".")[2]',
#                     'val.splitlines()[0]', 'val.replace(b"", b"")'):
#            newval = eval(expr)
#            self.assertEqual(val, newval)
#            self.assertTrue(val is not newval,
#                            expr+' returned val on a mutable object')
#        sep = self.marshal(b'')
#        newval = sep.join([val])
#        self.assertEqual(val, newval)
#        self.assertIsNot(val, newval)
#
#
class FixedStringTest(test.string_tests.BaseTest):

    def fixtype(self, obj):
        if isinstance(obj, str):
            return obj.encode("utf-8")
        return super().fixtype(obj)

    # Currently the bytes containment testing uses a single integer
    # value. This may not be the final design, but until then the
    # bytes section with in a bytes containment not valid
    def test_contains(self):
        pass
    def test_expandtabs(self):
        pass
    def test_upper(self):
        pass
    def test_lower(self):
        pass

class ByteArrayAsStringTest(FixedStringTest, unittest.TestCase):
    type2test = bytearray
    contains_bytes = True
                                                                                ###
    def test_replace(self):                                                     ###
        self.skipTest("FAILS")                                                  ###

class BytesAsStringTest(FixedStringTest, unittest.TestCase):
    type2test = bytes
    contains_bytes = True


class SubclassTest:

    def test_basic(self):
        self.assertTrue(issubclass(self.subclass2test, self.type2test))
        self.assertIsInstance(self.subclass2test(), self.type2test)

        a, b = b"abcd", b"efgh"
        _a, _b = self.subclass2test(a), self.subclass2test(b)

        # test comparison operators with subclass instances
        self.assertTrue(_a == _a)
        self.assertTrue(_a != _b)
#        self.assertTrue(_a < _b)
#        self.assertTrue(_a <= _b)
#        self.assertTrue(_b >= _a)
#        self.assertTrue(_b > _a)
        self.assertTrue(_a is not a)

        # test concat of subclass instances
        self.assertEqual(a + b, _a + _b)
        self.assertEqual(a + b, a + _b)
        self.assertEqual(a + b, _a + b)

        # test repeat
        self.assertTrue(a*5 == _a*5)

#    def test_join(self):
#        # Make sure join returns a NEW object for single item sequences
#        # involving a subclass.
#        # Make sure that it is of the appropriate type.
#        s1 = self.subclass2test(b"abcd")
#        s2 = self.type2test().join([s1])
#        self.assertTrue(s1 is not s2)
#        self.assertTrue(type(s2) is self.type2test, type(s2))
#
#        # Test reverse, calling join on subclass
#        s3 = s1.join([b"abcd"])
#        self.assertTrue(type(s3) is self.type2test)
#
#    def test_pickle(self):
#        a = self.subclass2test(b"abcd")
#        a.x = 10
#        a.y = self.subclass2test(b"efgh")
#        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
#            b = pickle.loads(pickle.dumps(a, proto))
#            self.assertNotEqual(id(a), id(b))
#            self.assertEqual(a, b)
#            self.assertEqual(a.x, b.x)
#            self.assertEqual(a.y, b.y)
#            self.assertEqual(type(a), type(b))
#            self.assertEqual(type(a.y), type(b.y))
#
#    def test_copy(self):
#        a = self.subclass2test(b"abcd")
#        a.x = 10
#        a.y = self.subclass2test(b"efgh")
#        for copy_method in (copy.copy, copy.deepcopy):
#            b = copy_method(a)
#            self.assertNotEqual(id(a), id(b))
#            self.assertEqual(a, b)
#            self.assertEqual(a.x, b.x)
#            self.assertEqual(a.y, b.y)
#            self.assertEqual(type(a), type(b))
#            self.assertEqual(type(a.y), type(b.y))


class ByteArraySubclass(bytearray):
    pass

class BytesSubclass(bytes):
    pass

class OtherBytesSubclass(bytes):
    pass

class ByteArraySubclassTest(SubclassTest, unittest.TestCase):
    type2test = bytearray
    subclass2test = ByteArraySubclass
#
#    def test_init_override(self):
#        class subclass(bytearray):
#            def __init__(me, newarg=1, *args, **kwargs):
#                bytearray.__init__(me, *args, **kwargs)
#        x = subclass(4, b"abcd")
#        x = subclass(4, source=b"abcd")
#        self.assertEqual(x, b"abcd")
#        x = subclass(newarg=4, source=b"abcd")
#        self.assertEqual(x, b"abcd")


class BytesSubclassTest(SubclassTest, unittest.TestCase):
    type2test = bytes
    subclass2test = BytesSubclass


#if __name__ == "__main__":
#    unittest.main()
