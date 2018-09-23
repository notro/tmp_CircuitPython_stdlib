"""
Tests common to genericpath, macpath, ntpath and posixpath
"""

import genericpath
import os
import sys
import unittest
import warnings
from test import support


def safe_rmdir(dirname):
    try:
        os.rmdir(dirname)
    except OSError:
        pass


class GenericTest:
    common_attributes = ['commonprefix', 'getsize', 'getatime', 'getctime',
                         'getmtime', 'exists', 'isdir', 'isfile']
    attributes = []

    def test_no_argument(self):
        for attr in self.common_attributes + self.attributes:
            with self.assertRaises(TypeError):
                getattr(self.pathmodule, attr)()
                raise self.fail("{}.{}() did not raise a TypeError"
                                .format(self.pathmodule.__name__, attr))

    def test_commonprefix(self):
        commonprefix = self.pathmodule.commonprefix
        self.assertEqual(
            commonprefix([]),
            ""
        )
        self.assertEqual(
            commonprefix(["/home/swenson/spam", "/home/swen/spam"]),
            "/home/swen"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/eggs"]),
            "/home/swen/"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/spam"]),
            "/home/swen/spam"
        )
        self.assertEqual(
            commonprefix(["home:swenson:spam", "home:swen:spam"]),
            "home:swen"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:eggs"]),
            ":home:swen:"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:spam"]),
            ":home:swen:spam"
        )

        self.assertEqual(
            commonprefix([b"/home/swenson/spam", b"/home/swen/spam"]),
            b"/home/swen"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/eggs"]),
            b"/home/swen/"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/spam"]),
            b"/home/swen/spam"
        )
        self.assertEqual(
            commonprefix([b"home:swenson:spam", b"home:swen:spam"]),
            b"home:swen"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:eggs"]),
            b":home:swen:"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:spam"]),
            b":home:swen:spam"
        )

        testlist = ['', 'abc', 'Xbcd', 'Xb', 'XY', 'abcd',
                    'aXc', 'abd', 'ab', 'aX', 'abcX']
        for s1 in testlist:
            for s2 in testlist:
                p = commonprefix([s1, s2])
                self.assertTrue(s1.startswith(p))
                self.assertTrue(s2.startswith(p))
                if s1 != s2:
                    n = len(p)
                    self.assertNotEqual(s1[n:n+1], s2[n:n+1])

    def test_getsize(self):
        f = open(support.TESTFN, "wb")
        try:
            f.write(b"foo")
            f.close()
            self.assertEqual(self.pathmodule.getsize(support.TESTFN), 3)
        finally:
            support.unlink(support.TESTFN)

    def test_time(self):
        f = open(support.TESTFN, "wb")
        try:
            f.write(b"foo")
            f.close()
            f = open(support.TESTFN, "ab")
            f.write(b"bar")
            f.close()
            f = open(support.TESTFN, "rb")
            d = f.read()
            f.close()
            self.assertEqual(d, b"foobar")

            self.assertLessEqual(
                self.pathmodule.getctime(support.TESTFN),
                self.pathmodule.getmtime(support.TESTFN)
            )
        finally:
            support.unlink(support.TESTFN)

    def test_exists(self):
        self.assertIs(self.pathmodule.exists(support.TESTFN), False)
        f = open(support.TESTFN, "wb")
        try:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.exists(support.TESTFN), True)
            if not self.pathmodule == genericpath:
                self.assertIs(self.pathmodule.lexists(support.TESTFN),
                              True)
        finally:
            if not f.close():
                f.close()
            support.unlink(support.TESTFN)


    def test_isdir(self):
        self.assertIs(self.pathmodule.isdir(support.TESTFN), False)
        f = open(support.TESTFN, "wb")
        try:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.isdir(support.TESTFN), False)
            os.remove(support.TESTFN)
            os.mkdir(support.TESTFN)
            self.assertIs(self.pathmodule.isdir(support.TESTFN), True)
            os.rmdir(support.TESTFN)
        finally:
            if not f.close():
                f.close()
            support.unlink(support.TESTFN)
            safe_rmdir(support.TESTFN)

    def test_isfile(self):
        self.assertIs(self.pathmodule.isfile(support.TESTFN), False)
        f = open(support.TESTFN, "wb")
        try:
            f.write(b"foo")
            f.close()
            self.assertIs(self.pathmodule.isfile(support.TESTFN), True)
            os.remove(support.TESTFN)
            os.mkdir(support.TESTFN)
            self.assertIs(self.pathmodule.isfile(support.TESTFN), False)
            os.rmdir(support.TESTFN)
        finally:
            if not f.close():
                f.close()
            support.unlink(support.TESTFN)
            safe_rmdir(support.TESTFN)

    @staticmethod
    def _create_file(filename):
        with open(filename, 'wb') as f:
            f.write(b'foo')

    def test_samefile(self):
        try:
            test_fn = support.TESTFN + "1"
            self._create_file(test_fn)
            self.assertTrue(self.pathmodule.samefile(test_fn, test_fn))
            self.assertRaises(TypeError, self.pathmodule.samefile)
        finally:
            os.remove(test_fn)


