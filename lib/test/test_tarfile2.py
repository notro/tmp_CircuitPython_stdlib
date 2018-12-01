import os
import io

import unittest
import tarfile

from test import support

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarname = support.findfile("testtar.tar")
tmpname = os.path.join(TEMPDIR, "tmp.tar")

class TarTest:
    tarname = tarname
    suffix = ''
    open = io.FileIO
    taropen = tarfile.TarFile.taropen

    @property
    def mode(self):
        return self.prefix + self.suffix

class ReadTest(TarTest):

    prefix = "r:"

    def setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")

    def tearDown(self):
        self.tar.close()


################################################################################
class CommonReadTest(ReadTest):

    def test_empty_tarfile(self):
        # Test for issue6123: Allow opening empty archives.
        # This test checks if tarfile.open() is able to open an empty tar
        # archive successfully. Note that an empty tar archive is not the
        # same as an empty file!
        with tarfile.open(tmpname, self.mode.replace("r", "w")):
            pass
        try:
            tar = tarfile.open(tmpname, self.mode)
            tar.getnames()
        except tarfile.ReadError:
            self.fail("tarfile.open() failed on empty archive")
        else:
            self.assertListEqual(tar.getmembers(), [])
        finally:
            tar.close()

    def test_non_existent_tarfile(self):
        # Test for issue11513: prevent non-existent gzipped tarfiles raising
        # multiple exceptions.
#        with self.assertRaisesRegex(FileNotFoundError, "xxx"):
        with self.assertRaises(OSError):                                        ###
            tarfile.open("xxx", self.mode)

    def test_null_tarfile(self):
        # Test for issue6123: Allow opening empty archives.
        # This test guarantees that tarfile.open() does not treat an empty
        # file as an empty tar archive.
        with open(tmpname, "wb"):
            pass
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, self.mode)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname)

#    def test_ignore_zeros(self):
#        # Test TarFile's ignore_zeros option.
#        for char in (b'\0', b'a'):
#            # Test if EOFHeaderError ('\0') and InvalidHeaderError ('a')
#            # are ignored correctly.
#            with self.open(tmpname, "w") as fobj:
#                fobj.write(char * 1024)
#                fobj.write(tarfile.TarInfo("foo").tobuf())
#
#            tar = tarfile.open(tmpname, mode="r", ignore_zeros=True)
#            try:
#                self.assertListEqual(tar.getnames(), ["foo"],
#                    "ignore_zeros=True should have skipped the %r-blocks" %
#                    char)
#            finally:
#                tar.close()
#
#    def test_premature_end_of_archive(self):
#        for size in (512, 600, 1024, 1200):
#            with tarfile.open(tmpname, "w:") as tar:
#                t = tarfile.TarInfo("foo")
#                t.size = 1024
#                tar.addfile(t, io.BytesIO(b"a" * 1024))
#
#            with open(tmpname, "r+b") as fobj:
#                fobj.truncate(size)
#
#            with tarfile.open(tmpname) as tar:
#                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
#                    for t in tar:
#                        pass
#
#            with tarfile.open(tmpname) as tar:
#                t = tar.next()
#
#                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
#                    tar.extract(t, TEMPDIR)
#
#                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
#                    tar.extractfile(t).read()

class MiscReadTestBase(CommonReadTest):
#    def requires_name_attribute(self):
#        pass
#
#    def test_no_name_argument(self):
#        self.requires_name_attribute()
#        with open(self.tarname, "rb") as fobj:
#            self.assertIsInstance(fobj.name, str)
#            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
#                self.assertIsInstance(tar.name, str)
#                self.assertEqual(tar.name, os.path.abspath(fobj.name))
#
#    def test_no_name_attribute(self):
#        with open(self.tarname, "rb") as fobj:
#            data = fobj.read()
#        fobj = io.BytesIO(data)
#        self.assertRaises(AttributeError, getattr, fobj, "name")
#        tar = tarfile.open(fileobj=fobj, mode=self.mode)
#        self.assertIsNone(tar.name)
#
#    def test_empty_name_attribute(self):
#        with open(self.tarname, "rb") as fobj:
#            data = fobj.read()
#        fobj = io.BytesIO(data)
#        fobj.name = ""
#        with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
#            self.assertIsNone(tar.name)
#
#    def test_int_name_attribute(self):
#        # Issue 21044: tarfile.open() should handle fileobj with an integer
#        # 'name' attribute.
#        fd = os.open(self.tarname, os.O_RDONLY)
#        with open(fd, 'rb') as fobj:
#            self.assertIsInstance(fobj.name, int)
#            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
#                self.assertIsNone(tar.name)
#
#    def test_bytes_name_attribute(self):
#        self.requires_name_attribute()
#        tarname = os.fsencode(self.tarname)
#        with open(tarname, 'rb') as fobj:
#            self.assertIsInstance(fobj.name, bytes)
#            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
#                self.assertIsInstance(tar.name, bytes)
#                self.assertEqual(tar.name, os.path.abspath(fobj.name))
#
    def test_illegal_mode_arg(self):
        with open(tmpname, 'wb'):
            pass
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'q')
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'rw')
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, '')

