import test.support; test.support.import_module('binascii')                     ###
import os
import zipfile
import unittest

from tempfile import TemporaryFile
from random import randint, random, getrandbits

from test.support import (TESTFN, findfile, unlink, rmtree)

TESTFN2 = TESTFN + "2"
#FIXEDTEST_SIZE = 1000
FIXEDTEST_SIZE = 10                                                             ###

SMALL_TEST_DATA = [('_ziptest1', '1q2w3e4r5t'),
                   ('ziptest2dir/_ziptest2', 'qawsedrftg'),
                   ('ziptest2dir/ziptest3dir/_ziptest3', 'azsxdcfvgb'),
                   ('ziptest2dir/ziptest3dir/ziptest4dir/_ziptest3', '6y7u8i9o0p')]

def getrandbytes(size):
    return getrandbits(8 * size).to_bytes(size, 'little')

def get_files(test):
    yield TESTFN2
    with TemporaryFile() as f:
        yield f
#        test.assertFalse(f.closed)
# AttributeError: 'BytesIO' object has no attribute 'tell'                      ###
#    with io.BytesIO() as f:
#        yield f
#        test.assertFalse(f.closed)

################################################################################
class ExtractTests(unittest.TestCase):
    def test_extract(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            for fpath, fdata in SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            for fpath, fdata in SMALL_TEST_DATA:
                writtenfile = zipfp.extract(fpath)

                # make sure it was written to the right place
                correctfile = os.path.join(os.getcwd(), fpath)
                correctfile = os.path.normpath(correctfile)

                self.assertEqual(writtenfile, correctfile)

                # make sure correct data is in correct file
                with open(writtenfile, "rb") as f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(writtenfile)

        # remove the test file subdirectories
        rmtree(os.path.join(os.getcwd(), 'ziptest2dir'))

    def test_extract_all(self):
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            for fpath, fdata in SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            zipfp.extractall()
            for fpath, fdata in SMALL_TEST_DATA:
                outfile = os.path.join(os.getcwd(), fpath)

                with open(outfile, "rb") as f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(outfile)

        # remove the test file subdirectories
        rmtree(os.path.join(os.getcwd(), 'ziptest2dir'))

    def check_file(self, filename, content):
        self.assertTrue(os.path.isfile(filename))
        with open(filename, 'rb') as f:
            self.assertEqual(f.read(), content)

#    def test_sanitize_windows_name(self):
#        san = zipfile.ZipFile._sanitize_windows_name
#        # Passing pathsep in allows this test to work regardless of platform.
#        self.assertEqual(san(r',,?,C:,foo,bar/z', ','), r'_,C_,foo,bar/z')
#        self.assertEqual(san(r'a\b,c<d>e|f"g?h*i', ','), r'a\b,c_d_e_f_g_h_i')
#        self.assertEqual(san('../../foo../../ba..r', '/'), r'foo/ba..r')
#
    def test_extract_hackers_arcnames_common_cases(self):
        common_hacknames = [
            ('../foo/bar', 'foo/bar'),
            ('foo/../bar', 'foo/bar'),
            ('foo/../../bar', 'foo/bar'),
            ('foo/bar/..', 'foo/bar'),
            ('./../foo/bar', 'foo/bar'),
            ('/foo/bar', 'foo/bar'),
            ('/foo/../bar', 'foo/bar'),
            ('/foo/../../bar', 'foo/bar'),
        ]
        self._test_extract_hackers_arcnames(common_hacknames)

#    @unittest.skipIf(os.path.sep != '\\', 'Requires \\ as path separator.')
#    def test_extract_hackers_arcnames_windows_only(self):
#        """Test combination of path fixing and windows name sanitization."""
#        windows_hacknames = [
#            (r'..\foo\bar', 'foo/bar'),
#            (r'..\/foo\/bar', 'foo/bar'),
#            (r'foo/\..\/bar', 'foo/bar'),
#            (r'foo\/../\bar', 'foo/bar'),
#            (r'C:foo/bar', 'foo/bar'),
#            (r'C:/foo/bar', 'foo/bar'),
#            (r'C://foo/bar', 'foo/bar'),
#            (r'C:\foo\bar', 'foo/bar'),
#            (r'//conky/mountpoint/foo/bar', 'foo/bar'),
#            (r'\\conky\mountpoint\foo\bar', 'foo/bar'),
#            (r'///conky/mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
#            (r'\\\conky\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
#            (r'//conky//mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
#            (r'\\conky\\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
#            (r'//?/C:/foo/bar', 'foo/bar'),
#            (r'\\?\C:\foo\bar', 'foo/bar'),
#            (r'C:/../C:/foo/bar', 'C_/foo/bar'),
#            (r'a:b\c<d>e|f"g?h*i', 'b/c_d_e_f_g_h_i'),
#            ('../../foo../../ba..r', 'foo/ba..r'),
#        ]
#        self._test_extract_hackers_arcnames(windows_hacknames)
#
#    @unittest.skipIf(os.path.sep != '/', r'Requires / as path separator.')
    def test_extract_hackers_arcnames_posix_only(self):
        posix_hacknames = [
            ('//foo/bar', 'foo/bar'),
            ('../../foo../../ba..r', 'foo../ba..r'),
            (r'foo/..\bar', r'foo/..\bar'),
        ]
        self._test_extract_hackers_arcnames(posix_hacknames)

    def _test_extract_hackers_arcnames(self, hacknames):
        for arcname, fixedname in hacknames:
            content = b'foobar' + arcname.encode()
            with zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_STORED) as zipfp:
                zinfo = zipfile.ZipInfo()
                # preserve backslashes
                zinfo.filename = arcname
                zinfo.external_attr = 0o600 << 16
                zipfp.writestr(zinfo, content)

            arcname = arcname.replace(os.sep, "/")
            targetpath = os.path.join('target', 'subdir', 'subsub')
            correctfile = os.path.join(targetpath, *fixedname.split('/'))

            with zipfile.ZipFile(TESTFN2, 'r') as zipfp:
                writtenfile = zipfp.extract(arcname, targetpath)
                self.assertEqual(writtenfile, correctfile,
                                 msg='extract %r: %r != %r' %
                                 (arcname, writtenfile, correctfile))
            self.check_file(correctfile, content)
            rmtree('target')

            with zipfile.ZipFile(TESTFN2, 'r') as zipfp:
                zipfp.extractall(targetpath)
            self.check_file(correctfile, content)
            rmtree('target')

            correctfile = os.path.join(os.getcwd(), *fixedname.split('/'))

            with zipfile.ZipFile(TESTFN2, 'r') as zipfp:
                writtenfile = zipfp.extract(arcname)
                self.assertEqual(writtenfile, correctfile,
                                 msg="extract %r" % arcname)
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            with zipfile.ZipFile(TESTFN2, 'r') as zipfp:
                zipfp.extractall()
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            unlink(TESTFN2)


