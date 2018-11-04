import unittest, test.support
import sys, io, os
import struct

# count the number of test runs, used to create unique
# strings to intern in test_intern()
numruns = 0


class SysModuleTest(unittest.TestCase):

    def test_attributes(self):
        self.assertIsInstance(sys.argv, list)
        self.assertIn(sys.byteorder, ("little", "big"))
        self.assertIsInstance(sys.maxsize, int)
        self.assertIsInstance(sys.platform, str)
        self.assertIsInstance(sys.version, str)
        vi = sys.version_info
        self.assertIsInstance(vi[:], tuple)
        self.assertIsInstance(vi[0], int)
        self.assertIsInstance(vi[1], int)
        self.assertIsInstance(vi[2], int)
        self.assertTrue(vi > (1,0,0))

    def test_implementation(self):
        # This test applies to all implementations equally.


        self.assertTrue(hasattr(sys.implementation, 'name'))
        self.assertTrue(hasattr(sys.implementation, 'version'))

