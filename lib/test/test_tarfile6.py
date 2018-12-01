import os

import unittest
import tarfile

TEMPDIR = os.path.abspath("$test-tardir")
tmpname = os.path.join(TEMPDIR, "tmp.tar")

################################################################################
class GNUWriteTest(unittest.TestCase):
    # This testcase checks for correct creation of GNU Longname
    # and Longlink extended headers (cp. bug #812325).

    def _length(self, s):
        blocks = len(s) // 512 + 1
        return blocks * 512

    def _calc_size(self, name, link=None):
        # Initial tar header
        count = 512

        if len(name) > tarfile.LENGTH_NAME:
            # GNU longname extended header + longname
            count += 512
            count += self._length(name)
        if link is not None and len(link) > tarfile.LENGTH_LINK:
            # GNU longlink extended header + longlink
            count += 512
            count += self._length(link)
        return count

    def _test(self, name, link=None):
        tarinfo = tarfile.TarInfo(name)
        if link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w")
        try:
            tar.format = tarfile.GNU_FORMAT
#            tar.addfile(tarinfo)
            try:                                                                ###
                tar.addfile(tarinfo)                                            ###
            except MemoryError:                                                 ###
                self.skipTest('Not enough memory')                              ###

            v1 = self._calc_size(name, link)
            v2 = tar.offset
            self.assertEqual(v1, v2, "GNU longname/longlink creation failed")
        finally:
            tar.close()

        tar = tarfile.open(tmpname)
        try:
            member = tar.next()
            self.assertIsNotNone(member,
                    "unable to read longname member")
            self.assertEqual(tarinfo.name, member.name,
                    "unable to read longname member")
            self.assertEqual(tarinfo.linkname, member.linkname,
                    "unable to read longname member")
        finally:
            tar.close()

    def test_longname_1023(self):
        self._test(("longnam/" * 127) + "longnam")

    def test_longname_1024(self):
        self._test(("longnam/" * 127) + "longname")

    def test_longname_1025(self):
        self._test(("longnam/" * 127) + "longname_")

    def test_longlink_1023(self):
        self._test("name", ("longlnk/" * 127) + "longlnk")

    def test_longlink_1024(self):
        self._test("name", ("longlnk/" * 127) + "longlink")

    def test_longlink_1025(self):
        self._test("name", ("longlnk/" * 127) + "longlink_")

    def test_longnamelink_1023(self):
        self._test(("longnam/" * 127) + "longnam",
                   ("longlnk/" * 127) + "longlnk")

    def test_longnamelink_1024(self):
        self._test(("longnam/" * 127) + "longname",
                   ("longlnk/" * 127) + "longlink")

    def test_longnamelink_1025(self):
        self._test(("longnam/" * 127) + "longname_",
                   ("longlnk/" * 127) + "longlink_")


#@unittest.skipUnless(hasattr(os, "link"), "Missing hardlink implementation")
#class HardlinkTest(unittest.TestCase):
#    # Test the creation of LNKTYPE (hardlink) members in an archive.
#
#    def setUp(self):
#        self.foo = os.path.join(TEMPDIR, "foo")
#        self.bar = os.path.join(TEMPDIR, "bar")
#
#        with open(self.foo, "wb") as fobj:
#            fobj.write(b"foo")
#
#        os.link(self.foo, self.bar)
#
#        self.tar = tarfile.open(tmpname, "w")
#        self.tar.add(self.foo)
#
#    def tearDown(self):
#        self.tar.close()
#        support.unlink(self.foo)
#        support.unlink(self.bar)
#
#    def test_add_twice(self):
#        # The same name will be added as a REGTYPE every
#        # time regardless of st_nlink.
#        tarinfo = self.tar.gettarinfo(self.foo)
#        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
#                "add file as regular failed")
#
#    def test_add_hardlink(self):
#        tarinfo = self.tar.gettarinfo(self.bar)
#        self.assertEqual(tarinfo.type, tarfile.LNKTYPE,
#                "add file as hardlink failed")
#
#    def test_dereference_hardlink(self):
#        self.tar.dereference = True
#        tarinfo = self.tar.gettarinfo(self.bar)
#        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
#                "dereferencing hardlink failed")
#
#
#class PaxWriteTest(GNUWriteTest):
#
#    def _test(self, name, link=None):
#        # See GNUWriteTest.
#        tarinfo = tarfile.TarInfo(name)
#        if link:
#            tarinfo.linkname = link
#            tarinfo.type = tarfile.LNKTYPE
#
#        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT)
#        try:
#            tar.addfile(tarinfo)
#        finally:
#            tar.close()
#
#        tar = tarfile.open(tmpname)
#        try:
#            if link:
#                l = tar.getmembers()[0].linkname
#                self.assertEqual(link, l, "PAX longlink creation failed")
#            else:
#                n = tar.getmembers()[0].name
#                self.assertEqual(name, n, "PAX longname creation failed")
#        finally:
#            tar.close()
#
#    def test_pax_global_header(self):
#        pax_headers = {
#                "foo": "bar",
#                "uid": "0",
#                "mtime": "1.23",
#                "test": "\xe4\xf6\xfc",
#                "\xe4\xf6\xfc": "test"}
#
#        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
#                pax_headers=pax_headers)
#        try:
#            tar.addfile(tarfile.TarInfo("test"))
#        finally:
#            tar.close()
#
#        # Test if the global header was written correctly.
#        tar = tarfile.open(tmpname, encoding="iso8859-1")
#        try:
#            self.assertEqual(tar.pax_headers, pax_headers)
#            self.assertEqual(tar.getmembers()[0].pax_headers, pax_headers)
#            # Test if all the fields are strings.
#            for key, val in tar.pax_headers.items():
#                self.assertIsNot(type(key), bytes)
#                self.assertIsNot(type(val), bytes)
#                if key in tarfile.PAX_NUMBER_FIELDS:
#                    try:
#                        tarfile.PAX_NUMBER_FIELDS[key](val)
#                    except (TypeError, ValueError):
#                        self.fail("unable to convert pax header field")
#        finally:
#            tar.close()
#
#    def test_pax_extended_header(self):
#        # The fields from the pax header have priority over the
#        # TarInfo.
#        pax_headers = {"path": "foo", "uid": "123"}
#
#        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
#                           encoding="iso8859-1")
#        try:
#            t = tarfile.TarInfo()
#            t.name = "\xe4\xf6\xfc" # non-ASCII
#            t.uid = 8**8 # too large
#            t.pax_headers = pax_headers
#            tar.addfile(t)
#        finally:
#            tar.close()
#
#        tar = tarfile.open(tmpname, encoding="iso8859-1")
#        try:
#            t = tar.getmembers()[0]
#            self.assertEqual(t.pax_headers, pax_headers)
#            self.assertEqual(t.name, "foo")
#            self.assertEqual(t.uid, 123)
#        finally:
#            tar.close()
#
#
################################################################################

def setUpModule():
    tearDownModule()
    os.makedirs(TEMPDIR)

def tearDownModule():
    try:
        os.unlink(tmpname)
    except OSError:
        pass
    try:
        os.rmdir(TEMPDIR)
    except OSError:
        pass