class OtherTests(unittest.TestCase):
    def test_open_via_zip_info(self):
        # Create the ZIP archive
        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) as zipfp:
            zipfp.writestr("name", "foo")
#            with self.assertWarns(UserWarning):
            if True:                                                            ###
                zipfp.writestr("name", "bar")
            self.assertEqual(zipfp.namelist(), ["name"] * 2)

        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            infos = zipfp.infolist()
            data = b""
            for info in infos:
                with zipfp.open(info) as zipopen:
                    data += zipopen.read()
            self.assertIn(data, {b"foobar", b"barfoo"})
            data = b""
            for info in infos:
                data += zipfp.read(info)
            self.assertIn(data, {b"foobar", b"barfoo"})

#    def test_universal_deprecation(self):
#        f = io.BytesIO()
#        with zipfile.ZipFile(f, "w") as zipfp:
#            zipfp.writestr('spam.txt', b'ababagalamaga')
#
#        with zipfile.ZipFile(f, "r") as zipfp:
#            for mode in 'U', 'rU':
#                with self.assertWarns(DeprecationWarning):
#                    zipopen = zipfp.open('spam.txt', mode)
#                zipopen.close()
#
#    def test_universal_readaheads(self):
#        f = io.BytesIO()
#
#        data = b'a\r\n' * 16 * 1024
#        with zipfile.ZipFile(f, 'w', zipfile.ZIP_STORED) as zipfp:
#            zipfp.writestr(TESTFN, data)
#
#        data2 = b''
#        with zipfile.ZipFile(f, 'r') as zipfp, \
#             openU(zipfp, TESTFN) as zipopen:
#            for line in zipopen:
#                data2 += line
#
#        self.assertEqual(data, data2.replace(b'\n', b'\r\n'))
#
    def test_writestr_extended_local_header_issue1202(self):
        with zipfile.ZipFile(TESTFN2, 'w') as orig_zip:
            for data in 'abcdefghijklmnop':
                zinfo = zipfile.ZipInfo(data)
                zinfo.flag_bits |= 0x08  # Include an extended local header.
                orig_zip.writestr(zinfo, data)

    def test_close(self):
        """Check that the zipfile is closed after the 'with' block."""
        with zipfile.ZipFile(TESTFN2, "w") as zipfp:
            for fpath, fdata in SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)
                self.assertIsNotNone(zipfp.fp, 'zipfp is not open')
        self.assertIsNone(zipfp.fp, 'zipfp is not closed')

        with zipfile.ZipFile(TESTFN2, "r") as zipfp:
            self.assertIsNotNone(zipfp.fp, 'zipfp is not open')
        self.assertIsNone(zipfp.fp, 'zipfp is not closed')

    def test_close_on_exception(self):
        """Check that the zipfile is closed if an exception is raised in the
        'with' block."""
        with zipfile.ZipFile(TESTFN2, "w") as zipfp:
            for fpath, fdata in SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        try:
            with zipfile.ZipFile(TESTFN2, "r") as zipfp2:
                raise zipfile.BadZipFile()
        except zipfile.BadZipFile:
            self.assertIsNone(zipfp2.fp, 'zipfp is not closed')

