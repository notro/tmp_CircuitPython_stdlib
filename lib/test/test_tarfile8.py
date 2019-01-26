import os
import io

import unittest
import tarfile

from test import support

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarname = support.findfile("testtar.tar")
tmpname = os.path.join(TEMPDIR, "tmp.tar")

################################################################################
class AppendTestBase:
    # Test append mode (cp. patch #1652681).

    def setUp(self):
        self.tarname = tmpname
        if os.path.exists(self.tarname):
            support.unlink(self.tarname)

    def _create_testtar(self, mode="w:"):
        with tarfile.open(tarname, encoding="iso8859-1") as src:
            t = src.getmember("ustar/regtype")
            t.name = "foo"
            with src.extractfile(t) as f:
                with tarfile.open(self.tarname, mode) as tar:
                    tar.addfile(t, f)

    def test_append_compressed(self):
        self._create_testtar("w:" + self.suffix)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, "a")

class AppendTest(AppendTestBase, unittest.TestCase):
    test_append_compressed = None

    def _add_testfile(self, fileobj=None):
        with tarfile.open(self.tarname, "a", fileobj=fileobj) as tar:
            tar.addfile(tarfile.TarInfo("bar"))

    def _test(self, names=["bar"], fileobj=None):
        with tarfile.open(self.tarname, fileobj=fileobj) as tar:
            self.assertEqual(tar.getnames(), names)

    def test_non_existing(self):
        self._add_testfile()
        self._test()

    def test_empty(self):
        tarfile.open(self.tarname, "w:").close()
        self._add_testfile()
        self._test()

#    def test_empty_fileobj(self):
#        fobj = io.BytesIO(b"\0" * 1024)
#        self._add_testfile(fobj)
#        fobj.seek(0)
#        self._test(fileobj=fobj)
#
    @unittest.skip("Missing BytesIO.tell")                                      ###
    def test_fileobj(self):
        self._create_testtar()
        with open(self.tarname, "rb") as fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(names=["foo", "bar"], fileobj=fobj)

    def test_existing(self):
        self._create_testtar()
        self._add_testfile()
        self._test(names=["foo", "bar"])

    # Append mode is supposed to fail if the tarfile to append to
    # does not end with a zero block.
    def _test_error(self, data):
        with open(self.tarname, "wb") as fobj:
            fobj.write(data)
        self.assertRaises(tarfile.ReadError, self._add_testfile)

    def test_null(self):
        self._test_error(b"")

    def test_incomplete(self):
        self._test_error(b"\0" * 13)

    def test_premature_eof(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data)

    def test_trailing_garbage(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data + b"\0" * 13)

    def test_invalid(self):
        self._test_error(b"a" * 512)

#class GzipAppendTest(GzipTest, AppendTestBase, unittest.TestCase):
#    pass
#
#class Bz2AppendTest(Bz2Test, AppendTestBase, unittest.TestCase):
#    pass
#
#class LzmaAppendTest(LzmaTest, AppendTestBase, unittest.TestCase):
#    pass
#
#
################################################################################

def setUpModule():
    tearDownModule()
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)
