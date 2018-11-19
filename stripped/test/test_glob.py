import glob
import os
import shutil
import sys
import unittest

from test.support import (TESTFN, create_empty_file)                            ###


class GlobTests(unittest.TestCase):

    def norm(self, *parts):
        return os.path.normpath(os.path.join(self.tempdir, *parts))

    def mktemp(self, *parts):
        filename = self.norm(*parts)
        base, file = os.path.split(filename)
        if not os.path.exists(base):
            os.makedirs(base)
        create_empty_file(filename)

    def setUp(self):
        self.tempdir = TESTFN + "_dir"
        shutil.rmtree(self.tempdir, True)                                       ### Keep until mkdir('a/a') is fixed, because setup will fail and not clean up
        self.mktemp('a', 'D')
        self.mktemp('aab', 'F')
        self.mktemp('.aa', 'G')
        self.mktemp('.bb', 'H')
        self.mktemp('aaa', 'zzzF')
        self.mktemp('ZZZ')
        self.mktemp('a', 'bcd', 'EF')
        self.mktemp('a', 'bcd', 'efg', 'ha')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def glob(self, *parts):
        if len(parts) == 1:
            pattern = parts[0]
        else:
            pattern = os.path.join(*parts)
        p = os.path.join(self.tempdir, pattern)
        res = glob.glob(p)
        self.assertEqual(list(glob.iglob(p)), res)
        bres = [os.fsencode(x) for x in res]
        self.assertEqual(glob.glob(os.fsencode(p)), bres)
        self.assertEqual(list(glob.iglob(os.fsencode(p))), bres)
        return res

    def assertSequencesEqual_noorder(self, l1, l2):
        l1 = list(l1)
        l2 = list(l2)
        self.assertEqual(set(l1), set(l2))
        self.assertEqual(sorted(l1), sorted(l2))

    def test_glob_literal(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('a'), [self.norm('a')])
        eq(self.glob('a', 'D'), [self.norm('a', 'D')])
        eq(self.glob('aab'), [self.norm('aab')])
        eq(self.glob('zymurgy'), [])

        res = glob.glob('*')
        self.assertEqual({type(r) for r in res}, {str})
        res = glob.glob(os.path.join(os.curdir, '*'))
        self.assertEqual({type(r) for r in res}, {str})

        res = glob.glob(b'*')
        res = glob.glob(os.path.join(os.fsencode(os.curdir), b'*'))
        self.assertEqual({type(r) for r in res}, {bytes})

    def test_glob_one_directory(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('a*'), map(self.norm, ['a', 'aab', 'aaa']))
        eq(self.glob('.*'), map(self.norm, ['.aa', '.bb']))
        eq(self.glob('?aa'), map(self.norm, ['aaa']))
        eq(self.glob('aa?'), map(self.norm, ['aaa', 'aab']))
        eq(self.glob('aa[ab]'), map(self.norm, ['aaa', 'aab']))
        eq(self.glob('*q'), [])

    def test_glob_nested_directory(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('a', 'bcd', '*g'), [self.norm('a', 'bcd', 'efg')])

    def test_glob_directory_names(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('*', 'D'), [self.norm('a', 'D')])
        eq(self.glob('*', '*a'), [])
        eq(self.glob('a', '*', '*', '*a'),
           [self.norm('a', 'bcd', 'efg', 'ha')])

    def test_glob_directory_with_trailing_slash(self):
        # Patterns ending with a slash shouldn't match non-dirs
        res = glob.glob(self.norm('Z*Z') + os.sep)
        self.assertEqual(res, [])
        res = glob.glob(self.norm('ZZZ') + os.sep)
        self.assertEqual(res, [])
        # When there is a wildcard pattern which ends with os.sep, glob()
        # doesn't blow up.
        res = glob.glob(self.norm('aa*') + os.sep)
        self.assertEqual(len(res), 2)
        # either of these results is reasonable
        self.assertIn(set(res), [
                      {self.norm('aaa'), self.norm('aab')},
                      {self.norm('aaa') + os.sep, self.norm('aab') + os.sep},
                      ])

    def test_glob_bytes_directory_with_trailing_slash(self):
        # Same as test_glob_directory_with_trailing_slash, but with a
        # bytes argument.
        res = glob.glob(os.fsencode(self.norm('Z*Z') + os.sep))
        self.assertEqual(res, [])
        res = glob.glob(os.fsencode(self.norm('ZZZ') + os.sep))
        self.assertEqual(res, [])
        res = glob.glob(os.fsencode(self.norm('aa*') + os.sep))
        self.assertEqual(len(res), 2)
        # either of these results is reasonable
        self.assertIn(set(res), [
                      {os.fsencode(self.norm('aaa')),
                       os.fsencode(self.norm('aab'))},
                      {os.fsencode(self.norm('aaa') + os.sep),
                       os.fsencode(self.norm('aab') + os.sep)},
                      ])