#    def test_unsupported_version(self):
#        # File has an extract_version of 120
#        data = (b'PK\x03\x04x\x00\x00\x00\x00\x00!p\xa1@\x00\x00\x00\x00\x00\x00'
#                b'\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00xPK\x01\x02x\x03x\x00\x00\x00\x00'
#                b'\x00!p\xa1@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00'
#                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00xPK\x05\x06'
#                b'\x00\x00\x00\x00\x01\x00\x01\x00/\x00\x00\x00\x1f\x00\x00\x00\x00\x00')
#
#        self.assertRaises(NotImplementedError, zipfile.ZipFile,
#                          io.BytesIO(data), 'r')
#
#    @requires_zlib
#    def test_read_unicode_filenames(self):
#        # bug #10801
#        fname = findfile('zip_cp437_header.zip')
#        with zipfile.ZipFile(fname) as zipfp:
#            for name in zipfp.namelist():
#                zipfp.open(name).close()
#
    def test_write_unicode_filenames(self):
        with zipfile.ZipFile(TESTFN, "w") as zf:
            zf.writestr("foo.txt", "Test for unicode filename")
            zf.writestr("\xf6.txt", "Test for unicode filename")
            self.assertIsInstance(zf.infolist()[0].filename, str)

        with zipfile.ZipFile(TESTFN, "r") as zf:
            self.assertEqual(zf.filelist[0].filename, "foo.txt")
            self.assertEqual(zf.filelist[1].filename, "\xf6.txt")

    def test_create_non_existent_file_for_append(self):
        if os.path.exists(TESTFN):
            os.unlink(TESTFN)

        filename = 'testfile.txt'
        content = b'hello, world. this is some content.'

        try:
            with zipfile.ZipFile(TESTFN, 'a') as zf:
                zf.writestr(filename, content)
        except OSError:
            self.fail('Could not append data to a non-existent zip file.')

        self.assertTrue(os.path.exists(TESTFN))

        with zipfile.ZipFile(TESTFN, 'r') as zf:
            self.assertEqual(zf.read(filename), content)

    def test_close_erroneous_file(self):
        # This test checks that the ZipFile constructor closes the file object
        # it opens if there's an error in the file.  If it doesn't, the
        # traceback holds a reference to the ZipFile object and, indirectly,
        # the file object.
        # On Windows, this causes the os.unlink() call to fail because the
        # underlying file is still open.  This is SF bug #412214.
        #
        with open(TESTFN, "w") as fp:
            fp.write("this is not a legal zip file\n")
        try:
            zf = zipfile.ZipFile(TESTFN)
        except zipfile.BadZipFile:
            pass

    def test_is_zip_erroneous_file(self):
        """Check that is_zipfile() correctly identifies non-zip files."""
        # - passing a filename
        with open(TESTFN, "w") as fp:
            fp.write("this is not a legal zip file\n")
        self.assertFalse(zipfile.is_zipfile(TESTFN))
        # - passing a file object
        with open(TESTFN, "rb") as fp:
            self.assertFalse(zipfile.is_zipfile(fp))
