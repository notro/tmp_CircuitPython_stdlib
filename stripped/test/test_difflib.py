import difflib
import unittest
import sys


class TestWithAscii(unittest.TestCase):
    def test_one_insert(self):
        sm = difflib.SequenceMatcher(None, 'b' * 100, 'a' + 'b' * 100)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('insert', 0, 0, 0, 1),
                ('equal', 0, 100, 1, 101)])
        self.assertEqual(sm.bpopular, set())
        sm = difflib.SequenceMatcher(None, 'b' * 100, 'b' * 50 + 'a' + 'b' * 50)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('equal', 0, 50, 0, 50),
                ('insert', 50, 50, 50, 51),
                ('equal', 50, 100, 51, 101)])
        self.assertEqual(sm.bpopular, set())

    def test_one_delete(self):
        sm = difflib.SequenceMatcher(None, 'a' * 40 + 'c' + 'b' * 40, 'a' * 40 + 'b' * 40)
        self.assertAlmostEqual(sm.ratio(), 0.994, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('equal', 0, 40, 0, 40),
                ('delete', 40, 41, 40, 40),
                ('equal', 41, 81, 40, 80)])

    def test_bjunk(self):
        sm = difflib.SequenceMatcher(isjunk=lambda x: x == ' ',
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40)
        self.assertEqual(sm.bjunk, set())

        sm = difflib.SequenceMatcher(isjunk=lambda x: x == ' ',
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40 + ' ' * 20)
        self.assertEqual(sm.bjunk, {' '})

        sm = difflib.SequenceMatcher(isjunk=lambda x: x in [' ', 'b'],
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40 + ' ' * 20)
        self.assertEqual(sm.bjunk, {' ', 'b'})


class TestAutojunk(unittest.TestCase):
    """Tests for the autojunk parameter added in 2.7"""
    def test_one_insert_homogenous_sequence(self):
        # By default autojunk=True and the heuristic kicks in for a sequence
        # of length 200+
        seq1 = 'b' * 200
        seq2 = 'a' + 'b' * 200

        sm = difflib.SequenceMatcher(None, seq1, seq2)
        self.assertAlmostEqual(sm.ratio(), 0, places=3)
        self.assertEqual(sm.bpopular, {'b'})

        # Now turn the heuristic off
        sm = difflib.SequenceMatcher(None, seq1, seq2, autojunk=False)
        self.assertAlmostEqual(sm.ratio(), 0.9975, places=3)
        self.assertEqual(sm.bpopular, set())


class TestSFbugs(unittest.TestCase):
    def test_ratio_for_null_seqn(self):
        # Check clearing of SF bug 763023
        s = difflib.SequenceMatcher(None, [], [])
        self.assertEqual(s.ratio(), 1)
        self.assertEqual(s.quick_ratio(), 1)
        self.assertEqual(s.real_quick_ratio(), 1)

    def test_comparing_empty_lists(self):
        # Check fix for bug #979794
        group_gen = difflib.SequenceMatcher(None, [], []).get_grouped_opcodes()
        self.assertRaises(StopIteration, next, group_gen)
        diff_gen = difflib.unified_diff([], [])
        self.assertRaises(StopIteration, next, diff_gen)

    def test_matching_blocks_cache(self):
        # Issue #21635
        s = difflib.SequenceMatcher(None, "abxcd", "abcd")
        first = s.get_matching_blocks()
        second = s.get_matching_blocks()
        self.assertEqual(second[0].size, 2)
        self.assertEqual(second[1].size, 2)
        self.assertEqual(second[2].size, 0)

    def test_added_tab_hint(self):
        # Check fix for bug #1488943
        diff = list(difflib.Differ().compare(["\tI am a buggy"],["\t\tI am a bug"]))
        self.assertEqual("- \tI am a buggy", diff[0])
        self.assertEqual("?            --\n", diff[1])
        self.assertEqual("+ \t\tI am a bug", diff[2])
        self.assertEqual("? +\n", diff[3])



class TestOutputFormat(unittest.TestCase):
    def test_tab_delimiter(self):
        args = ['one', 'two', 'Original', 'Current',
            '2005-01-26 23:30:50', '2010-04-02 10:20:52']
        ud = difflib.unified_diff(*args, lineterm='')
        self.assertEqual(list(ud)[0:2], [
                           "--- Original\t2005-01-26 23:30:50",
                           "+++ Current\t2010-04-02 10:20:52"])
        cd = difflib.context_diff(*args, lineterm='')
        self.assertEqual(list(cd)[0:2], [
                           "*** Original\t2005-01-26 23:30:50",
                           "--- Current\t2010-04-02 10:20:52"])

    def test_no_trailing_tab_on_empty_filedate(self):
        args = ['one', 'two', 'Original', 'Current']
        ud = difflib.unified_diff(*args, lineterm='')
        self.assertEqual(list(ud)[0:2], ["--- Original", "+++ Current"])

        cd = difflib.context_diff(*args, lineterm='')
        self.assertEqual(list(cd)[0:2], ["*** Original", "--- Current"])

    def test_range_format_unified(self):
        # Per the diff spec at http://www.unix.org/single_unix_specification/
        spec = '''\
           Each <range> field shall be of the form:
             %1d", <beginning line number>  if the range contains exactly one line,
           and:
            "%1d,%1d", <beginning line number>, <number of lines> otherwise.
           If a range is empty, its beginning line number shall be the number of
           the line just before the range, or 0 if the empty range starts the file.
        '''
        fmt = difflib._format_range_unified
        self.assertEqual(fmt(3,3), '3,0')
        self.assertEqual(fmt(3,4), '4')
        self.assertEqual(fmt(3,5), '4,2')
        self.assertEqual(fmt(3,6), '4,3')
        self.assertEqual(fmt(0,0), '0,0')

    def test_range_format_context(self):
        # Per the diff spec at http://www.unix.org/single_unix_specification/
        spec = '''\
           The range of lines in file1 shall be written in the following format
           if the range contains two or more lines:
               "*** %d,%d ****\n", <beginning line number>, <ending line number>
           and the following format otherwise:
               "*** %d ****\n", <ending line number>
           The ending line number of an empty range shall be the number of the preceding line,
           or 0 if the range is at the start of the file.

           Next, the range of lines in file2 shall be written in the following format
           if the range contains two or more lines:
               "--- %d,%d ----\n", <beginning line number>, <ending line number>
           and the following format otherwise:
               "--- %d ----\n", <ending line number>
        '''
        fmt = difflib._format_range_context
        self.assertEqual(fmt(3,3), '3')
        self.assertEqual(fmt(3,4), '4')
        self.assertEqual(fmt(3,5), '4,5')
        self.assertEqual(fmt(3,6), '4,6')
        self.assertEqual(fmt(0,0), '0')

class TestJunkAPIs(unittest.TestCase):
    def test_is_line_junk_true(self):
        for line in ['#', '  ', ' #', '# ', ' # ', '']:
            self.assertTrue(difflib.IS_LINE_JUNK(line), repr(line))

    def test_is_line_junk_false(self):
        for line in ['##', ' ##', '## ', 'abc ', 'abc #', 'Mr. Moose is up!']:
            self.assertFalse(difflib.IS_LINE_JUNK(line), repr(line))


    def test_is_character_junk_true(self):
        for char in [' ', '\t']:
            self.assertTrue(difflib.IS_CHARACTER_JUNK(char), repr(char))

    def test_is_character_junk_false(self):
        for char in ['a', '#', '\n', '\f', '\r', '\v']:
            self.assertFalse(difflib.IS_CHARACTER_JUNK(char), repr(char))

