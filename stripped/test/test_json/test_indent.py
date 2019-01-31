import unittest                                                                 ###
from io import StringIO
from test.test_json import PyTest, CTest


class TestIndent:
    @unittest.skip('keyword argument not supported')                            ###
    def test_indent0(self):
        h = {3: 1}
        def check(indent, expected):
            d1 = self.dumps(h, indent=indent)
            self.assertEqual(d1, expected)

            sio = StringIO()
            self.json.dump(h, sio, indent=indent)
            self.assertEqual(sio.getvalue(), expected)

        # indent=0 should emit newlines
        check(0, '{\n"3": 1\n}')
        # indent=None is more compact
        check(None, '{"3": 1}')


class TestCIndent(TestIndent, CTest): pass
