import itertools
import os
import posixpath
import sys
import unittest
import warnings
from posixpath import realpath, abspath, dirname, basename
from test import support, test_genericpath


# An absolute path to a temporary filename for testing. We can't rely on TESTFN
# being an absolute path, so we need this.

ABSTFN = abspath(support.TESTFN)

def skip_if_ABSTFN_contains_backslash(test):
    """
    On Windows, posixpath.abspath still returns paths with backslashes
    instead of posix forward slashes. If this is the case, several tests
    fail, so skip them.
    """
    found_backslash = '\\' in ABSTFN
    msg = "ABSTFN is not a posix path - tests fail"
    return [test, unittest.skip(msg)(test)][found_backslash]

def safe_rmdir(dirname):
    try:
        os.rmdir(dirname)
    except OSError:
        pass

class PosixPathTest(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        for suffix in ["", "1", "2"]:
            support.unlink(support.TESTFN + suffix)
            safe_rmdir(support.TESTFN + suffix)

    def test_join(self):
        self.assertEqual(posixpath.join("/foo", "bar", "/bar", "baz"),
                         "/bar/baz")
        self.assertEqual(posixpath.join("/foo", "bar", "baz"), "/foo/bar/baz")
        self.assertEqual(posixpath.join("/foo/", "bar/", "baz/"),
                         "/foo/bar/baz/")

        self.assertEqual(posixpath.join(b"/foo", b"bar", b"/bar", b"baz"),
                         b"/bar/baz")
        self.assertEqual(posixpath.join(b"/foo", b"bar", b"baz"),
                         b"/foo/bar/baz")
        self.assertEqual(posixpath.join(b"/foo/", b"bar/", b"baz/"),
                         b"/foo/bar/baz/")

    def test_join_errors(self):
        # Check posixpath.join raises friendly TypeErrors.
        errmsg = "Can't mix strings and bytes in path components"
        with self.assertRaisesRegex(TypeError, errmsg):
            posixpath.join('str', b'bytes')
        # regression, see #15377
        with self.assertRaises(TypeError) as cm:
            posixpath.join(None, 'str')
        self.assertNotEqual(cm.exception.args[0], errmsg)

    def test_split(self):
        self.assertEqual(posixpath.split("/foo/bar"), ("/foo", "bar"))
        self.assertEqual(posixpath.split("/"), ("/", ""))
        self.assertEqual(posixpath.split("foo"), ("", "foo"))
        self.assertEqual(posixpath.split("////foo"), ("////", "foo"))
        self.assertEqual(posixpath.split("//foo//bar"), ("//foo", "bar"))

        self.assertEqual(posixpath.split(b"/foo/bar"), (b"/foo", b"bar"))
        self.assertEqual(posixpath.split(b"/"), (b"/", b""))
        self.assertEqual(posixpath.split(b"foo"), (b"", b"foo"))
        self.assertEqual(posixpath.split(b"////foo"), (b"////", b"foo"))
        self.assertEqual(posixpath.split(b"//foo//bar"), (b"//foo", b"bar"))

    def splitextTest(self, path, filename, ext):
        self.assertEqual(posixpath.splitext(path), (filename, ext))
        self.assertEqual(posixpath.splitext("/" + path), ("/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc/" + path),
                         ("abc/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc.def/" + path),
                         ("abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext("/abc.def/" + path),
                         ("/abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(path + "/"),
                         (filename + ext + "/", ""))

        path = bytes(path, "ASCII")
        filename = bytes(filename, "ASCII")
        ext = bytes(ext, "ASCII")

        self.assertEqual(posixpath.splitext(path), (filename, ext))
        self.assertEqual(posixpath.splitext(b"/" + path),
                         (b"/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"abc/" + path),
                         (b"abc/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"abc.def/" + path),
                         (b"abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"/abc.def/" + path),
                         (b"/abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(path + b"/"),
                         (filename + ext + b"/", b""))

    def test_splitext(self):
        self.splitextTest("foo.bar", "foo", ".bar")
        self.splitextTest("foo.boo.bar", "foo.boo", ".bar")
        self.splitextTest("foo.boo.biff.bar", "foo.boo.biff", ".bar")
        self.splitextTest(".csh.rc", ".csh", ".rc")
        self.splitextTest("nodots", "nodots", "")
        self.splitextTest(".cshrc", ".cshrc", "")
        self.splitextTest("...manydots", "...manydots", "")
        self.splitextTest("...manydots.ext", "...manydots", ".ext")
        self.splitextTest(".", ".", "")
        self.splitextTest("..", "..", "")
        self.splitextTest("........", "........", "")
        self.splitextTest("", "", "")

    def test_isabs(self):
        self.assertIs(posixpath.isabs(""), False)
        self.assertIs(posixpath.isabs("/"), True)
        self.assertIs(posixpath.isabs("/foo"), True)
        self.assertIs(posixpath.isabs("/foo/bar"), True)
        self.assertIs(posixpath.isabs("foo/bar"), False)

        self.assertIs(posixpath.isabs(b""), False)
        self.assertIs(posixpath.isabs(b"/"), True)
        self.assertIs(posixpath.isabs(b"/foo"), True)
        self.assertIs(posixpath.isabs(b"/foo/bar"), True)
        self.assertIs(posixpath.isabs(b"foo/bar"), False)

    def test_basename(self):
        self.assertEqual(posixpath.basename("/foo/bar"), "bar")
        self.assertEqual(posixpath.basename("/"), "")
        self.assertEqual(posixpath.basename("foo"), "foo")
        self.assertEqual(posixpath.basename("////foo"), "foo")
        self.assertEqual(posixpath.basename("//foo//bar"), "bar")

        self.assertEqual(posixpath.basename(b"/foo/bar"), b"bar")
        self.assertEqual(posixpath.basename(b"/"), b"")
        self.assertEqual(posixpath.basename(b"foo"), b"foo")
        self.assertEqual(posixpath.basename(b"////foo"), b"foo")
        self.assertEqual(posixpath.basename(b"//foo//bar"), b"bar")

    def test_dirname(self):
        self.assertEqual(posixpath.dirname("/foo/bar"), "/foo")
        self.assertEqual(posixpath.dirname("/"), "/")
        self.assertEqual(posixpath.dirname("foo"), "")
        self.assertEqual(posixpath.dirname("////foo"), "////")
        self.assertEqual(posixpath.dirname("//foo//bar"), "//foo")

        self.assertEqual(posixpath.dirname(b"/foo/bar"), b"/foo")
        self.assertEqual(posixpath.dirname(b"/"), b"/")
        self.assertEqual(posixpath.dirname(b"foo"), b"")
        self.assertEqual(posixpath.dirname(b"////foo"), b"////")
        self.assertEqual(posixpath.dirname(b"//foo//bar"), b"//foo")

    def test_islink(self):
        self.assertIs(posixpath.islink(support.TESTFN + "1"), False)
        self.assertIs(posixpath.lexists(support.TESTFN + "2"), False)
        f = open(support.TESTFN + "1", "wb")
        try:
            f.write(b"foo")
            f.close()
            self.assertIs(posixpath.islink(support.TESTFN + "1"), False)
        finally:
            if not f.close():
                f.close()

    def test_ismount(self):
        self.assertIs(posixpath.ismount("/"), True)
        with warnings.catch_warnings():
            self.assertIs(posixpath.ismount(b"/"), True)

    def test_ismount_non_existent(self):
        # Non-existent mountpoint.
        self.assertIs(posixpath.ismount(ABSTFN), False)
        try:
            os.mkdir(ABSTFN)
            self.assertIs(posixpath.ismount(ABSTFN), False)
        finally:
            safe_rmdir(ABSTFN)


    def test_normpath(self):
        self.assertEqual(posixpath.normpath(""), ".")
        self.assertEqual(posixpath.normpath("/"), "/")
        self.assertEqual(posixpath.normpath("//"), "//")
        self.assertEqual(posixpath.normpath("///"), "/")
        self.assertEqual(posixpath.normpath("///foo/.//bar//"), "/foo/bar")
        self.assertEqual(posixpath.normpath("///foo/.//bar//.//..//.//baz"),
                         "/foo/baz")
        self.assertEqual(posixpath.normpath("///..//./foo/.//bar"), "/foo/bar")

        self.assertEqual(posixpath.normpath(b""), b".")
        self.assertEqual(posixpath.normpath(b"/"), b"/")
        self.assertEqual(posixpath.normpath(b"//"), b"//")
        self.assertEqual(posixpath.normpath(b"///"), b"/")
        self.assertEqual(posixpath.normpath(b"///foo/.//bar//"), b"/foo/bar")
        self.assertEqual(posixpath.normpath(b"///foo/.//bar//.//..//.//baz"),
                         b"/foo/baz")
        self.assertEqual(posixpath.normpath(b"///..//./foo/.//bar"),
                         b"/foo/bar")

    @skip_if_ABSTFN_contains_backslash
    def test_realpath_curdir(self):
        self.assertEqual(realpath('.'), os.getcwd())
        self.assertEqual(realpath('./.'), os.getcwd())
        self.assertEqual(realpath('/'.join(['.'] * 100)), os.getcwd())

        self.assertEqual(realpath(b'.'), os.getcwdb())
        self.assertEqual(realpath(b'./.'), os.getcwdb())
        self.assertEqual(realpath(b'/'.join([b'.'] * 100)), os.getcwdb())

    @skip_if_ABSTFN_contains_backslash
    def test_realpath_pardir(self):
        self.assertEqual(realpath('..'), dirname(os.getcwd()))
        self.assertEqual(realpath('../..'), dirname(dirname(os.getcwd())))
        self.assertEqual(realpath('/'.join(['..'] * 100)), '/')

        self.assertEqual(realpath(b'..'), dirname(os.getcwdb()))
        self.assertEqual(realpath(b'../..'), dirname(dirname(os.getcwdb())))
        self.assertEqual(realpath(b'/'.join([b'..'] * 100)), b'/')


    def test_relpath(self):
        (real_getcwd, os.getcwd) = (os.getcwd, lambda: r"/home/user/bar")
        try:
            curdir = os.path.split(os.getcwd())[-1]
            self.assertRaises(ValueError, posixpath.relpath, "")
            self.assertEqual(posixpath.relpath("a"), "a")
            self.assertEqual(posixpath.relpath(posixpath.abspath("a")), "a")
            self.assertEqual(posixpath.relpath("a/b"), "a/b")
            self.assertEqual(posixpath.relpath("../a/b"), "../a/b")
            self.assertEqual(posixpath.relpath("a", "../b"), "../"+curdir+"/a")
            self.assertEqual(posixpath.relpath("a/b", "../c"),
                             "../"+curdir+"/a/b")
            self.assertEqual(posixpath.relpath("a", "b/c"), "../../a")
            self.assertEqual(posixpath.relpath("a", "a"), ".")
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x/y/z"), '../../../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/foo/bar"), 'bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/"), 'foo/bar/bat')
            self.assertEqual(posixpath.relpath("/", "/foo/bar/bat"), '../../..')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x"), '../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/x", "/foo/bar/bat"), '../../../x')
            self.assertEqual(posixpath.relpath("/", "/"), '.')
            self.assertEqual(posixpath.relpath("/a", "/a"), '.')
            self.assertEqual(posixpath.relpath("/a/b", "/a/b"), '.')
        finally:
            os.getcwd = real_getcwd

    def test_relpath_bytes(self):
        (real_getcwdb, os.getcwdb) = (os.getcwdb, lambda: br"/home/user/bar")
        try:
            curdir = os.path.split(os.getcwdb())[-1]
            self.assertRaises(ValueError, posixpath.relpath, b"")
            self.assertEqual(posixpath.relpath(b"a"), b"a")
            self.assertEqual(posixpath.relpath(posixpath.abspath(b"a")), b"a")
            self.assertEqual(posixpath.relpath(b"a/b"), b"a/b")
            self.assertEqual(posixpath.relpath(b"../a/b"), b"../a/b")
            self.assertEqual(posixpath.relpath(b"a", b"../b"),
                             b"../"+curdir+b"/a")
            self.assertEqual(posixpath.relpath(b"a/b", b"../c"),
                             b"../"+curdir+b"/a/b")
            self.assertEqual(posixpath.relpath(b"a", b"b/c"), b"../../a")
            self.assertEqual(posixpath.relpath(b"a", b"a"), b".")
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/x/y/z"), b'../../../foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/foo/bar"), b'bat')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/"), b'foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/", b"/foo/bar/bat"), b'../../..')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/x"), b'../foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/x", b"/foo/bar/bat"), b'../../../x')
            self.assertEqual(posixpath.relpath(b"/", b"/"), b'.')
            self.assertEqual(posixpath.relpath(b"/a", b"/a"), b'.')
            self.assertEqual(posixpath.relpath(b"/a/b", b"/a/b"), b'.')

            self.assertRaises(TypeError, posixpath.relpath, b"bytes", "str")
            self.assertRaises(TypeError, posixpath.relpath, "str", b"bytes")
        finally:
            os.getcwdb = real_getcwdb


class PosixCommonTest(test_genericpath.CommonTest, unittest.TestCase):
    pathmodule = posixpath
    attributes = ['relpath', 'samefile']                                        ###


