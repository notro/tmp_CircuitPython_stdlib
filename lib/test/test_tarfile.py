import sys
import os
import io
#from hashlib import md5

import unittest
import tarfile

#from test import support, script_helper
from test import support                                                        ###

## Check for our compression modules.
#try:
#    import gzip
#except ImportError:
#    gzip = None
#try:
#    import bz2
#except ImportError:
#    bz2 = None
#try:
#    import lzma
#except ImportError:
#    lzma = None
#
#def md5sum(data):
#    return md5(data).hexdigest()

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarextdir = TEMPDIR + '-extract-test'
tarname = support.findfile("testtar.tar")
#gzipname = os.path.join(TEMPDIR, "testtar.tar.gz")
#bz2name = os.path.join(TEMPDIR, "testtar.tar.bz2")
#xzname = os.path.join(TEMPDIR, "testtar.tar.xz")
tmpname = os.path.join(TEMPDIR, "tmp.tar")
dotlessname = os.path.join(TEMPDIR, "testtar")

md5_regtype = "65f477c818ad9e15f7feab0c6d37742f"
md5_sparse = "a54fbc4ca4f4399a90e1b27164012fc6"


class TarTest:
    tarname = tarname
    suffix = ''
    open = io.FileIO
    taropen = tarfile.TarFile.taropen

    @property
    def mode(self):
        return self.prefix + self.suffix

#@support.requires_gzip
#class GzipTest:
#    tarname = gzipname
#    suffix = 'gz'
#    open = gzip.GzipFile if gzip else None
#    taropen = tarfile.TarFile.gzopen
#
#@support.requires_bz2
#class Bz2Test:
#    tarname = bz2name
#    suffix = 'bz2'
#    open = bz2.BZ2File if bz2 else None
#    taropen = tarfile.TarFile.bz2open
#
#@support.requires_lzma
#class LzmaTest:
#    tarname = xzname
#    suffix = 'xz'
#    open = lzma.LZMAFile if lzma else None
#    taropen = tarfile.TarFile.xzopen
#

class ReadTest(TarTest):

    prefix = "r:"

    def setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")

    def tearDown(self):
        self.tar.close()


class UstarReadTest(ReadTest, unittest.TestCase):

    def test_fileobj_regular_file(self):
        tarinfo = self.tar.getmember("ustar/regtype")
        with self.tar.extractfile(tarinfo) as fobj:
            data = fobj.read()
            self.assertEqual(len(data), tarinfo.size,
                    "regular file extraction failed")
#            self.assertEqual(md5sum(data), md5_regtype,
#                    "regular file extraction failed")

    def test_fileobj_readlines(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "r") as fobj1:
            lines1 = fobj1.readlines()

        with self.tar.extractfile(tarinfo) as fobj:
#            fobj2 = io.TextIOWrapper(fobj)
            fobj2 = fobj                                                        ### uio.TextIOWrapper() is a wrapper for open()
            lines2 = fobj2.readlines()
            lines2 = [line.decode() for line in lines2]                         ### Turn into Text
            self.assertEqual(lines1, lines2,
                    "fileobj.readlines() failed")
#            self.assertEqual(len(lines2), 114,
#                    "fileobj.readlines() failed")
#            self.assertEqual(lines2[83],
#                    "I will gladly admit that Python is not the fastest "
#                    "running scripting language.\n",
#                    "fileobj.readlines() failed")
            self.assertEqual(lines2[2],                                         ### File is trimmed to reduce size
                    "As Python's creator, I'd like to say a few words about its origins, adding a\n",  ###
                    "fileobj.readlines() failed")                               ###

    def test_fileobj_iter(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "r") as fobj1:
            lines1 = fobj1.readlines()
        with self.tar.extractfile(tarinfo) as fobj2:
#            lines2 = list(io.TextIOWrapper(fobj2))
            lines2 = [line.decode() for line in fobj2]                          ###
            self.assertEqual(lines1, lines2,
                    "fileobj.__iter__() failed")

    def test_fileobj_seek(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "rb") as fobj:
            data = fobj.read()

        tarinfo = self.tar.getmember("ustar/regtype")
        fobj = self.tar.extractfile(tarinfo)

        text = fobj.read()
        fobj.seek(0)
        self.assertEqual(0, fobj.tell(),
                     "seek() to file's start failed")
#        fobj.seek(2048, 0)
#        self.assertEqual(2048, fobj.tell(),
        fobj.seek(64, 0)                                                        ###
        self.assertEqual(64, fobj.tell(),                                       ###
                     "seek() to absolute position failed")
#        fobj.seek(-1024, 1)
#        self.assertEqual(1024, fobj.tell(),
        fobj.seek(-32, 1)                                                       ###
        self.assertEqual(32, fobj.tell(),                                       ###
                     "seek() to negative relative position failed")
#        fobj.seek(1024, 1)
#        self.assertEqual(2048, fobj.tell(),
        fobj.seek(32, 1)                                                        ###
        self.assertEqual(64, fobj.tell(),                                       ###
                     "seek() to positive relative position failed")
        s = fobj.read(10)
#        self.assertEqual(s, data[2048:2058],
        self.assertEqual(s, data[64:74],                                        ###
                     "read() after seek failed")
        fobj.seek(0, 2)
        self.assertEqual(tarinfo.size, fobj.tell(),
                     "seek() to file's end failed")
        self.assertEqual(fobj.read(), b"",
                     "read() at file's end did not return empty string")
        fobj.seek(-tarinfo.size, 2)
        self.assertEqual(0, fobj.tell(),
                     "relative seek() to file's end failed")
#        fobj.seek(512)
        fobj.seek(32)                                                           ###
        s1 = fobj.readlines()
#        fobj.seek(512)
        fobj.seek(32)                                                           ###
        s2 = fobj.readlines()
        self.assertEqual(s1, s2,
                     "readlines() after seek failed")
        fobj.seek(0)
        self.assertEqual(len(fobj.readline()), fobj.tell(),
                     "tell() after readline() failed")
#        fobj.seek(512)
        fobj.seek(32)                                                           ###
#        self.assertEqual(len(fobj.readline()) + 512, fobj.tell(),
        self.assertEqual(len(fobj.readline()) + 32, fobj.tell(),                ###
                     "tell() after seek() and readline() failed")
        fobj.seek(0)
        line = fobj.readline()
        self.assertEqual(fobj.read(), data[len(line):],
                     "read() after readline() failed")
        fobj.close()

#    def test_fileobj_text(self):
#        with self.tar.extractfile("ustar/regtype") as fobj:
#            fobj = io.TextIOWrapper(fobj)
#            data = fobj.read().encode("iso8859-1")
#            self.assertEqual(md5sum(data), md5_regtype)
#            try:
#                fobj.seek(100)
#            except AttributeError:
#                # Issue #13815: seek() complained about a missing
#                # flush() method.
#                self.fail("seeking failed in text mode")
#
    # Test if symbolic and hard links are resolved by extractfile().  The
    # test link members each point to a regular member whose data is
    # supposed to be exported.
    def _test_fileobj_link(self, lnktype, regtype):
        with self.tar.extractfile(lnktype) as a, \
             self.tar.extractfile(regtype) as b:
            self.assertEqual(a.name, b.name)

    def test_fileobj_link1(self):
        self._test_fileobj_link("ustar/lnktype", "ustar/regtype")

#    def test_fileobj_link2(self):
#        self._test_fileobj_link("./ustar/linktest2/lnktype",
#                                "ustar/linktest1/regtype")
#
    def test_fileobj_symlink1(self):
        self._test_fileobj_link("ustar/symtype", "ustar/regtype")