#        # - passing a file-like object
#        fp = io.BytesIO()
#        fp.write(b"this is not a legal zip file\n")
#        self.assertFalse(zipfile.is_zipfile(fp))
#        fp.seek(0, 0)
#        self.assertFalse(zipfile.is_zipfile(fp))

#    def test_damaged_zipfile(self):
#        """Check that zipfiles with missing bytes at the end raise BadZipFile."""
#        # - Create a valid zip file
#        fp = io.BytesIO()
#        with zipfile.ZipFile(fp, mode="w") as zipf:
#            zipf.writestr("foo.txt", b"O, for a Muse of Fire!")
#        zipfiledata = fp.getvalue()
#
#        # - Now create copies of it missing the last N bytes and make sure
#        #   a BadZipFile exception is raised when we try to open it
#        for N in range(len(zipfiledata)):
#            fp = io.BytesIO(zipfiledata[:N])
#            self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, fp)
#
    def test_is_zip_valid_file(self):
        """Check that is_zipfile() correctly identifies zip files."""
        # - passing a filename
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            zipf.writestr("foo.txt", b"O, for a Muse of Fire!")

        self.assertTrue(zipfile.is_zipfile(TESTFN))
        # - passing a file object
        with open(TESTFN, "rb") as fp:
            self.assertTrue(zipfile.is_zipfile(fp))
            fp.seek(0, 0)
            zip_contents = fp.read()
#        # - passing a file-like object
#        fp = io.BytesIO()
#        fp.write(zip_contents)
#        self.assertTrue(zipfile.is_zipfile(fp))
#        fp.seek(0, 0)
#        self.assertTrue(zipfile.is_zipfile(fp))

#    def test_non_existent_file_raises_OSError(self):
#        # make sure we don't raise an AttributeError when a partially-constructed
#        # ZipFile instance is finalized; this tests for regression on SF tracker
#        # bug #403871.
#
#        # The bug we're testing for caused an AttributeError to be raised
#        # when a ZipFile instance was created for a file that did not
#        # exist; the .fp member was not initialized but was needed by the
#        # __del__() method.  Since the AttributeError is in the __del__(),
#        # it is ignored, but the user should be sufficiently annoyed by
#        # the message on the output that regression will be noticed
#        # quickly.
#        self.assertRaises(OSError, zipfile.ZipFile, TESTFN)
#
    def test_empty_file_raises_BadZipFile(self):
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

        with open(TESTFN, 'w') as fp:
            fp.write("short file")
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