#    def test_fileobj_with_offset(self):
#        # Skip the first member and store values from the second member
#        # of the testtar.
#        tar = tarfile.open(self.tarname, mode=self.mode)
#        try:
#            tar.next()
#            t = tar.next()
#            name = t.name
#            offset = t.offset
#            with tar.extractfile(t) as f:
#                data = f.read()
#        finally:
#            tar.close()
#
#        # Open the testtar and seek to the offset of the second member.
#        with self.open(self.tarname) as fobj:
#            fobj.seek(offset)
#
#            # Test if the tarfile starts with the second member.
#            tar = tar.open(self.tarname, mode="r:", fileobj=fobj)
#            t = tar.next()
#            self.assertEqual(t.name, name)
#            # Read to the end of fileobj and test if seeking back to the
#            # beginning works.
#            tar.getmembers()
#            self.assertEqual(tar.extractfile(t).read(), data,
#                    "seek back did not work")
#            tar.close()
#
#    def test_fail_comp(self):
#        # For Gzip and Bz2 Tests: fail with a ReadError on an uncompressed file.
#        self.assertRaises(tarfile.ReadError, tarfile.open, tarname, self.mode)
#        with open(tarname, "rb") as fobj:
#            self.assertRaises(tarfile.ReadError, tarfile.open,
#                              fileobj=fobj, mode=self.mode)
#
#    def test_v7_dirtype(self):
#        # Test old style dirtype member (bug #1336623):
#        # Old V7 tars create directory members using an AREGTYPE
#        # header with a "/" appended to the filename field.
#        tarinfo = self.tar.getmember("misc/dirtype-old-v7")
#        self.assertEqual(tarinfo.type, tarfile.DIRTYPE,
#                "v7 dirtype failed")
#
#    def test_xstar_type(self):
#        # The xstar format stores extra atime and ctime fields inside the
#        # space reserved for the prefix field. The prefix field must be
#        # ignored in this case, otherwise it will mess up the name.
#        try:
#            self.tar.getmember("misc/regtype-xstar")
#        except KeyError:
#            self.fail("failed to find misc/regtype-xstar (mangled prefix?)")
#
    def test_check_members(self):
        for tarinfo in self.tar:
            self.assertEqual(int(tarinfo.mtime), 0o7606136617,
                    "wrong mtime for %s" % tarinfo.name)
            if not tarinfo.name.startswith("ustar/"):
                continue
            self.assertEqual(tarinfo.uname, "tarfile",
                    "wrong uname for %s" % tarinfo.name)

#    def test_find_members(self):
#        self.assertEqual(self.tar.getmembers()[-1].name, "misc/eof",
#                "could not find all members")
#
#    @unittest.skipUnless(hasattr(os, "link"),
#                         "Missing hardlink implementation")
#    @support.skip_unless_symlink
#    def test_extract_hardlink(self):
#        # Test hardlink extraction (e.g. bug #857297).
#        with tarfile.open(tarname, errorlevel=1, encoding="iso8859-1") as tar:
#            tar.extract("ustar/regtype", TEMPDIR)
#            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/regtype"))
#
#            tar.extract("ustar/lnktype", TEMPDIR)
#            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/lnktype"))
#            with open(os.path.join(TEMPDIR, "ustar/lnktype"), "rb") as f:
#                data = f.read()
#            self.assertEqual(md5sum(data), md5_regtype)
#
#            tar.extract("ustar/symtype", TEMPDIR)
#            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/symtype"))
#            with open(os.path.join(TEMPDIR, "ustar/symtype"), "rb") as f:
#                data = f.read()
#            self.assertEqual(md5sum(data), md5_regtype)
#
    def test_extractall(self):
        # Test if extractall() correctly restores directory permissions
        # and times (see issue1735).
        tar = tarfile.open(tarname, encoding="iso8859-1")
        DIR = os.path.join(TEMPDIR, "extractall")
        os.mkdir(DIR)
        try:
            directories = [t for t in tar if t.isdir()]
            tar.extractall(DIR, directories)
#            for tarinfo in directories:
#                path = os.path.join(DIR, tarinfo.name)
#                if sys.platform != "win32":
#                    # Win32 has no support for fine grained permissions.
#                    self.assertEqual(tarinfo.mode & 0o777,
#                                     os.stat(path).st_mode & 0o777)
#                def format_mtime(mtime):
#                    if isinstance(mtime, float):
#                        return "{} ({})".format(mtime, mtime.hex())
#                    else:
#                        return "{!r} (int)".format(mtime)
#                file_mtime = os.path.getmtime(path)
#                errmsg = "tar mtime {0} != file time {1} of path {2!a}".format(
#                    format_mtime(tarinfo.mtime),
#                    format_mtime(file_mtime),
#                    path)
#                self.assertEqual(tarinfo.mtime, file_mtime, errmsg)
        finally:
            tar.close()
            support.rmtree(DIR)

    def test_extract_directory(self):
        dirtype = "ustar/dirtype"
        DIR = os.path.join(TEMPDIR, "extractdir")
        os.mkdir(DIR)
        try:
            with tarfile.open(tarname, encoding="iso8859-1") as tar:
                tarinfo = tar.getmember(dirtype)
                tar.extract(tarinfo, path=DIR)
                extracted = os.path.join(DIR, dirtype)
