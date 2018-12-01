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


################################################################################
#class LongnameTest:
#
#    def test_read_longname(self):
#        # Test reading of longname (bug #1471427).
#        longname = self.subdir + "/" + "123/" * 125 + "longname"
#        try:
#            tarinfo = self.tar.getmember(longname)
#        except KeyError:
#            self.fail("longname not found")
#        self.assertNotEqual(tarinfo.type, tarfile.DIRTYPE,
#                "read longname as dirtype")
#
#    def test_read_longlink(self):
#        longname = self.subdir + "/" + "123/" * 125 + "longname"
#        longlink = self.subdir + "/" + "123/" * 125 + "longlink"
#        try:
#            tarinfo = self.tar.getmember(longlink)
#        except KeyError:
#            self.fail("longlink not found")
#        self.assertEqual(tarinfo.linkname, longname, "linkname wrong")
#
#    def test_truncated_longname(self):
#        longname = self.subdir + "/" + "123/" * 125 + "longname"
#        tarinfo = self.tar.getmember(longname)
#        offset = tarinfo.offset
#        self.tar.fileobj.seek(offset)
#        fobj = io.BytesIO(self.tar.fileobj.read(3 * 512))
#        with self.assertRaises(tarfile.ReadError):
#            tarfile.open(name="foo.tar", fileobj=fobj)
#
#    def test_header_offset(self):
#        # Test if the start offset of the TarInfo object includes
#        # the preceding extended header.
#        longname = self.subdir + "/" + "123/" * 125 + "longname"
#        offset = self.tar.getmember(longname).offset
#        with open(tarname, "rb") as fobj:
#            fobj.seek(offset)
#            tarinfo = tarfile.TarInfo.frombuf(fobj.read(512),
#                                              "iso8859-1", "strict")
#            self.assertEqual(tarinfo.type, self.longnametype)
#
#
#class GNUReadTest(LongnameTest, ReadTest, unittest.TestCase):
#
#    subdir = "gnu"
#    longnametype = tarfile.GNUTYPE_LONGNAME
#
#    # Since 3.2 tarfile is supposed to accurately restore sparse members and
#    # produce files with holes. This is what we actually want to test here.
#    # Unfortunately, not all platforms/filesystems support sparse files, and
#    # even on platforms that do it is non-trivial to make reliable assertions
#    # about holes in files. Therefore, we first do one basic test which works
#    # an all platforms, and after that a test that will work only on
#    # platforms/filesystems that prove to support sparse files.
#    def _test_sparse_file(self, name):
#        self.tar.extract(name, TEMPDIR)
#        filename = os.path.join(TEMPDIR, name)
#        with open(filename, "rb") as fobj:
#            data = fobj.read()
#        self.assertEqual(md5sum(data), md5_sparse,
#                "wrong md5sum for %s" % name)
#
#        if self._fs_supports_holes():
#            s = os.stat(filename)
#            self.assertLess(s.st_blocks * 512, s.st_size)
#
#    def test_sparse_file_old(self):
#        self._test_sparse_file("gnu/sparse")
#
#    def test_sparse_file_00(self):
#        self._test_sparse_file("gnu/sparse-0.0")
#
#    def test_sparse_file_01(self):
#        self._test_sparse_file("gnu/sparse-0.1")
#
#    def test_sparse_file_10(self):
#        self._test_sparse_file("gnu/sparse-1.0")
#
#    @staticmethod
#    def _fs_supports_holes():
#        # Return True if the platform knows the st_blocks stat attribute and
#        # uses st_blocks units of 512 bytes, and if the filesystem is able to
#        # store holes in files.
#        if sys.platform.startswith("linux"):
#            # Linux evidentially has 512 byte st_blocks units.
#            name = os.path.join(TEMPDIR, "sparse-test")
#            with open(name, "wb") as fobj:
#                fobj.seek(4096)
#                fobj.truncate()
#            s = os.stat(name)
#            support.unlink(name)
#            return s.st_blocks == 0
#        else:
#            return False
#
#
#class PaxReadTest(LongnameTest, ReadTest, unittest.TestCase):
#
#    subdir = "pax"
#    longnametype = tarfile.XHDTYPE
#
#    def test_pax_global_headers(self):
#        tar = tarfile.open(tarname, encoding="iso8859-1")
#        try:
#            tarinfo = tar.getmember("pax/regtype1")
#            self.assertEqual(tarinfo.uname, "foo")
#            self.assertEqual(tarinfo.gname, "bar")
#            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
#                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
#
#            tarinfo = tar.getmember("pax/regtype2")
#            self.assertEqual(tarinfo.uname, "")
#            self.assertEqual(tarinfo.gname, "bar")
#            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
#                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
#
#            tarinfo = tar.getmember("pax/regtype3")
#            self.assertEqual(tarinfo.uname, "tarfile")
#            self.assertEqual(tarinfo.gname, "tarfile")
#            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
#                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
#        finally:
#            tar.close()
#
#    def test_pax_number_fields(self):
#        # All following number fields are read from the pax header.
#        tar = tarfile.open(tarname, encoding="iso8859-1")
#        try:
#            tarinfo = tar.getmember("pax/regtype4")
#            self.assertEqual(tarinfo.size, 7011)
#            self.assertEqual(tarinfo.uid, 123)
#            self.assertEqual(tarinfo.gid, 123)
#            self.assertEqual(tarinfo.mtime, 1041808783.0)
#            self.assertEqual(type(tarinfo.mtime), float)
#            self.assertEqual(float(tarinfo.pax_headers["atime"]), 1041808783.0)
#            self.assertEqual(float(tarinfo.pax_headers["ctime"]), 1041808783.0)
#        finally:
#            tar.close()
#
#
class WriteTestBase(TarTest):
    # Put all write tests in here that are supposed to be tested
    # in all possible mode combinations.

