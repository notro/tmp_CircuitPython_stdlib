#import contextlib
import io
#import os
#import sys
#import importlib.util
#import time
#import struct
import zipfile
import unittest


from tempfile import TemporaryFile
from random import randint, random, getrandbits

from test.support import (TESTFN, findfile, unlink, rmtree,
#                          requires_zlib, requires_bz2, requires_lzma,
#                          captured_stdout, check_warnings)
                          )                                                     ###

TESTFN2 = TESTFN + "2"
TESTFNDIR = TESTFN + "d"
#FIXEDTEST_SIZE = 1000
FIXEDTEST_SIZE = 10                                                             ###
#DATAFILES_DIR = 'zipfile_datafiles'

#SMALL_TEST_DATA = [('_ziptest1', '1q2w3e4r5t'),
#                   ('ziptest2dir/_ziptest2', 'qawsedrftg'),
#                   ('ziptest2dir/ziptest3dir/_ziptest3', 'azsxdcfvgb'),
#                   ('ziptest2dir/ziptest3dir/ziptest4dir/_ziptest3', '6y7u8i9o0p')]
#
#def getrandbytes(size):
#    return getrandbits(8 * size).to_bytes(size, 'little')

def get_files(test):
    yield TESTFN2
    with TemporaryFile() as f:
        yield f
#        test.assertFalse(f.closed)
# AttributeError: 'BytesIO' object has no attribute 'tell'                      ###
#    with io.BytesIO() as f:
#        yield f
#        test.assertFalse(f.closed)

#def openU(zipfp, fn):
#    with check_warnings(('', DeprecationWarning)):
#        return zipfp.open(fn, 'rU')

class AbstractTestsWithSourceFile:
    @classmethod
    def setUpClass(cls):
        cls.line_gen = [bytes("Zipfile test line %d. random float: %f\n" %
                              (i, random()), "ascii")
                        for i in range(FIXEDTEST_SIZE)]
        cls.data = b''.join(cls.line_gen)

    def setUp(self):
        # Make a source file with some lines
        with open(TESTFN, "wb") as fp:
            fp.write(self.data)

    def make_test_archive(self, f, compression):
        # Create the ZIP archive
        with zipfile.ZipFile(f, "w", compression) as zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)

    def zip_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r", compression) as zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(file=fp)
            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 4) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