#    def test_closed_zip_raises_RuntimeError(self):
#        """Verify that testzip() doesn't swallow inappropriate exceptions."""
#        data = io.BytesIO()
#        with zipfile.ZipFile(data, mode="w") as zipf:
#            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
#
#        # This is correct; calling .read on a closed ZipFile should raise
#        # a RuntimeError, and so should calling .testzip.  An earlier
#        # version of .testzip would swallow this exception (and any other)
#        # and report that the first file in the archive was corrupt.
#        self.assertRaises(RuntimeError, zipf.read, "foo.txt")
#        self.assertRaises(RuntimeError, zipf.open, "foo.txt")
#        self.assertRaises(RuntimeError, zipf.testzip)
#        self.assertRaises(RuntimeError, zipf.writestr, "bogus.txt", "bogus")
#        with open(TESTFN, 'w') as f:
#            f.write('zipfile test data')
#        self.assertRaises(RuntimeError, zipf.write, TESTFN)
#
    def test_bad_constructor_mode(self):
        """Check that bad modes passed to ZipFile constructor are caught."""
        self.assertRaises(RuntimeError, zipfile.ZipFile, TESTFN, "q")

    def test_bad_open_mode(self):
        """Check that bad modes passed to ZipFile.open are caught."""
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")

        with zipfile.ZipFile(TESTFN, mode="r") as zipf:
        # read the data to make sure the file is there
            zipf.read("foo.txt")
            self.assertRaises(RuntimeError, zipf.open, "foo.txt", "q")

    def test_read0(self):
        """Check that calling read(0) on a ZipExtFile object returns an empty
        string and doesn't advance file pointer."""
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
            # read the data to make sure the file is there
            with zipf.open("foo.txt") as f:
                for i in range(FIXEDTEST_SIZE):
                    self.assertEqual(f.read(0), b'')

                self.assertEqual(f.read(), b"O, for a Muse of Fire!")

    def test_open_non_existent_item(self):
        """Check that attempting to call open() for an item that doesn't
        exist in the archive raises a RuntimeError."""
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            self.assertRaises(KeyError, zipf.open, "foo.txt", "r")

    def test_bad_compression_mode(self):
        """Check that bad compression methods passed to ZipFile.open are
        caught."""
        self.assertRaises(RuntimeError, zipfile.ZipFile, TESTFN, "w", -1)

#    def test_unsupported_compression(self):
#        # data is declared as shrunk, but actually deflated
#        data = (b'PK\x03\x04.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00'
#                b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00x\x03\x00PK\x01'
#                b'\x02.\x03.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00\x00\x02\x00\x00'
#                b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#                b'\x80\x01\x00\x00\x00\x00xPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00'
#                b'/\x00\x00\x00!\x00\x00\x00\x00\x00')
#        with zipfile.ZipFile(io.BytesIO(data), 'r') as zipf:
#            self.assertRaises(NotImplementedError, zipf.open, 'x')
#
    def test_null_byte_in_filename(self):
        """Check that a filename containing a null byte is properly
        terminated."""
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            zipf.writestr("foo.txt\x00qqq", b"O, for a Muse of Fire!")
            self.assertEqual(zipf.namelist(), ['foo.txt'])

    def test_struct_sizes(self):
        """Check that ZIP internal structure sizes are calculated correctly."""
        self.assertEqual(zipfile.sizeEndCentDir, 22)
        self.assertEqual(zipfile.sizeCentralDir, 46)
        self.assertEqual(zipfile.sizeEndCentDir64, 56)
        self.assertEqual(zipfile.sizeEndCentDir64Locator, 20)

    def test_comments(self):
        """Check that comments on the archive are handled properly."""

        # check default comment is empty
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            self.assertEqual(zipf.comment, b'')
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")

        with zipfile.ZipFile(TESTFN, mode="r") as zipfr:
            self.assertEqual(zipfr.comment, b'')

        # check a simple short comment
        comment = b'Bravely taking to his feet, he beat a very brave retreat.'
        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
            zipf.comment = comment
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
        with zipfile.ZipFile(TESTFN, mode="r") as zipfr:
            self.assertEqual(zipf.comment, comment)