#    def test_fileobj_symlink2(self):
#        self._test_fileobj_link("./ustar/linktest2/symtype",
#                                "ustar/linktest1/regtype")
#
#    def test_issue14160(self):
#        self._test_fileobj_link("symtype2", "ustar/regtype")
#
#class GzipUstarReadTest(GzipTest, UstarReadTest):
#    pass
#
#class Bz2UstarReadTest(Bz2Test, UstarReadTest):
#    pass
#
#class LzmaUstarReadTest(LzmaTest, UstarReadTest):
#    pass
#
#
#class ListTest(ReadTest, unittest.TestCase):
#
#    # Override setUp to use default encoding (UTF-8)
#    def setUp(self):
#        self.tar = tarfile.open(self.tarname, mode=self.mode)
#
#    def test_list(self):
#        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
#        with support.swap_attr(sys, 'stdout', tio):
#            self.tar.list(verbose=False)
#        out = tio.detach().getvalue()
#        self.assertIn(b'ustar/conttype', out)
#        self.assertIn(b'ustar/regtype', out)
#        self.assertIn(b'ustar/lnktype', out)
#        self.assertIn(b'ustar' + (b'/12345' * 40) + b'67/longname', out)
#        self.assertIn(b'./ustar/linktest2/symtype', out)
#        self.assertIn(b'./ustar/linktest2/lnktype', out)
#        # Make sure it puts trailing slash for directory
#        self.assertIn(b'ustar/dirtype/', out)
#        self.assertIn(b'ustar/dirtype-with-size/', out)
#        # Make sure it is able to print unencodable characters
#        def conv(b):
#            s = b.decode(self.tar.encoding, 'surrogateescape')
#            return s.encode('ascii', 'backslashreplace')
#        self.assertIn(conv(b'ustar/umlauts-\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
#        self.assertIn(conv(b'misc/regtype-hpux-signed-chksum-'
#                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
#        self.assertIn(conv(b'misc/regtype-old-v7-signed-chksum-'
#                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
#        self.assertIn(conv(b'pax/bad-pax-\xe4\xf6\xfc'), out)
#        self.assertIn(conv(b'pax/hdrcharset-\xe4\xf6\xfc'), out)
#        # Make sure it prints files separated by one newline without any
#        # 'ls -l'-like accessories if verbose flag is not being used
#        # ...
#        # ustar/conttype
#        # ustar/regtype
#        # ...
#        self.assertRegex(out, br'ustar/conttype ?\r?\n'
#                              br'ustar/regtype ?\r?\n')
#        # Make sure it does not print the source of link without verbose flag
#        self.assertNotIn(b'link to', out)
#        self.assertNotIn(b'->', out)
#
#    def test_list_verbose(self):
#        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
#        with support.swap_attr(sys, 'stdout', tio):
#            self.tar.list(verbose=True)
#        out = tio.detach().getvalue()
#        # Make sure it prints files separated by one newline with 'ls -l'-like
#        # accessories if verbose flag is being used
#        # ...
#        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/conttype
#        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/regtype
#        # ...
#        self.assertRegex(out, (br'\?rw-r--r-- tarfile/tarfile\s+7011 '
#                               br'\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d '
#                               br'ustar/\w+type ?\r?\n') * 2)
#        # Make sure it prints the source of link with verbose flag
#        self.assertIn(b'ustar/symtype -> regtype', out)
#        self.assertIn(b'./ustar/linktest2/symtype -> ../linktest1/regtype', out)
#        self.assertIn(b'./ustar/linktest2/lnktype link to '
#                      b'./ustar/linktest1/regtype', out)
#        self.assertIn(b'gnu' + (b'/123' * 125) + b'/longlink link to gnu' +
#                      (b'/123' * 125) + b'/longname', out)
#        self.assertIn(b'pax' + (b'/123' * 125) + b'/longlink link to pax' +
#                      (b'/123' * 125) + b'/longname', out)
#
#
#class GzipListTest(GzipTest, ListTest):
#    pass
#
#
#class Bz2ListTest(Bz2Test, ListTest):
#    pass
#
#
#class LzmaListTest(LzmaTest, ListTest):
#    pass
#
#
######################################################################################

def setUpModule():
    tearDownModule()                                                            ### Might run out of memory and this wasn't called
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)
