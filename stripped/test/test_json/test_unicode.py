import unittest                                                                 ###
from collections import OrderedDict
from test.test_json import PyTest, CTest


class TestUnicode:
    # test_encoding1 and test_encoding2 from 2.x are irrelevant (only str
    # is supported as input, not bytes).

    @unittest.expectedFailure                                                   ###
    def test_big_unicode_encode(self):
        u = '\U0001d120'
        self.assertEqual(self.dumps(u), '"\\ud834\\udd20"')

    @unittest.expectedFailure                                                   ###
    def test_big_unicode_decode(self):
        u = 'z\U0001d120x'
        self.assertEqual(self.loads('"' + u + '"'), u)
        self.assertEqual(self.loads('"z\\ud834\\udd20x"'), u)

    def test_unicode_decode(self):
        for i in range(0xd000, 0xd7ff):                                         ### Probably qstr's eating up memory so just try some
            u = chr(i)
            s = '"\\u{0:04x}"'.format(i)
            self.assertEqual(self.loads(s), u)

    def test_unicode_preservation(self):
        self.assertEqual(type(self.loads('""')), str)
        self.assertEqual(type(self.loads('"a"')), str)
        self.assertEqual(type(self.loads('["a"]')[0]), str)

    def test_object_pairs_hook_with_unicode(self):
        s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
        p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4),
             ("qrt", 5), ("pad", 6), ("hoy", 7)]
        self.assertEqual(self.loads(s), eval(s))


class TestCUnicode(TestUnicode, CTest): pass