#        # check a comment of max length
#        comment2 = ''.join(['%d' % (i**3 % 10) for i in range((1 << 16)-1)])
#        comment2 = comment2.encode("ascii")
#        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
#            zipf.comment = comment2
#            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
#
#        with zipfile.ZipFile(TESTFN, mode="r") as zipfr:
#            self.assertEqual(zipfr.comment, comment2)
#
#        # check a comment that is too long is truncated
#        with zipfile.ZipFile(TESTFN, mode="w") as zipf:
#            with self.assertWarns(UserWarning):
#                zipf.comment = comment2 + b'oops'
#            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
#        with zipfile.ZipFile(TESTFN, mode="r") as zipfr:
#            self.assertEqual(zipfr.comment, comment2)
#
        # check that comments are correctly modified in append mode
        with zipfile.ZipFile(TESTFN,mode="w") as zipf:
            zipf.comment = b"original comment"
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
        with zipfile.ZipFile(TESTFN,mode="a") as zipf:
            zipf.comment = b"an updated comment"
        with zipfile.ZipFile(TESTFN,mode="r") as zipf:
            self.assertEqual(zipf.comment, b"an updated comment")

        # check that comments are correctly shortened in append mode
        with zipfile.ZipFile(TESTFN,mode="w") as zipf:
            zipf.comment = b"original comment that's longer"
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
        with zipfile.ZipFile(TESTFN,mode="a") as zipf:
            zipf.comment = b"shorter comment"
        with zipfile.ZipFile(TESTFN,mode="r") as zipf:
            self.assertEqual(zipf.comment, b"shorter comment")

    def test_unicode_comment(self):
        with zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) as zipf:
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
            with self.assertRaises(TypeError):
                zipf.comment = "this is an error"

    def test_change_comment_in_empty_archive(self):
        with zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) as zipf:
            self.assertFalse(zipf.filelist)
            zipf.comment = b"this is a comment"
        with zipfile.ZipFile(TESTFN, "r") as zipf:
            self.assertEqual(zipf.comment, b"this is a comment")

    def test_change_comment_in_nonempty_archive(self):
        with zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) as zipf:
            zipf.writestr("foo.txt", "O, for a Muse of Fire!")
        with zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) as zipf:
            self.assertTrue(zipf.filelist)
            zipf.comment = b"this is a comment"
        with zipfile.ZipFile(TESTFN, "r") as zipf:
            self.assertEqual(zipf.comment, b"this is a comment")

    def test_empty_zipfile(self):
        # Check that creating a file in 'w' or 'a' mode and closing without
        # adding any files to the archives creates a valid empty ZIP file
        zipf = zipfile.ZipFile(TESTFN, mode="w")
        zipf.close()
        try:
            zipf = zipfile.ZipFile(TESTFN, mode="r")
        except zipfile.BadZipFile:
            self.fail("Unable to create empty ZIP file in 'w' mode")
#
#        zipf = zipfile.ZipFile(TESTFN, mode="a")
#        zipf.close()
#        try:
#            zipf = zipfile.ZipFile(TESTFN, mode="r")
#        except:
#            self.fail("Unable to create empty ZIP file in 'a' mode")

    def test_open_empty_file(self):
        # Issue 1710703: Check that opening a file with less than 22 bytes
        # raises a BadZipFile exception (rather than the previously unhelpful
        # OSError)
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN, 'r')

    def test_create_zipinfo_before_1980(self):
        self.assertRaises(ValueError,
                          zipfile.ZipInfo, 'seventies', (1979, 1, 1, 0, 0, 0))

#    def test_zipfile_with_short_extra_field(self):
#        """If an extra field in the header is less than 4 bytes, skip it."""
#        zipdata = (
#            b'PK\x03\x04\x14\x00\x00\x00\x00\x00\x93\x9b\xad@\x8b\x9e'
#            b'\xd9\xd3\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x03\x00ab'
#            b'c\x00\x00\x00APK\x01\x02\x14\x03\x14\x00\x00\x00\x00'
#            b'\x00\x93\x9b\xad@\x8b\x9e\xd9\xd3\x01\x00\x00\x00\x01\x00\x00'
#            b'\x00\x03\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00'
#            b'\x00\x00\x00abc\x00\x00PK\x05\x06\x00\x00\x00\x00'
#            b'\x01\x00\x01\x003\x00\x00\x00%\x00\x00\x00\x00\x00'
#        )
#        with zipfile.ZipFile(io.BytesIO(zipdata), 'r') as zipf:
#            # testzip returns the name of the first corrupt file, or None
#            self.assertIsNone(zipf.testzip())
#
    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


