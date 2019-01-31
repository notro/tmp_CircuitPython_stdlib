import unittest                                                                 ###
from test.test_json import PyTest, CTest


class TestDefault:
    @unittest.skip('keyword argument not supported')                            ###
    def test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


class TestCDefault(TestDefault, CTest): pass