class TestGenericTest(GenericTest, unittest.TestCase):
    # Issue 16852: GenericTest can't inherit from unittest.TestCase
    # for test discovery purposes; CommonTest inherits from GenericTest
    # and is only meant to be inherited by others.
    pathmodule = genericpath


# Following TestCase is not supposed to be run from test_genericpath.
# It is inherited by other test modules (macpath, ntpath, posixpath).

class CommonTest(GenericTest):
    common_attributes = GenericTest.common_attributes + [
        # Properties
        'curdir', 'pardir', 'extsep', 'sep',
        'pathsep', 'defpath', 'altsep', 'devnull',
        # Methods
        'normcase', 'splitdrive', 'normpath', 'abspath',                        ###
        'join', 'split', 'splitext', 'isabs', 'basename', 'dirname',
        'lexists', 'islink', 'ismount', 'normpath', 'realpath',                 ###
    ]

    def test_normcase(self):
        normcase = self.pathmodule.normcase
        # check that normcase() is idempotent
        for p in ["FoO/./BaR", b"FoO/./BaR"]:
            p = normcase(p)
            self.assertEqual(p, normcase(p))

        self.assertEqual(normcase(''), '')
        self.assertEqual(normcase(b''), b'')

        # check that normcase raises a TypeError for invalid types
        for path in (None, True, 0, 2.5, [], bytearray(b''), {'o','o'}):
            self.assertRaises(TypeError, normcase, path)

    def test_splitdrive(self):
        # splitdrive for non-NT paths
        splitdrive = self.pathmodule.splitdrive
        self.assertEqual(splitdrive("/foo/bar"), ("", "/foo/bar"))
        self.assertEqual(splitdrive("foo:bar"), ("", "foo:bar"))
        self.assertEqual(splitdrive(":foo:bar"), ("", ":foo:bar"))

        self.assertEqual(splitdrive(b"/foo/bar"), (b"", b"/foo/bar"))
        self.assertEqual(splitdrive(b"foo:bar"), (b"", b"foo:bar"))
        self.assertEqual(splitdrive(b":foo:bar"), (b"", b":foo:bar"))


    def test_abspath(self):
        self.assertIn("foo", self.pathmodule.abspath("foo"))
        with warnings.catch_warnings():
            self.assertIn(b"foo", self.pathmodule.abspath(b"foo"))

        # Abspath returns bytes when the arg is bytes
        with warnings.catch_warnings():
            for path in (b'', b'foo', b'f\xf2\xf2', b'/foo', b'C:\\'):
                self.assertIsInstance(self.pathmodule.abspath(path), bytes)

    def test_realpath(self):
        self.assertIn("foo", self.pathmodule.realpath("foo"))
        with warnings.catch_warnings():
            self.assertIn(b"foo", self.pathmodule.realpath(b"foo"))

    def test_normpath_issue5827(self):
        # Make sure normpath preserves unicode
        for path in ('', '.', '/', '\\', '///foo/.//bar//'):
            self.assertIsInstance(self.pathmodule.normpath(path), str)

    def test_abspath_issue3426(self):
        # Check that abspath returns unicode when the arg is unicode
        # with both ASCII and non-ASCII cwds.
        abspath = self.pathmodule.abspath
        for path in ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
            self.assertIsInstance(abspath(path), str)

        unicwd = '\xe7w\xf0'
        try:
            os.fsencode(unicwd)
        except (AttributeError, UnicodeEncodeError):
            # FS encoding is probably ASCII
            pass
        else:
            with support.temp_cwd(unicwd):
                for path in ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
                    self.assertIsInstance(abspath(path), str)

    def test_nonascii_abspath(self):
        if (support.TESTFN_UNDECODABLE
        # Mac OS X denies the creation of a directory with an invalid
        # UTF-8 name. Windows allows to create a directory with an
        # arbitrary bytes name, but fails to enter this directory
        # (when the bytes name is used).
        and sys.platform not in ('win32', 'darwin')):
            name = support.TESTFN_UNDECODABLE
        elif support.TESTFN_NONASCII:
            name = support.TESTFN_NONASCII
        else:
            self.skipTest("need support.TESTFN_NONASCII")

        with warnings.catch_warnings():
            with support.temp_cwd(name):
                self.test_abspath()


