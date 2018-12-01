import os

import unittest
import tarfile

from test import support


TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarname = support.findfile("testtar.tar")
tmpname = os.path.join(TEMPDIR, "tmp.tar")

################################################################################
class UstarUnicodeTest(unittest.TestCase):

    format = tarfile.USTAR_FORMAT

    def test_iso8859_1_filename(self):
        self._test_unicode_filename("iso8859-1")

    def test_utf7_filename(self):
        self._test_unicode_filename("utf7")

    def test_utf8_filename(self):
        self._test_unicode_filename("utf-8")

    def _test_unicode_filename(self, encoding):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding=encoding, errors="strict")
        try:
            name = "\xe4\xf6\xfc"
            tar.addfile(tarfile.TarInfo(name))
        finally:
            tar.close()

        tar = tarfile.open(tmpname, encoding=encoding)
        try:
            self.assertEqual(tar.getmembers()[0].name, name)
        finally:
            tar.close()

#    def test_unicode_filename_error(self):
#        tar = tarfile.open(tmpname, "w", format=self.format,
#                           encoding="ascii", errors="strict")
#        try:
#            tarinfo = tarfile.TarInfo()
#
#            tarinfo.name = "\xe4\xf6\xfc"
#            self.assertRaises(UnicodeError, tar.addfile, tarinfo)
#
#            tarinfo.name = "foo"
#            tarinfo.uname = "\xe4\xf6\xfc"
#            self.assertRaises(UnicodeError, tar.addfile, tarinfo)
#        finally:
#            tar.close()
#
    def test_unicode_argument(self):
        tar = tarfile.open(tarname, "r",
                           encoding="iso8859-1", errors="strict")
        try:
            for t in tar:
                self.assertIs(type(t.name), str)
                self.assertIs(type(t.linkname), str)
                self.assertIs(type(t.uname), str)
                self.assertIs(type(t.gname), str)
        finally:
            tar.close()

    def test_uname_unicode(self):
        t = tarfile.TarInfo("foo")
        t.uname = "\xe4\xf6\xfc"
        t.gname = "\xe4\xf6\xfc"

        tar = tarfile.open(tmpname, mode="w", format=self.format,
                           encoding="iso8859-1")
        try:
            tar.addfile(t)
        finally:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        try:
            t = tar.getmember("foo")
            self.assertEqual(t.uname, "\xe4\xf6\xfc")
            self.assertEqual(t.gname, "\xe4\xf6\xfc")

            if self.format != tarfile.PAX_FORMAT:
                tar.close()
                tar = tarfile.open(tmpname, encoding="ascii")
                t = tar.getmember("foo")
#                self.assertEqual(t.uname, "\udce4\udcf6\udcfc")
#                self.assertEqual(t.gname, "\udce4\udcf6\udcfc")
        finally:
            tar.close()


class GNUUnicodeTest(UstarUnicodeTest):

    format = tarfile.GNU_FORMAT

    @unittest.expectedFailure                                                   ###
    def test_bad_pax_header(self):
        # Test for issue #8633. GNU tar <= 1.23 creates raw binary fields
        # without a hdrcharset=BINARY header.
        for encoding, name in (
                ("utf-8", "pax/bad-pax-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/bad-pax-\xe4\xf6\xfc"),):
            with tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") as tar:
                try:
                    t = tar.getmember(name)
                except KeyError:
                    self.fail("unable to read bad GNU tar pax header")


class PAXUnicodeTest(UstarUnicodeTest):

    format = tarfile.PAX_FORMAT

    # PAX_FORMAT ignores encoding in write mode.
    test_unicode_filename_error = None

    @unittest.expectedFailure                                                   ###
    def test_binary_header(self):
        # Test a POSIX.1-2008 compatible header with a hdrcharset=BINARY field.
        for encoding, name in (
                ("utf-8", "pax/hdrcharset-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/hdrcharset-\xe4\xf6\xfc"),):
            with tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") as tar:
                try:
                    t = tar.getmember(name)
                except KeyError:
                    self.fail("unable to read POSIX.1-2008 binary header")


################################################################################

def setUpModule():
    tearDownModule()                                                            ### Might run out of memory and this wasn't called
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)
