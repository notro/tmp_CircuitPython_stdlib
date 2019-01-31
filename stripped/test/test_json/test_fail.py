import unittest                                                                 ###
from test.test_json import PyTest, CTest
import re

# 2007-10-05
JSONDOCS = [
    # http://json.org/JSON_checker/test/fail1.json
    '"A JSON payload should be an object or array, not a string."',
    # http://json.org/JSON_checker/test/fail3.json
    '{unquoted_key: "keys must be quoted"}',
    # http://json.org/JSON_checker/test/fail7.json
    '["Comma after the close"],',
    # http://json.org/JSON_checker/test/fail8.json
    '["Extra close"]]',
    # http://json.org/JSON_checker/test/fail10.json
    '{"Extra value after close": true} "misplaced quoted value"',
    # http://json.org/JSON_checker/test/fail11.json
    '{"Illegal expression": 1 + 2}',
    # http://json.org/JSON_checker/test/fail12.json
    '{"Illegal invocation": alert()}',
    # http://json.org/JSON_checker/test/fail14.json
    '{"Numbers cannot be hex": 0x14}',
    # http://json.org/JSON_checker/test/fail16.json
    '[\\naked]',
    # http://json.org/JSON_checker/test/fail23.json
    '["Bad value", truth]',
    # http://json.org/JSON_checker/test/fail24.json
    "['single quote']",
    # http://json.org/JSON_checker/test/fail29.json
    '[0e]',
    # http://json.org/JSON_checker/test/fail30.json
    '[0e+]',
    # http://json.org/JSON_checker/test/fail31.json
    '[0e+-1]',
]

SKIPS = {
    1: "why not have a string payload?",
}

class TestFail:
    def test_failures(self):
        for idx, doc in enumerate(JSONDOCS):
            idx = idx + 1
            if idx in SKIPS:
                self.loads(doc)
                continue
            try:
                self.loads(doc)
            except ValueError:
                pass
            else:
                self.fail("Expected failure for fail{0}.json: {1!r}".format(idx, doc))

    @unittest.expectedFailure                                                   ###
    def test_non_string_keys_dict(self):
        data = {'a' : 1, (1, 2) : 2}

        #This is for c encoder
        self.assertRaises(TypeError, self.dumps, data)

        #This is for python encoder
        self.assertRaises(TypeError, self.dumps, data, indent=True)

    @unittest.expectedFailure                                                   ###
    def test_truncated_input(self):
        test_cases = [
            ('', 'Expecting value', 0),
            ('[', 'Expecting value', 1),
            ('[42', "Expecting ',' delimiter", 3),
            ('[42,', 'Expecting value', 4),
            ('["', 'Unterminated string starting at', 1),
            ('["spam', 'Unterminated string starting at', 1),
            ('["spam"', "Expecting ',' delimiter", 7),
            ('["spam",', 'Expecting value', 8),
            ('{', 'Expecting property name enclosed in double quotes', 1),
            ('{"', 'Unterminated string starting at', 1),
            ('{"spam', 'Unterminated string starting at', 1),
            ('{"spam"', "Expecting ':' delimiter", 7),
            ('{"spam":', 'Expecting value', 8),
            ('{"spam":42', "Expecting ',' delimiter", 10),
            ('{"spam":42,', 'Expecting property name enclosed in double quotes', 11),
        ]
        test_cases += [
            ('"', 'Unterminated string starting at', 0),
            ('"spam', 'Unterminated string starting at', 0),
        ]
        for data, msg, idx in test_cases:
            self.assertRaisesRegex(ValueError,
                r'^{0}: line 1 column {1} \(char {2}\)'.format(
                    re.escape(msg), idx + 1, idx),
                self.loads, data)

    @unittest.expectedFailure                                                   ###
    def test_unexpected_data(self):
        test_cases = [
            ('[,', 'Expecting value', 1),
            ('{"spam":[}', 'Expecting value', 9),
            ('[42:', "Expecting ',' delimiter", 3),
            ('[42 "spam"', "Expecting ',' delimiter", 4),
            ('[42,]', 'Expecting value', 4),
            ('{"spam":[42}', "Expecting ',' delimiter", 11),
            ('["]', 'Unterminated string starting at', 1),
            ('["spam":', "Expecting ',' delimiter", 7),
            ('["spam",]', 'Expecting value', 8),
            ('{:', 'Expecting property name enclosed in double quotes', 1),
            ('{,', 'Expecting property name enclosed in double quotes', 1),
            ('{42', 'Expecting property name enclosed in double quotes', 1),
            ('[{]', 'Expecting property name enclosed in double quotes', 2),
            ('{"spam",', "Expecting ':' delimiter", 7),
            ('{"spam"}', "Expecting ':' delimiter", 7),
            ('[{"spam"]', "Expecting ':' delimiter", 8),
            ('{"spam":}', 'Expecting value', 8),
            ('[{"spam":]', 'Expecting value', 9),
            ('{"spam":42 "ham"', "Expecting ',' delimiter", 11),
            ('[{"spam":42]', "Expecting ',' delimiter", 11),
            ('{"spam":42,}', 'Expecting property name enclosed in double quotes', 11),
        ]
        for data, msg, idx in test_cases:
            self.assertRaisesRegex(ValueError,
                r'^{0}: line 1 column {1} \(char {2}\)'.format(
                    re.escape(msg), idx + 1, idx),
                self.loads, data)

    def test_extra_data(self):
        test_cases = [
            ('[]]', 'Extra data', 2),
            ('{}}', 'Extra data', 2),
            ('[],[]', 'Extra data', 2),
            ('{},{}', 'Extra data', 2),
        ]
        test_cases += [
            ('42,"spam"', 'Extra data', 2),
            ('"spam",42', 'Extra data', 6),
        ]
        for data, msg, idx in test_cases:
            self.assertRaisesRegex(ValueError,
                r'syntax error',                                                ###
                self.loads, data)

    def test_linecol(self):
        test_cases = [
            ('!', 1, 1, 0),
            (' !', 1, 2, 1),
            ('\n!', 2, 1, 1),
            ('\n  \n\n     !', 4, 6, 10),
        ]
        for data, line, col, idx in test_cases:
            self.assertRaisesRegex(ValueError,
                r'syntax error',                                                ###
                self.loads, data)

class TestCFail(TestFail, CTest): pass
