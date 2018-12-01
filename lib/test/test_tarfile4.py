import io
from hashlib import md5

import unittest
import tarfile

from test import support

def md5sum(data):
    return md5(data).hexdigest()

tarname = support.findfile("testtar.tar")

#md5_regtype = "65f477c818ad9e15f7feab0c6d37742f"
md5_regtype = "1aea8fceaf9fd632ffdee130fe68d5e7"                                ### 128 byte version

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
class MemberReadTest(ReadTest, unittest.TestCase):

    def _test_member(self, tarinfo, chksum=None, **kwargs):
        if chksum is not None:
            with self.tar.extractfile(tarinfo) as f:
                self.assertEqual(md5sum(f.read()), chksum,
                        "wrong md5sum for %s" % tarinfo.name)

        kwargs["mtime"] = 0o7606136617
        kwargs["uid"] = 1000
        kwargs["gid"] = 100
        if "old-v7" not in tarinfo.name:
            # V7 tar can't handle alphabetic owners.
            kwargs["uname"] = "tarfile"
            kwargs["gname"] = "tarfile"
        for k, v in kwargs.items():
            self.assertEqual(getattr(tarinfo, k), v,
                    "wrong value in %s field of %s" % (k, tarinfo.name))

    def test_find_regtype(self):
        tarinfo = self.tar.getmember("ustar/regtype")
#        self._test_member(tarinfo, size=7011, chksum=md5_regtype)
        self._test_member(tarinfo, size=128, chksum=md5_regtype)                ###

    def test_find_conttype(self):
        tarinfo = self.tar.getmember("ustar/conttype")
#        self._test_member(tarinfo, size=7011, chksum=md5_regtype)
        self._test_member(tarinfo, size=128, chksum=md5_regtype)                ###

    def test_find_dirtype(self):
        tarinfo = self.tar.getmember("ustar/dirtype")
        self._test_member(tarinfo, size=0)

    def test_find_dirtype_with_size(self):
        tarinfo = self.tar.getmember("ustar/dirtype-with-size")
        self._test_member(tarinfo, size=255)

    def test_find_lnktype(self):
        tarinfo = self.tar.getmember("ustar/lnktype")
        self._test_member(tarinfo, size=0, linkname="ustar/regtype")

    def test_find_symtype(self):
        tarinfo = self.tar.getmember("ustar/symtype")
        self._test_member(tarinfo, size=0, linkname="regtype")

    def test_find_blktype(self):
        tarinfo = self.tar.getmember("ustar/blktype")
        self._test_member(tarinfo, size=0, devmajor=3, devminor=0)

    def test_find_chrtype(self):
        tarinfo = self.tar.getmember("ustar/chrtype")
        self._test_member(tarinfo, size=0, devmajor=1, devminor=3)

    def test_find_fifotype(self):
        tarinfo = self.tar.getmember("ustar/fifotype")
        self._test_member(tarinfo, size=0)

#    def test_find_sparse(self):
#        tarinfo = self.tar.getmember("ustar/sparse")
#        self._test_member(tarinfo, size=86016, chksum=md5_sparse)
#
#    def test_find_gnusparse(self):
#        tarinfo = self.tar.getmember("gnu/sparse")
#        self._test_member(tarinfo, size=86016, chksum=md5_sparse)
#
#    def test_find_gnusparse_00(self):
#        tarinfo = self.tar.getmember("gnu/sparse-0.0")
#        self._test_member(tarinfo, size=86016, chksum=md5_sparse)
#
#    def test_find_gnusparse_01(self):
#        tarinfo = self.tar.getmember("gnu/sparse-0.1")
#        self._test_member(tarinfo, size=86016, chksum=md5_sparse)
#
#    def test_find_gnusparse_10(self):
#        tarinfo = self.tar.getmember("gnu/sparse-1.0")
#        self._test_member(tarinfo, size=86016, chksum=md5_sparse)
#
#    def test_find_umlauts(self):
#        tarinfo = self.tar.getmember("ustar/umlauts-"
#                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
#        self._test_member(tarinfo, size=7011, chksum=md5_regtype)
#
    def test_find_ustar_longname(self):
        name = "ustar/" + "12345/" * 39 + "1234567/longname"
        self.assertIn(name, self.tar.getnames())

#    def test_find_regtype_oldv7(self):
#        tarinfo = self.tar.getmember("misc/regtype-old-v7")
#        self._test_member(tarinfo, size=7011, chksum=md5_regtype)
#
#    def test_find_pax_umlauts(self):
#        self.tar.close()
#        self.tar = tarfile.open(self.tarname, mode=self.mode,
#                                encoding="iso8859-1")
#        tarinfo = self.tar.getmember("pax/umlauts-"
#                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
#        self._test_member(tarinfo, size=7011, chksum=md5_regtype)
#
#
################################################################################
