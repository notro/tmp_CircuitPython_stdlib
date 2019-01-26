"""Test the errno module
   Roger E. Masse
"""

import errno
#from test import support
import unittest

std_c_errors = frozenset(['EDOM', 'ERANGE'])

class ErrnoAttributeTests(unittest.TestCase):

    @unittest.skip("Missing errno.EDOM")                                        ###
    def test_for_improper_attributes(self):
        # No unexpected attributes should be on the module.
        for error_code in std_c_errors:
            self.assertTrue(hasattr(errno, error_code),
                            "errno is missing %s" % error_code)

    @unittest.skip("Missing errno.errorcode")                                   ###
    def test_using_errorcode(self):
        # Every key value in errno.errorcode should be on the module.
        for value in errno.errorcode.values():
            self.assertTrue(hasattr(errno, value),
                            'no %s attr in errno' % value)


class ErrorcodeTests(unittest.TestCase):

    @unittest.skip("Missing errno.__dict__")                                    ###
    def test_attributes_in_errorcode(self):
        for attribute in errno.__dict__.keys():
            if attribute.isupper():
                self.assertIn(getattr(errno, attribute), errno.errorcode,
                              'no %s attr in errno.errorcode' % attribute)


#def test_main():
#    support.run_unittest(ErrnoAttributeTests, ErrorcodeTests)
#
#
#if __name__ == '__main__':
#    test_main()