#class AbstractBadCrcTests:
#    def test_testzip_with_bad_crc(self):
#        """Tests that files with bad CRCs return their name from testzip."""
#        zipdata = self.zip_with_bad_crc
#
#        with zipfile.ZipFile(io.BytesIO(zipdata), mode="r") as zipf:
#            # testzip returns the name of the first corrupt file, or None
#            self.assertEqual('afile', zipf.testzip())
#
#    def test_read_with_bad_crc(self):
#        """Tests that files with bad CRCs raise a BadZipFile exception when read."""
#        zipdata = self.zip_with_bad_crc
#
#        # Using ZipFile.read()
#        with zipfile.ZipFile(io.BytesIO(zipdata), mode="r") as zipf:
#            self.assertRaises(zipfile.BadZipFile, zipf.read, 'afile')
#
#        # Using ZipExtFile.read()
#        with zipfile.ZipFile(io.BytesIO(zipdata), mode="r") as zipf:
#            with zipf.open('afile', 'r') as corrupt_file:
#                self.assertRaises(zipfile.BadZipFile, corrupt_file.read)
#
#        # Same with small reads (in order to exercise the buffering logic)
#        with zipfile.ZipFile(io.BytesIO(zipdata), mode="r") as zipf:
#            with zipf.open('afile', 'r') as corrupt_file:
#                corrupt_file.MIN_READ_SIZE = 2
#                with self.assertRaises(zipfile.BadZipFile):
#                    while corrupt_file.read(2):
#                        pass
#
#
#class StoredBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
#    compression = zipfile.ZIP_STORED
#    zip_with_bad_crc = (
#        b'PK\003\004\024\0\0\0\0\0 \213\212;:r'
#        b'\253\377\f\0\0\0\f\0\0\0\005\0\0\000af'
#        b'ilehello,AworldP'
#        b'K\001\002\024\003\024\0\0\0\0\0 \213\212;:'
#        b'r\253\377\f\0\0\0\f\0\0\0\005\0\0\0\0'
#        b'\0\0\0\0\0\0\0\200\001\0\0\0\000afi'
#        b'lePK\005\006\0\0\0\0\001\0\001\0003\000'
#        b'\0\0/\0\0\0\0\0')
#
#@requires_zlib
#class DeflateBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
#    compression = zipfile.ZIP_DEFLATED
#    zip_with_bad_crc = (
#        b'PK\x03\x04\x14\x00\x00\x00\x08\x00n}\x0c=FA'
#        b'KE\x10\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
#        b'ile\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\xc9\xa0'
#        b'=\x13\x00PK\x01\x02\x14\x03\x14\x00\x00\x00\x08\x00n'
#        b'}\x0c=FAKE\x10\x00\x00\x00n\x00\x00\x00\x05'
#        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00'
#        b'\x00afilePK\x05\x06\x00\x00\x00\x00\x01\x00'
#        b'\x01\x003\x00\x00\x003\x00\x00\x00\x00\x00')
#
#@requires_bz2
#class Bzip2BadCrcTests(AbstractBadCrcTests, unittest.TestCase):
#    compression = zipfile.ZIP_BZIP2
#    zip_with_bad_crc = (
#        b'PK\x03\x04\x14\x03\x00\x00\x0c\x00nu\x0c=FA'
#        b'KE8\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
#        b'ileBZh91AY&SY\xd4\xa8\xca'
#        b'\x7f\x00\x00\x0f\x11\x80@\x00\x06D\x90\x80 \x00 \xa5'
#        b'P\xd9!\x03\x03\x13\x13\x13\x89\xa9\xa9\xc2u5:\x9f'
#        b'\x8b\xb9"\x9c(HjTe?\x80PK\x01\x02\x14'
#        b'\x03\x14\x03\x00\x00\x0c\x00nu\x0c=FAKE8'
#        b'\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00'
#        b'\x00 \x80\x80\x81\x00\x00\x00\x00afilePK'
#        b'\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00\x00[\x00'
#        b'\x00\x00\x00\x00')
#
#@requires_lzma
#class LzmaBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
#    compression = zipfile.ZIP_LZMA
#    zip_with_bad_crc = (
#        b'PK\x03\x04\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
#        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
#        b'ile\t\x04\x05\x00]\x00\x00\x00\x04\x004\x19I'
#        b'\xee\x8d\xe9\x17\x89:3`\tq!.8\x00PK'
#        b'\x01\x02\x14\x03\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
#        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00'
#        b'\x00\x00\x00\x00 \x80\x80\x81\x00\x00\x00\x00afil'
#        b'ePK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00'
#        b'\x00>\x00\x00\x00\x00\x00')
#
#