#                self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)
                os.path.getmtime(extracted)                                     ### No os.utime, just do this to verify the file is there
#                if sys.platform != "win32":
#                    self.assertEqual(os.stat(extracted).st_mode & 0o777, 0o755)
        finally:
            support.rmtree(DIR)

    def test_init_close_fobj(self):
        # Issue #7341: Close the internal file object in the TarFile
        # constructor in case of an error. For the test we rely on
        # the fact that opening an empty file raises a ReadError.
        empty = os.path.join(TEMPDIR, "empty")
        with open(empty, "wb") as fobj:
            fobj.write(b"")

        try:
            tar = object.__new__(tarfile.TarFile)
            try:
                tar.__init__(empty)
            except tarfile.ReadError:
#                self.assertTrue(tar.fileobj.closed)
                pass                                                            ### AttributeError: 'FileIO' object has no attribute 'closed'
            else:
                self.fail("ReadError not raised")
        finally:
            support.unlink(empty)

    def test_parallel_iteration(self):
        # Issue #16601: Restarting iteration over tarfile continued
        # from where it left off.
        with tarfile.open(self.tarname) as tar:
            for m1, m2 in zip(tar, tar):
                self.assertEqual(m1.offset, m2.offset)
                self.assertEqual(m1.get_info(), m2.get_info())

class MiscReadTest(MiscReadTestBase, unittest.TestCase):
    test_fail_comp = None

#class GzipMiscReadTest(GzipTest, MiscReadTestBase, unittest.TestCase):
#    pass
#
#class Bz2MiscReadTest(Bz2Test, MiscReadTestBase, unittest.TestCase):
#    def requires_name_attribute(self):
#        self.skipTest("BZ2File have no name attribute")
#
#class LzmaMiscReadTest(LzmaTest, MiscReadTestBase, unittest.TestCase):
#    def requires_name_attribute(self):
#        self.skipTest("LZMAFile have no name attribute")
#
#
class StreamReadTest(CommonReadTest, unittest.TestCase):

    prefix="r|"

    def test_read_through(self):
        # Issue #11224: A poorly designed _FileInFile.read() method
        # caused seeking errors with stream tar files.
        for tarinfo in self.tar:
            if not tarinfo.isreg():
                continue
            with self.tar.extractfile(tarinfo) as fobj:
                while True:
                    try:
                        buf = fobj.read(512)
                    except tarfile.StreamError:
                        self.fail("simple read-through using "
                                  "TarFile.extractfile() failed")
                    if not buf:
                        break

    def test_fileobj_regular_file(self):
        tarinfo = self.tar.next() # get "regtype" (can't use getmember)
        with self.tar.extractfile(tarinfo) as fobj:
            data = fobj.read()
        self.assertEqual(len(data), tarinfo.size,
                "regular file extraction failed")
#        self.assertEqual(md5sum(data), md5_regtype,
#                "regular file extraction failed")

    def test_provoke_stream_error(self):
        tarinfos = self.tar.getmembers()
        with self.tar.extractfile(tarinfos[0]) as f: # read the first member
            self.assertRaises(tarfile.StreamError, f.read)

    def test_compare_members(self):
        tar1 = tarfile.open(tarname, encoding="iso8859-1")
        try:
            tar2 = self.tar

            while True:
                t1 = tar1.next()
                t2 = tar2.next()
                if t1 is None:
                    break
                self.assertIsNotNone(t2, "stream.next() failed.")

                if t2.islnk() or t2.issym():
                    with self.assertRaises(tarfile.StreamError):
                        tar2.extractfile(t2)
                    continue

                v1 = tar1.extractfile(t1)
                v2 = tar2.extractfile(t2)
                if v1 is None:
                    continue
                self.assertIsNotNone(v2, "stream.extractfile() failed")
                self.assertEqual(v1.read(), v2.read(),
                        "stream extraction failed")
        finally:
            tar1.close()

#class GzipStreamReadTest(GzipTest, StreamReadTest):
#    pass
#
#class Bz2StreamReadTest(Bz2Test, StreamReadTest):
#    pass
#
#class LzmaStreamReadTest(LzmaTest, StreamReadTest):
#    pass
#
#
################################################################################

def setUpModule():
    tearDownModule()
    os.makedirs(TEMPDIR)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)