#    def test_fileobj_no_close(self):
#        fobj = io.BytesIO()
#        tar = tarfile.open(fileobj=fobj, mode=self.mode)
#        tar.addfile(tarfile.TarInfo("foo"))
#        tar.close()
#        self.assertFalse(fobj.closed, "external fileobjs must never closed")
#        # Issue #20238: Incomplete gzip output with mode="w:gz"
#        data = fobj.getvalue()
#        del tar
#        support.gc_collect()
#        self.assertFalse(fobj.closed)
#        self.assertEqual(data, fobj.getvalue())
    pass                                                                        ###


class WriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w:"

    def test_100_char_name(self):
        # The name field in a tar header stores strings of at most 100 chars.
        # If a string is shorter than 100 chars it has to be padded with '\0',
        # which implies that a string of exactly 100 chars is stored without
        # a trailing '\0'.
        name = "0123456789" * 10
        tar = tarfile.open(tmpname, self.mode)
        try:
            t = tarfile.TarInfo(name)
            tar.addfile(t)
        finally:
            tar.close()

        tar = tarfile.open(tmpname)
        try:
            self.assertEqual(tar.getnames()[0], name,
                    "failed to store 100 char filename")
        finally:
            tar.close()

    def test_tar_size(self):
        # Test for bug #1013882.
        tar = tarfile.open(tmpname, self.mode)
        try:
            path = os.path.join(TEMPDIR, "file")
            with open(path, "wb") as fobj:
                fobj.write(b"aaa")
            tar.add(path)
        finally:
            tar.close()
        self.assertGreater(os.path.getsize(tmpname), 0,
                "tarfile is empty")

    # The test_*_size tests test for bug #1167128.
    def test_file_size(self):
        tar = tarfile.open(tmpname, self.mode)
        try:
            path = os.path.join(TEMPDIR, "file")
            with open(path, "wb"):
                pass
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 0)

            with open(path, "wb") as fobj:
                fobj.write(b"aaa")
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 3)
        finally:
            tar.close()

    def test_directory_size(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        try:
            tar = tarfile.open(tmpname, self.mode)
            try:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            finally:
                tar.close()
        finally:
            support.rmdir(path)

#    @unittest.skipUnless(hasattr(os, "link"),
#                         "Missing hardlink implementation")
#    def test_link_size(self):
#        link = os.path.join(TEMPDIR, "link")
#        target = os.path.join(TEMPDIR, "link_target")
#        with open(target, "wb") as fobj:
#            fobj.write(b"aaa")
#        os.link(target, link)
#        try:
#            tar = tarfile.open(tmpname, self.mode)
#            try:
#                # Record the link target in the inodes list.
#                tar.gettarinfo(target)
#                tarinfo = tar.gettarinfo(link)
#                self.assertEqual(tarinfo.size, 0)
#            finally:
#                tar.close()
#        finally:
#            support.unlink(target)
#            support.unlink(link)
#
#    @support.skip_unless_symlink
#    def test_symlink_size(self):
#        path = os.path.join(TEMPDIR, "symlink")
#        os.symlink("link_target", path)
#        try:
#            tar = tarfile.open(tmpname, self.mode)
#            try:
#                tarinfo = tar.gettarinfo(path)
#                self.assertEqual(tarinfo.size, 0)
#            finally:
#                tar.close()
#        finally:
#            support.unlink(path)
#
    def test_add_self(self):
        # Test for #1257255.
        dstname = os.path.abspath(tmpname)
        tar = tarfile.open(tmpname, self.mode)
        try:
            self.assertEqual(tar.name, dstname,
                    "archive name must be absolute")
            tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")

            with support.change_cwd(TEMPDIR):
                tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")
        finally:
            tar.close()

    def test_exclude(self):
        tempdir = os.path.join(TEMPDIR, "exclude")
        os.mkdir(tempdir)
        try:
            for name in ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            exclude = os.path.isfile

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            try:
#                with support.check_warnings(("use the filter argument",
#                                             DeprecationWarning)):
                if True:                                                        ###
                    tar.add(tempdir, arcname="empty_dir", exclude=exclude)
            finally:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            try:
                self.assertEqual(len(tar.getmembers()), 1)
                self.assertEqual(tar.getnames()[0], "empty_dir")
            finally:
                tar.close()
        finally:
            support.rmtree(tempdir)

    def test_filter(self):
        tempdir = os.path.join(TEMPDIR, "filter")
        os.mkdir(tempdir)
        try:
            for name in ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            def filter(tarinfo):
                if os.path.basename(tarinfo.name) == "bar":
                    return
                tarinfo.uid = 123
                tarinfo.uname = "foo"
                return tarinfo

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            try:
                tar.add(tempdir, arcname="empty_dir", filter=filter)
            finally:
                tar.close()

            # Verify that filter is a keyword-only argument
            with self.assertRaises(TypeError):
                tar.add(tempdir, "empty_dir", True, None, filter)

            tar = tarfile.open(tmpname, "r")
            try:
                for tarinfo in tar:
                    self.assertEqual(tarinfo.uid, 123)
                    self.assertEqual(tarinfo.uname, "foo")
                self.assertEqual(len(tar.getmembers()), 3)
            finally:
                tar.close()
        finally:
            support.rmtree(tempdir)

    # Guarantee that stored pathnames are not modified. Don't
    # remove ./ or ../ or double slashes. Still make absolute
    # pathnames relative.
    # For details see bug #6054.
    def _test_pathname(self, path, cmp_path=None, dir=False):
        # Create a tarfile with an empty member named path
        # and compare the stored name with the original.
        foo = os.path.join(TEMPDIR, "foo")
        if not dir:
            support.create_empty_file(foo)
        else:
            os.mkdir(foo)

        tar = tarfile.open(tmpname, self.mode)
        try:
            tar.add(foo, arcname=path)
        finally:
            tar.close()

        tar = tarfile.open(tmpname, "r")
        try:
            t = tar.next()
        finally:
            tar.close()

        if not dir:
            support.unlink(foo)
        else:
            support.rmdir(foo)

        self.assertEqual(t.name, cmp_path or path.replace(os.sep, "/"))


#    @support.skip_unless_symlink
#    def test_extractall_symlinks(self):
#        # Test if extractall works properly when tarfile contains symlinks
#        tempdir = os.path.join(TEMPDIR, "testsymlinks")
#        temparchive = os.path.join(TEMPDIR, "testsymlinks.tar")
#        os.mkdir(tempdir)
#        try:
#            source_file = os.path.join(tempdir,'source')
#            target_file = os.path.join(tempdir,'symlink')
#            with open(source_file,'w') as f:
#                f.write('something\n')
#            os.symlink(source_file, target_file)
#            tar = tarfile.open(temparchive,'w')
#            tar.add(source_file)
#            tar.add(target_file)
#            tar.close()
#            # Let's extract it to the location which contains the symlink
#            tar = tarfile.open(temparchive,'r')
#            # this should not raise OSError: [Errno 17] File exists
#            try:
#                tar.extractall(path=tempdir)
#            except OSError:
#                self.fail("extractall failed with symlinked files")
#            finally:
#                tar.close()
#        finally:
#            support.unlink(temparchive)
#            support.rmtree(tempdir)
#
    def test_pathnames(self):
        self._test_pathname("foo")
        self._test_pathname(os.path.join("foo", ".", "bar"))
        self._test_pathname(os.path.join("foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo"))
        self._test_pathname(os.path.join(".", "foo", "."))
        self._test_pathname(os.path.join(".", "foo", ".", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join("..", "foo"))
        self._test_pathname(os.path.join("..", "foo", ".."))
        self._test_pathname(os.path.join("..", "foo", ".", "bar"))
        self._test_pathname(os.path.join("..", "foo", "..", "bar"))

        self._test_pathname("foo" + os.sep + os.sep + "bar")
        self._test_pathname("foo" + os.sep + os.sep, "foo", dir=True)

    def test_abs_pathnames(self):
#        if sys.platform == "win32":
#            self._test_pathname("C:\\foo", "foo")
#        else:
            self._test_pathname("/foo", "foo")
            self._test_pathname("///foo", "foo")

    def test_cwd(self):
        # Test adding the current working directory.
        with support.change_cwd(TEMPDIR):
            tar = tarfile.open(tmpname, self.mode)
            try:
                tar.add(".")
            finally:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            try:
                for t in tar:
                    if t.name != ".":
                        self.assertTrue(t.name.startswith("./"), t.name)
            finally:
                tar.close()

#    def test_open_nonwritable_fileobj(self):
#        for exctype in OSError, EOFError, RuntimeError:
#            class BadFile(io.BytesIO):
#                first = True
#                def write(self, data):
#                    if self.first:
#                        self.first = False
#                        raise exctype
#
#            f = BadFile()
#            with self.assertRaises(exctype):
#                tar = tarfile.open(tmpname, self.mode, fileobj=f,
#                                   format=tarfile.PAX_FORMAT,
#                                   pax_headers={'non': 'empty'})
#            self.assertFalse(f.closed)
#
#class GzipWriteTest(GzipTest, WriteTest):
#    pass
#
#class Bz2WriteTest(Bz2Test, WriteTest):
#    pass
#
#class LzmaWriteTest(LzmaTest, WriteTest):
#    pass
#
#
#class StreamWriteTest(WriteTestBase, unittest.TestCase):
#
#    prefix = "w|"
#    decompressor = None
#
#    def test_stream_padding(self):
#        # Test for bug #1543303.
#        tar = tarfile.open(tmpname, self.mode)
#        tar.close()
#        if self.decompressor:
#            dec = self.decompressor()
#            with open(tmpname, "rb") as fobj:
#                data = fobj.read()
#            data = dec.decompress(data)
#            self.assertFalse(dec.unused_data, "found trailing data")
#        else:
#            with self.open(tmpname) as fobj:
#                data = fobj.read()
#        self.assertEqual(data.count(b"\0"), tarfile.RECORDSIZE,
#                        "incorrect zero padding")
#
#    @unittest.skipUnless(sys.platform != "win32" and hasattr(os, "umask"),
#                         "Missing umask implementation")
#    def test_file_mode(self):
#        # Test for issue #8464: Create files with correct
#        # permissions.
#        if os.path.exists(tmpname):
#            support.unlink(tmpname)
#
#        original_umask = os.umask(0o022)
#        try:
#            tar = tarfile.open(tmpname, self.mode)
#            tar.close()
#            mode = os.stat(tmpname).st_mode & 0o777
#            self.assertEqual(mode, 0o644, "wrong file permissions")
#        finally:
#            os.umask(original_umask)
#
#class GzipStreamWriteTest(GzipTest, StreamWriteTest):
#    pass
#
#class Bz2StreamWriteTest(Bz2Test, StreamWriteTest):
#    decompressor = bz2.BZ2Decompressor if bz2 else None
#
#class LzmaStreamWriteTest(LzmaTest, StreamWriteTest):
#    decompressor = lzma.LZMADecompressor if lzma else None
#
#
################################################################################

def setUpModule():
    tearDownModule()
    os.makedirs(TEMPDIR)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)
