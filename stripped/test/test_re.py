import re
import sys
import unittest

# Misc tests from Tim Peters' re.doc

# WARNING: Don't change details in these tests if you don't know
# what you're doing. Some of these tests were carefully modeled to
# cover most of the code.

class S(str):
    def __getitem__(self, index):
        return S(super().__getitem__(index))

class B(bytes):
    def __getitem__(self, index):
        return B(super().__getitem__(index))

class ReTests(unittest.TestCase):

    def assertTypedEqual(self, actual, expect, msg=None):
        self.assertEqual(actual, expect, msg)
        def recurse(actual, expect):
            if isinstance(expect, (tuple, list)):
                for x, y in zip(actual, expect):
                    recurse(x, y)
            else:
                self.assertIs(type(actual), type(expect), msg)
        recurse(actual, expect)


    def test_search_star_plus(self):
        self.assertIsNone(re.search('x', 'aaa'))
        self.assertIsNone(re.match('a+', 'xxx'))

    def bump_num(self, matchobj):
        int_value = int(matchobj.group(0))
        return str(int_value + 1)


    def test_re_split(self):
        for string in ":a:b::c", S(":a:b::c"):
            self.assertTypedEqual(re.split(":", string),
                                  ['', 'a', 'b', '', 'c'])
        for a, b, c in ("\xe0\xdf\xe7", "\u0430\u0431\u0432",
                        "\U0001d49c\U0001d49e\U0001d4b5"):
            string = ":%s:%s::%s" % (a, b, c)
            self.assertEqual(re.split(":", string), ['', a, b, '', c])

        self.assertEqual(re.split("(?:b)|(?::+)", ":a:b::c"),
                         ['', 'a', '', '', 'c'])

    def test_qualified_re_split(self):
        self.assertEqual(re.split(":", ":a:b::c", 2), ['', 'a', 'b::c'])
        self.assertEqual(re.split(':', 'a:b:c:d', 2), ['a', 'b', 'c:d'])


    def test_re_match(self):
        for string in 'a', S('a'):
            self.assertEqual(re.match('(a)', string).group(0), 'a')
            self.assertEqual(re.match('(a)', string).group(1), 'a')
        for a in ("\xe0", "\u0430", "\U0001d49c"):
            self.assertEqual(re.match('(%s)' % a, a).group(0), a)
            self.assertEqual(re.match('(%s)' % a, a).group(1), a)


        # A single group
        m = re.match('(a)', 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(1), 'a')




    def test_re_groupref(self):
        self.assertIsNone(re.match(r'^(\|)?([^()]+)\1$', 'a|'))
        self.assertIsNone(re.match(r'^(\|)?([^()]+)\1$', '|a'))


    def test_repeat_minmax(self):
        self.assertIsNone(re.match("^(\w){1}$", "abc"))
        self.assertIsNone(re.match("^(\w){1}?$", "abc"))
        self.assertIsNone(re.match("^(\w){1,2}$", "abc"))
        self.assertIsNone(re.match("^(\w){1,2}?$", "abc"))


        self.assertIsNone(re.match("^x{1}$", "xxx"))
        self.assertIsNone(re.match("^x{1}?$", "xxx"))
        self.assertIsNone(re.match("^x{1,2}$", "xxx"))
        self.assertIsNone(re.match("^x{1,2}?$", "xxx"))


        self.assertIsNone(re.match("^x{}$", "xxx"))
        self.assertTrue(re.match("^x{}$", "x{}"))


    def test_special_escapes(self):
        self.assertEqual(re.search(r"\d\D\w\W\s\S",
                                   "1aa! a").group(0), "1aa! a")
        self.assertEqual(re.search(br"\d\D\w\W\s\S",
                                   b"1aa! a").group(0), b"1aa! a")





    def test_category(self):
        self.assertEqual(re.match(r"(\s)", " ").group(1), " ")


    def test_not_literal(self):
        self.assertEqual(re.search("\s([^a])", " b").group(1), "b")
        self.assertEqual(re.search("\s([^a]*)", " bb").group(1), "bb")

    def test_search_coverage(self):
        self.assertEqual(re.search("\s(b)", " b").group(1), "b")
        self.assertEqual(re.search("a\s", "a ").group(0), "a ")

    def assertMatch(self, pattern, text, match=None, span=None,
                    matcher=re.match):
        if match is None and span is None:
            # the pattern matches the whole text
            match = text
            span = (0, len(text))
        elif match is None or span is None:
            raise ValueError('If match is not None, span should be specified '
                             '(and vice versa).')
        m = matcher(pattern, text)
        self.assertTrue(m)
        self.assertEqual(m.group(0), match)                                     ###


    def test_re_escape_non_ascii(self):
        s = 'xxx\u2620\u2620\u2620xxx'
        s_escaped = re.escape(s)
        self.assertEqual(s_escaped, 'xxx\\\u2620\\\u2620\\\u2620xxx')
        self.assertMatch(s_escaped, s)

    def test_re_escape_non_ascii_bytes(self):
        b = 'y\u2620y\u2620y'.encode('utf-8')
        b_escaped = re.escape(b)
        self.assertEqual(b_escaped, b'y\\\xe2\\\x98\\\xa0y\\\xe2\\\x98\\\xa0y')



    def test_search_dot_unicode(self):
        self.assertTrue(re.search("123.*-", '123abc-'))
        self.assertTrue(re.search("123.*-", '123\xe9-'))
        self.assertTrue(re.search("123.*-", '123\u20ac-'))
        self.assertTrue(re.search("123.*-", '123\U0010ffff-'))
        self.assertTrue(re.search("123.*-", '123\xe9\u20ac\U0010ffff-'))

    def test_compile(self):
        # Test return value when given string and pattern as parameter
        pattern = re.compile('random pattern')
        self.assertIsInstance(pattern, re._pattern_type)
        same_pattern = re.compile(pattern)
        self.assertIsInstance(same_pattern, re._pattern_type)
        self.assertIs(same_pattern, pattern)
        # Test behaviour when not given a string or pattern as parameter
        self.assertRaises(TypeError, re.compile, 0)