#            self.assertTrue(time.strptime(date, '%Y-%m-%d'))
#            self.assertTrue(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename for i in infos]
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            for i in infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            for nm in (TESTFN, "another.name", "strfile"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't raise an exception
            zipfp.testzip()

    def test_basic(self):
        for f in get_files(self):
            self.zip_test(f, self.compression)

    def zip_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r", compression) as zipfp:
            zipdata1 = []
            with zipfp.open(TESTFN) as zipopen1:
                while True:
                    read_data = zipopen1.read(256)
                    if not read_data:
                        break
                    zipdata1.append(read_data)

            zipdata2 = []
            with zipfp.open("another.name") as zipopen2:
                while True:
                    read_data = zipopen2.read(256)
                    if not read_data:
                        break
                    zipdata2.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)
            self.assertEqual(b''.join(zipdata2), self.data)

    def test_open(self):
        for f in get_files(self):
            self.zip_open_test(f, self.compression)

    def zip_random_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r", compression) as zipfp:
            zipdata1 = []
            with zipfp.open(TESTFN) as zipopen1:
                while True:
                    read_data = zipopen1.read(randint(1, 1024))
                    if not read_data:
                        break
                    zipdata1.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)

    def test_random_open(self):
        for f in get_files(self):
            self.zip_random_open_test(f, self.compression)

    def zip_read1_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp, \
             zipfp.open(TESTFN) as zipopen:
            zipdata = []
            while True:
                read_data = zipopen.read1(-1)
                if not read_data:
                    break
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    def test_read1(self):
        for f in get_files(self):
            self.zip_read1_test(f, self.compression)

    def zip_read1_10_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp, \
             zipfp.open(TESTFN) as zipopen:
            zipdata = []
            while True:
                read_data = zipopen.read1(10)
                self.assertLessEqual(len(read_data), 10)
                if not read_data:
                    break
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    def test_read1_10(self):
        for f in get_files(self):
            self.zip_read1_10_test(f, self.compression)

    def zip_readline_read_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp, \
             zipfp.open(TESTFN) as zipopen:
            data = b''
            while True:
                read = zipopen.readline()
                if not read:
                    break
                data += read

                read = zipopen.read(100)
                if not read:
                    break
                data += read

        self.assertEqual(data, self.data)

    def test_readline_read(self):
        # Issue #7610: calls to readline() interleaved with calls to read().
        for f in get_files(self):
            self.zip_readline_read_test(f, self.compression)

    def zip_readline_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp:
            with zipfp.open(TESTFN) as zipopen:
                for line in self.line_gen:
                    linedata = zipopen.readline()
                    self.assertEqual(linedata, line)

    def test_readline(self):
        for f in get_files(self):
            self.zip_readline_test(f, self.compression)

    def zip_readlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp:
            with zipfp.open(TESTFN) as zipopen:
                ziplines = zipopen.readlines()
            for line, zipline in zip(self.line_gen, ziplines):
                self.assertEqual(zipline, line)

    def test_readlines(self):
        for f in get_files(self):
            self.zip_readlines_test(f, self.compression)

    def zip_iterlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r") as zipfp:
            with zipfp.open(TESTFN) as zipopen:
                for line, zipline in zip(self.line_gen, zipopen):
                    self.assertEqual(zipline, line)

    def test_iterlines(self):
        for f in get_files(self):
            self.zip_iterlines_test(f, self.compression)

    def test_low_compression(self):
        """Check for cases where compressed data is larger than original."""
        # Create the ZIP archive
        with zipfile.ZipFile(TESTFN2, "w", self.compression) as zipfp:
            zipfp.writestr("strfile", '12')

        # Get an open object for strfile
        with zipfile.ZipFile(TESTFN2, "r", self.compression) as zipfp:
            with zipfp.open("strfile") as openobj:
                self.assertEqual(openobj.read(1), b'1')
                self.assertEqual(openobj.read(1), b'2')

    def test_writestr_compression(self):
        zipfp = zipfile.ZipFile(TESTFN2, "w")
        zipfp.writestr("b.txt", "hello world", compress_type=self.compression)
        info = zipfp.getinfo('b.txt')
        self.assertEqual(info.compress_type, self.compression)

#    def test_read_return_size(self):
#        # Issue #9837: ZipExtFile.read() shouldn't return more bytes
#        # than requested.
#        for test_size in (1, 4095, 4096, 4097, 16384):
#            file_size = test_size + 1
#            junk = getrandbytes(file_size)
#            with zipfile.ZipFile(io.BytesIO(), "w", self.compression) as zipf:
#                zipf.writestr('foo', junk)
#                with zipf.open('foo', 'r') as fp:
#                    buf = fp.read(test_size)
#                    self.assertEqual(len(buf), test_size)
#
#    def test_truncated_zipfile(self):
#        fp = io.BytesIO()
#        with zipfile.ZipFile(fp, mode='w') as zipf:
#            zipf.writestr('strfile', self.data, compress_type=self.compression)
#            end_offset = fp.tell()
#        zipfiledata = fp.getvalue()
#
#        fp = io.BytesIO(zipfiledata)
#        with zipfile.ZipFile(fp) as zipf:
#            with zipf.open('strfile') as zipopen:
#                fp.truncate(end_offset - 20)
#                with self.assertRaises(EOFError):
#                    zipopen.read()
#
#        fp = io.BytesIO(zipfiledata)
#        with zipfile.ZipFile(fp) as zipf:
#            with zipf.open('strfile') as zipopen:
#                fp.truncate(end_offset - 20)
#                with self.assertRaises(EOFError):
#                    while zipopen.read(100):
#                        pass
#
#        fp = io.BytesIO(zipfiledata)
#        with zipfile.ZipFile(fp) as zipf:
#            with zipf.open('strfile') as zipopen:
#                fp.truncate(end_offset - 20)
#                with self.assertRaises(EOFError):
#                    while zipopen.read1(100):
#                        pass
#
    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


