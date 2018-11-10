import os
import zipfile
import unittest

from tempfile import TemporaryFile

from test.support import (TESTFN, findfile, unlink, rmtree)

TESTFN2 = TESTFN + "2"

################################################################################
class TestWithDirectory(unittest.TestCase):
    def setUp(self):
###        rmtree(TESTFN2)               #################################################################################
        os.mkdir(TESTFN2)

    def test_extract_dir(self):
        with zipfile.ZipFile(findfile("zipdir.zip")) as zipf:
            zipf.extractall(TESTFN2)
        self.assertTrue(os.path.isdir(os.path.join(TESTFN2, "a")))
        self.assertTrue(os.path.isdir(os.path.join(TESTFN2, "a", "b")))
        self.assertTrue(os.path.exists(os.path.join(TESTFN2, "a", "b", "c")))

    def test_bug_6050(self):
        # Extraction should succeed if directories already exist
        os.mkdir(os.path.join(TESTFN2, "a"))
        self.test_extract_dir()

    def test_write_dir(self):
        dirpath = os.path.join(TESTFN2, "x")
        os.mkdir(dirpath)
        mode = os.stat(dirpath).st_mode & 0xFFFF
        with zipfile.ZipFile(TESTFN, "w") as zipf:
            zipf.write(dirpath)
            zinfo = zipf.filelist[0]
            self.assertTrue(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zipf.write(dirpath, "y")
            zinfo = zipf.filelist[1]
            self.assertTrue(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
        with zipfile.ZipFile(TESTFN, "r") as zipf:
            zinfo = zipf.filelist[0]
            self.assertTrue(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zinfo = zipf.filelist[1]
            self.assertTrue(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertTrue(os.path.isdir(os.path.join(target, "y")))
            self.assertEqual(len(os.listdir(target)), 2)

    def test_writestr_dir(self):
        os.mkdir(os.path.join(TESTFN2, "x"))
        with zipfile.ZipFile(TESTFN, "w") as zipf:
            zipf.writestr("x/", b'')
            zinfo = zipf.filelist[0]
            self.assertEqual(zinfo.filename, "x/")
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
        with zipfile.ZipFile(TESTFN, "r") as zipf:
            zinfo = zipf.filelist[0]
            self.assertTrue(zinfo.filename.endswith("x/"))
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertTrue(os.path.isdir(os.path.join(target, "x")))
            self.assertEqual(os.listdir(target), ["x"])

    def tearDown(self):
        rmtree(TESTFN2)
        if os.path.exists(TESTFN):
            unlink(TESTFN)


#class AbstractUniversalNewlineTests:
#    @classmethod
#    def setUpClass(cls):
#        cls.line_gen = [bytes("Test of zipfile line %d." % i, "ascii")
#                        for i in range(FIXEDTEST_SIZE)]
#        cls.seps = (b'\r', b'\r\n', b'\n')
#        cls.arcdata = {}
#        for n, s in enumerate(cls.seps):
#            cls.arcdata[s] = s.join(cls.line_gen) + s
#
#    def setUp(self):
#        self.arcfiles = {}
#        for n, s in enumerate(self.seps):
#            self.arcfiles[s] = '%s-%d' % (TESTFN, n)
#            with open(self.arcfiles[s], "wb") as f:
#                f.write(self.arcdata[s])
#
#    def make_test_archive(self, f, compression):
#        # Create the ZIP archive
#        with zipfile.ZipFile(f, "w", compression) as zipfp:
#            for fn in self.arcfiles.values():
#                zipfp.write(fn, fn)
#
#    def read_test(self, f, compression):
#        self.make_test_archive(f, compression)
#
#        # Read the ZIP archive
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for sep, fn in self.arcfiles.items():
#                with openU(zipfp, fn) as fp:
#                    zipdata = fp.read()
#                self.assertEqual(self.arcdata[sep], zipdata)
#
#    def test_read(self):
#        for f in get_files(self):
#            self.read_test(f, self.compression)
#
#    def readline_read_test(self, f, compression):
#        self.make_test_archive(f, compression)
#
#        # Read the ZIP archive
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for sep, fn in self.arcfiles.items():
#                with openU(zipfp, fn) as zipopen:
#                    data = b''
#                    while True:
#                        read = zipopen.readline()
#                        if not read:
#                            break
#                        data += read
#
#                        read = zipopen.read(5)
#                        if not read:
#                            break
#                        data += read
#
#            self.assertEqual(data, self.arcdata[b'\n'])
#
#    def test_readline_read(self):
#        for f in get_files(self):
#            self.readline_read_test(f, self.compression)
#
#    def readline_test(self, f, compression):
#        self.make_test_archive(f, compression)
#
#        # Read the ZIP archive
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for sep, fn in self.arcfiles.items():
#                with openU(zipfp, fn) as zipopen:
#                    for line in self.line_gen:
#                        linedata = zipopen.readline()
#                        self.assertEqual(linedata, line + b'\n')
#
#    def test_readline(self):
#        for f in get_files(self):
#            self.readline_test(f, self.compression)
#
#    def readlines_test(self, f, compression):
#        self.make_test_archive(f, compression)
#
#        # Read the ZIP archive
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for sep, fn in self.arcfiles.items():
#                with openU(zipfp, fn) as fp:
#                    ziplines = fp.readlines()
#                for line, zipline in zip(self.line_gen, ziplines):
#                    self.assertEqual(zipline, line + b'\n')
#
#    def test_readlines(self):
#        for f in get_files(self):
#            self.readlines_test(f, self.compression)
#
#    def iterlines_test(self, f, compression):
#        self.make_test_archive(f, compression)
#
#        # Read the ZIP archive
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for sep, fn in self.arcfiles.items():
#                with openU(zipfp, fn) as fp:
#                    for line, zipline in zip(self.line_gen, fp):
#                        self.assertEqual(zipline, line + b'\n')
#
#    def test_iterlines(self):
#        for f in get_files(self):
#            self.iterlines_test(f, self.compression)
#
#    def tearDown(self):
#        for sep, fn in self.arcfiles.items():
#            unlink(fn)
#        unlink(TESTFN)
#        unlink(TESTFN2)
#
#
#class StoredUniversalNewlineTests(AbstractUniversalNewlineTests,
#                                  unittest.TestCase):
#    compression = zipfile.ZIP_STORED
#
#@requires_zlib
#class DeflateUniversalNewlineTests(AbstractUniversalNewlineTests,
#                                   unittest.TestCase):
#    compression = zipfile.ZIP_DEFLATED
#
#@requires_bz2
#class Bzip2UniversalNewlineTests(AbstractUniversalNewlineTests,
#                                 unittest.TestCase):
#    compression = zipfile.ZIP_BZIP2
#
#@requires_lzma
#class LzmaUniversalNewlineTests(AbstractUniversalNewlineTests,
#                                unittest.TestCase):
#    compression = zipfile.ZIP_LZMA
#
#if __name__ == "__main__":
#    unittest.main()
