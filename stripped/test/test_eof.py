"""test script for a few new invalid token catches"""

import unittest

class EOFTestCase(unittest.TestCase):
    def test_EOFC(self):
        expect = "invalid syntax"                                               ###
        try:
            eval("""'this is a test\
            """)
        except SyntaxError as msg:
            self.assertEqual(str(msg), expect)
        else:
            raise support.TestFailed

    def test_EOFS(self):
        expect = "invalid syntax"                                               ###
        try:
            eval("""'''this is a test""")
        except SyntaxError as msg:
            self.assertEqual(str(msg), expect)
        else:
            raise support.TestFailed