class StoredTestsWithSourceFile(AbstractTestsWithSourceFile,
                                unittest.TestCase):
    compression = zipfile.ZIP_STORED
    test_low_compression = None

#    def zip_test_writestr_permissions(self, f, compression):
#        # Make sure that writestr creates files with mode 0600,
#        # when it is passed a name rather than a ZipInfo instance.
#
#        self.make_test_archive(f, compression)
#        with zipfile.ZipFile(f, "r") as zipfp:
#            zinfo = zipfp.getinfo('strfile')
#            self.assertEqual(zinfo.external_attr, 0o600 << 16)
#
#    def test_writestr_permissions(self):
#        for f in get_files(self):
#            self.zip_test_writestr_permissions(f, zipfile.ZIP_STORED)
#
    def test_absolute_arcnames(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            zipfp.write(TESTFN, "/absolute")

        with zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) as zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

    def test_append_to_zip_file(self):
        """Test appending to an existing zipfile."""
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            zipfp.write(TESTFN, TESTFN)

        with zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) as zipfp:
            zipfp.writestr("strfile", self.data)
            self.assertEqual(zipfp.namelist(), [TESTFN, "strfile"])

    def test_append_to_non_zip_file(self):
        """Test appending to an existing file that is not a zipfile."""
        # NOTE: this test fails if len(d) < 22 because of the first
        # line "fpin.seek(-22, 2)" in _EndRecData
        data = b'I am not a ZipFile!'*10
        with open(TESTFN2, 'wb') as f:
            f.write(data)

        with zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) as zipfp:
            zipfp.write(TESTFN, TESTFN)

        with open(TESTFN2, 'rb') as f:
            f.seek(len(data))
            with zipfile.ZipFile(f, "r") as zipfp:
                self.assertEqual(zipfp.namelist(), [TESTFN])

    def test_ignores_newline_at_end(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            zipfp.write(TESTFN, TESTFN)
        with open(TESTFN2, 'a') as f:
            f.write("\r\n\00\00\00")
        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)

    def test_ignores_stuff_appended_past_comments(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            zipfp.comment = b"this is a comment"
            zipfp.write(TESTFN, TESTFN)
        with open(TESTFN2, 'a') as f:
            f.write("abcdef\r\n")
        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)
            self.assertEqual(zipfp.comment, b"this is a comment")

    def test_write_default_name(self):
        """Check that calling ZipFile.write without arcname specified
        produces the expected result."""
        with zipfile.ZipFile(TESTFN2, "w") as zipfp:
            zipfp.write(TESTFN)
        with zipfile.ZipFile(TESTFN2, "r") as zipfp:                            ### This stays with the test objective but avoids: BadZipFile: Truncated file header
            with open(TESTFN, "rb") as f:
                self.assertEqual(zipfp.read(TESTFN), f.read())

    def test_write_to_readonly(self):
        """Check that trying to call write() on a readonly ZipFile object
        raises a RuntimeError."""
        with zipfile.ZipFile(TESTFN2, mode="w") as zipfp:
            zipfp.writestr("somefile.txt", "bogus")

        with zipfile.ZipFile(TESTFN2, mode="r") as zipfp:
            self.assertRaises(RuntimeError, zipfp.write, TESTFN)

#    def test_add_file_before_1980(self):
#        # Set atime and mtime to 1970-01-01
#        os.utime(TESTFN, (0, 0))
#        with zipfile.ZipFile(TESTFN2, "w") as zipfp:
#            self.assertRaises(ValueError, zipfp.write, TESTFN)
#

