import io

import unittest
import tarfile

from test import support

tarname = support.findfile("testtar.tar")

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
class DetectReadTest(TarTest, unittest.TestCase):
    def _testfunc_file(self, name, mode):
        try:
            tar = tarfile.open(name, mode)
        except tarfile.ReadError as e:
            self.fail()
        else:
            tar.close()

    def _testfunc_fileobj(self, name, mode):
        try:
            with open(name, "rb") as f:
                tar = tarfile.open(name, mode, fileobj=f)
        except tarfile.ReadError as e:
            self.fail()
        else:
            tar.close()

    def _test_modes(self, testfunc):
        if self.suffix:
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r:" + self.suffix)
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r|" + self.suffix)
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r:")
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r|")
        testfunc(self.tarname, "r")
        testfunc(self.tarname, "r:" + self.suffix)
        testfunc(self.tarname, "r:*")
        testfunc(self.tarname, "r|" + self.suffix)
        testfunc(self.tarname, "r|*")

    def test_detect_file(self):
        self._test_modes(self._testfunc_file)

    def test_detect_fileobj(self):
        self._test_modes(self._testfunc_fileobj)

#class GzipDetectReadTest(GzipTest, DetectReadTest):
#    pass
#
#class Bz2DetectReadTest(Bz2Test, DetectReadTest):
#    def test_detect_stream_bz2(self):
#        # Originally, tarfile's stream detection looked for the string
#        # "BZh91" at the start of the file. This is incorrect because
#        # the '9' represents the blocksize (900kB). If the file was
#        # compressed using another blocksize autodetection fails.
#        with open(tarname, "rb") as fobj:
#            data = fobj.read()
#
#        # Compress with blocksize 100kB, the file starts with "BZh11".
#        with bz2.BZ2File(tmpname, "wb", compresslevel=1) as fobj:
#            fobj.write(data)
#
#        self._testfunc_file(tmpname, "r|*")
#
#class LzmaDetectReadTest(LzmaTest, DetectReadTest):
#    pass
#
#
################################################################################