#@requires_zlib
#class DeflateTestsWithSourceFile(AbstractTestsWithSourceFile,
#                                 unittest.TestCase):
#    compression = zipfile.ZIP_DEFLATED
#
#    def test_per_file_compression(self):
#        """Check that files within a Zip archive can have different
#        compression options."""
#        with zipfile.ZipFile(TESTFN2, "w") as zipfp:
#            zipfp.write(TESTFN, 'storeme', zipfile.ZIP_STORED)
#            zipfp.write(TESTFN, 'deflateme', zipfile.ZIP_DEFLATED)
#            sinfo = zipfp.getinfo('storeme')
#            dinfo = zipfp.getinfo('deflateme')
#            self.assertEqual(sinfo.compress_type, zipfile.ZIP_STORED)
#            self.assertEqual(dinfo.compress_type, zipfile.ZIP_DEFLATED)
#
#@requires_bz2
#class Bzip2TestsWithSourceFile(AbstractTestsWithSourceFile,
#                               unittest.TestCase):
#    compression = zipfile.ZIP_BZIP2
#
#@requires_lzma
#class LzmaTestsWithSourceFile(AbstractTestsWithSourceFile,
#                              unittest.TestCase):
#    compression = zipfile.ZIP_LZMA
#
#
class AbstractTestZip64InSmallFiles:
    # These tests test the ZIP64 functionality without using large files,
    # see test_zipfile64 for proper tests.

    @classmethod
    def setUpClass(cls):
        line_gen = (bytes("Test of zipfile line %d." % i, "ascii")
                    for i in range(0, FIXEDTEST_SIZE))
        cls.data = b'\n'.join(line_gen)

    def setUp(self):
        self._limit = zipfile.ZIP64_LIMIT
        self._filecount_limit = zipfile.ZIP_FILECOUNT_LIMIT
        zipfile.ZIP64_LIMIT = 1000
        zipfile.ZIP_FILECOUNT_LIMIT = 9

        # Make a source file with some lines
        with open(TESTFN, "wb") as fp:
            fp.write(self.data)

    def zip_test(self, f, compression):
        # Create the ZIP archive
        with zipfile.ZipFile(f, "w", compression, allowZip64=True) as zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r", compression) as zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(fp)

            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 4) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
#            self.assertTrue(time.strptime(date, '%Y-%m-%d'))
#            self.assertTrue(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename for i in infos]
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            for i in infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            for nm in (TESTFN, "another.name", "strfile"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't raise an exception
            zipfp.testzip()

    def test_basic(self):
        for f in get_files(self):
            self.zip_test(f, self.compression)

    def test_too_many_files(self):
        # This test checks that more than 64k files can be added to an archive,
        # and that the resulting archive can be read properly by ZipFile
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=True)
        zipf.debug = 100
        numfiles = 15
        for i in range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles)
        for i in range(numfiles):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def test_too_many_files_append(self):
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=False)
        zipf.debug = 100
        numfiles = 9
        for i in range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        with self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=False)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        with self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=True)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        numfiles2 = 15
        for i in range(numfiles, numfiles2):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles2)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles2)
        for i in range(numfiles2):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    def tearDown(self):
        zipfile.ZIP64_LIMIT = self._limit
        zipfile.ZIP_FILECOUNT_LIMIT = self._filecount_limit
        unlink(TESTFN)
        unlink(TESTFN2)


class StoredTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                  unittest.TestCase):
    compression = zipfile.ZIP_STORED

# Maybe the reduced FIXEDTEST_SIZE prevents this from triggering                ###
#    def large_file_exception_test(self, f, compression):
#        with zipfile.ZipFile(f, "w", compression, allowZip64=False) as zipfp:
#            self.assertRaises(zipfile.LargeZipFile,
#                              zipfp.write, TESTFN, "another.name")
#
#    def large_file_exception_test2(self, f, compression):
#        with zipfile.ZipFile(f, "w", compression, allowZip64=False) as zipfp:
#            self.assertRaises(zipfile.LargeZipFile,
#                              zipfp.writestr, "another.name", self.data)
#
#    def test_large_file_exception(self):
#        for f in get_files(self):
#            self.large_file_exception_test(f, zipfile.ZIP_STORED)
#            self.large_file_exception_test2(f, zipfile.ZIP_STORED)
#
    def test_absolute_arcnames(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED,
                             allowZip64=True) as zipfp:
            zipfp.write(TESTFN, "/absolute")

        with zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) as zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

#@requires_zlib
#class DeflateTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
#                                   unittest.TestCase):
#    compression = zipfile.ZIP_DEFLATED
#
#@requires_bz2
#class Bzip2TestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
#                                 unittest.TestCase):
#    compression = zipfile.ZIP_BZIP2
#
#@requires_lzma
#class LzmaTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
#                                unittest.TestCase):
#    compression = zipfile.ZIP_LZMA
#
#
#class PyZipFileTests(unittest.TestCase):
#    def assertCompiledIn(self, name, namelist):
#        if name + 'o' not in namelist:
#            self.assertIn(name + 'c', namelist)
#
#    def requiresWriteAccess(self, path):
#        # effective_ids unavailable on windows
#        if not os.access(path, os.W_OK,
#                         effective_ids=os.access in os.supports_effective_ids):
#            self.skipTest('requires write access to the installed location')
#        filename = os.path.join(path, 'test_zipfile.try')
#        try:
#            fd = os.open(filename, os.O_WRONLY | os.O_CREAT)
#            os.close(fd)
#        except Exception:
#            self.skipTest('requires write access to the installed location')
#        unlink(filename)
#
#    def test_write_pyfile(self):
#        self.requiresWriteAccess(os.path.dirname(__file__))
#        with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#            fn = __file__
#            if fn.endswith('.pyc') or fn.endswith('.pyo'):
#                path_split = fn.split(os.sep)
#                if os.altsep is not None:
#                    path_split.extend(fn.split(os.altsep))
#                if '__pycache__' in path_split:
#                    fn = importlib.util.source_from_cache(fn)
#                else:
#                    fn = fn[:-1]
#
#            zipfp.writepy(fn)
#
#            bn = os.path.basename(fn)
#            self.assertNotIn(bn, zipfp.namelist())
#            self.assertCompiledIn(bn, zipfp.namelist())
#
#        with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#            fn = __file__
#            if fn.endswith(('.pyc', '.pyo')):
#                fn = fn[:-1]
#
#            zipfp.writepy(fn, "testpackage")
#
#            bn = "%s/%s" % ("testpackage", os.path.basename(fn))
#            self.assertNotIn(bn, zipfp.namelist())
#            self.assertCompiledIn(bn, zipfp.namelist())
#
#    def test_write_python_package(self):
#        import email
#        packagedir = os.path.dirname(email.__file__)
#        self.requiresWriteAccess(packagedir)
#
#        with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#            zipfp.writepy(packagedir)
#
#            # Check for a couple of modules at different levels of the
#            # hierarchy
#            names = zipfp.namelist()
#            self.assertCompiledIn('email/__init__.py', names)
#            self.assertCompiledIn('email/mime/text.py', names)
#
#    def test_write_filtered_python_package(self):
#        import test
#        packagedir = os.path.dirname(test.__file__)
#        self.requiresWriteAccess(packagedir)
#
#        with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#
#            # first make sure that the test folder gives error messages
#            # (on the badsyntax_... files)
#            with captured_stdout() as reportSIO:
#                zipfp.writepy(packagedir)
#            reportStr = reportSIO.getvalue()
#            self.assertTrue('SyntaxError' in reportStr)
#
#            # then check that the filter works on the whole package
#            with captured_stdout() as reportSIO:
#                zipfp.writepy(packagedir, filterfunc=lambda whatever: False)
#            reportStr = reportSIO.getvalue()
#            self.assertTrue('SyntaxError' not in reportStr)
#
#            # then check that the filter works on individual files
#            def filter(path):
#                return not os.path.basename(path).startswith("bad")
#            with captured_stdout() as reportSIO, self.assertWarns(UserWarning):
#                zipfp.writepy(packagedir, filterfunc=filter)
#            reportStr = reportSIO.getvalue()
#            if reportStr:
#                print(reportStr)
#            self.assertTrue('SyntaxError' not in reportStr)
#
#    def test_write_with_optimization(self):
#        import email
#        packagedir = os.path.dirname(email.__file__)
#        self.requiresWriteAccess(packagedir)
#        # use .pyc if running test in optimization mode,
#        # use .pyo if running test in debug mode
#        optlevel = 1 if __debug__ else 0
#        ext = '.pyo' if optlevel == 1 else '.pyc'
#
#        with TemporaryFile() as t, \
#             zipfile.PyZipFile(t, "w", optimize=optlevel) as zipfp:
#            zipfp.writepy(packagedir)
#
#            names = zipfp.namelist()
#            self.assertIn('email/__init__' + ext, names)
#            self.assertIn('email/mime/text' + ext, names)
#
#    def test_write_python_directory(self):
#        os.mkdir(TESTFN2)
#        try:
#            with open(os.path.join(TESTFN2, "mod1.py"), "w") as fp:
#                fp.write("print(42)\n")
#
#            with open(os.path.join(TESTFN2, "mod2.py"), "w") as fp:
#                fp.write("print(42 * 42)\n")
#
#            with open(os.path.join(TESTFN2, "mod2.txt"), "w") as fp:
#                fp.write("bla bla bla\n")
#
#            with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#                zipfp.writepy(TESTFN2)
#
#                names = zipfp.namelist()
#                self.assertCompiledIn('mod1.py', names)
#                self.assertCompiledIn('mod2.py', names)
#                self.assertNotIn('mod2.txt', names)
#
#        finally:
#            rmtree(TESTFN2)
#
#    def test_write_python_directory_filtered(self):
#        os.mkdir(TESTFN2)
#        try:
#            with open(os.path.join(TESTFN2, "mod1.py"), "w") as fp:
#                fp.write("print(42)\n")
#
#            with open(os.path.join(TESTFN2, "mod2.py"), "w") as fp:
#                fp.write("print(42 * 42)\n")
#
#            with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#                zipfp.writepy(TESTFN2, filterfunc=lambda fn:
#                                                  not fn.endswith('mod2.py'))
#
#                names = zipfp.namelist()
#                self.assertCompiledIn('mod1.py', names)
#                self.assertNotIn('mod2.py', names)
#
#        finally:
#            rmtree(TESTFN2)
#
#    def test_write_non_pyfile(self):
#        with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#            with open(TESTFN, 'w') as f:
#                f.write('most definitely not a python file')
#            self.assertRaises(RuntimeError, zipfp.writepy, TESTFN)
#            unlink(TESTFN)
#
#    def test_write_pyfile_bad_syntax(self):
#        os.mkdir(TESTFN2)
#        try:
#            with open(os.path.join(TESTFN2, "mod1.py"), "w") as fp:
#                fp.write("Bad syntax in python file\n")
#
#            with TemporaryFile() as t, zipfile.PyZipFile(t, "w") as zipfp:
#                # syntax errors are printed to stdout
#                with captured_stdout() as s:
#                    zipfp.writepy(os.path.join(TESTFN2, "mod1.py"))
#
#                self.assertIn("SyntaxError", s.getvalue())
#
#                # as it will not have compiled the python file, it will
#                # include the .py file not .pyc or .pyo
#                names = zipfp.namelist()
#                self.assertIn('mod1.py', names)
#                self.assertNotIn('mod1.pyc', names)
#                self.assertNotIn('mod1.pyo', names)
#
#        finally:
#            rmtree(TESTFN2)
#
#
