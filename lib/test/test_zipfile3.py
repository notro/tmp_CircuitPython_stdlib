import struct
import zipfile
import unittest

from tempfile import TemporaryFile
from random import randint, random, getrandbits

from test.support import (TESTFN, findfile, unlink, rmtree)

TESTFN2 = TESTFN + "2"

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
#class DecryptionTests(unittest.TestCase):
#    """Check that ZIP decryption works. Since the library does not
#    support encryption at the moment, we use a pre-generated encrypted
#    ZIP file."""
#
#    data = (
#        b'PK\x03\x04\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00\x1a\x00'
#        b'\x00\x00\x08\x00\x00\x00test.txt\xfa\x10\xa0gly|\xfa-\xc5\xc0=\xf9y'
#        b'\x18\xe0\xa8r\xb3Z}Lg\xbc\xae\xf9|\x9b\x19\xe4\x8b\xba\xbb)\x8c\xb0\xdbl'
#        b'PK\x01\x02\x14\x00\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00'
#        b'\x1a\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00 \x00\xb6\x81'
#        b'\x00\x00\x00\x00test.txtPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x006\x00'
#        b'\x00\x00L\x00\x00\x00\x00\x00' )
#    data2 = (
#        b'PK\x03\x04\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02'
#        b'\x00\x00\x04\x00\x15\x00zeroUT\t\x00\x03\xd6\x8b\x92G\xda\x8b\x92GUx\x04'
#        b'\x00\xe8\x03\xe8\x03\xc7<M\xb5a\xceX\xa3Y&\x8b{oE\xd7\x9d\x8c\x98\x02\xc0'
#        b'PK\x07\x08xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00PK\x01\x02\x17\x03'
#        b'\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00'
#        b'\x04\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00\x00\x00\x00ze'
#        b'roUT\x05\x00\x03\xd6\x8b\x92GUx\x00\x00PK\x05\x06\x00\x00\x00\x00\x01'
#        b'\x00\x01\x00?\x00\x00\x00[\x00\x00\x00\x00\x00' )
#
#    plain = b'zipfile.py encryption test'
#    plain2 = b'\x00'*512
#
#    def setUp(self):
#        with open(TESTFN, "wb") as fp:
#            fp.write(self.data)
#        self.zip = zipfile.ZipFile(TESTFN, "r")
#        with open(TESTFN2, "wb") as fp:
#            fp.write(self.data2)
#        self.zip2 = zipfile.ZipFile(TESTFN2, "r")
#
#    def tearDown(self):
#        self.zip.close()
#        os.unlink(TESTFN)
#        self.zip2.close()
#        os.unlink(TESTFN2)
#
#    def test_no_password(self):
#        # Reading the encrypted file without password
#        # must generate a RunTime exception
#        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
#        self.assertRaises(RuntimeError, self.zip2.read, "zero")
#
#    def test_bad_password(self):
#        self.zip.setpassword(b"perl")
#        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
#        self.zip2.setpassword(b"perl")
#        self.assertRaises(RuntimeError, self.zip2.read, "zero")
#
#    @requires_zlib
#    def test_good_password(self):
#        self.zip.setpassword(b"python")
#        self.assertEqual(self.zip.read("test.txt"), self.plain)
#        self.zip2.setpassword(b"12345")
#        self.assertEqual(self.zip2.read("zero"), self.plain2)
#
#    def test_unicode_password(self):
#        self.assertRaises(TypeError, self.zip.setpassword, "unicode")
#        self.assertRaises(TypeError, self.zip.read, "test.txt", "python")
#        self.assertRaises(TypeError, self.zip.open, "test.txt", pwd="python")
#        self.assertRaises(TypeError, self.zip.extract, "test.txt", pwd="python")
#
class AbstractTestsWithRandomBinaryFiles:
    @classmethod
    def setUpClass(cls):
#        datacount = randint(16, 64)*1024 + randint(1, 1024)
        datacount = 256 + randint(1, 256)                                       ###
        cls.data = b''.join(struct.pack('<f', random()*randint(-1000, 1000))
                            for i in range(datacount))

    def setUp(self):
        # Make a source file with some lines
        with open(TESTFN, "wb") as fp:
            fp.write(self.data)

    def tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)

    def make_test_archive(self, f, compression):
        # Create the ZIP archive
        with zipfile.ZipFile(f, "w", compression) as zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)

# Can't read the entire file into memory at once                                ###
    def zip_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        with zipfile.ZipFile(f, "r", compression) as zipfp:
            testdata = zipfp.read(TESTFN)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)

    def test_read(self):
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

            testdata1 = b''.join(zipdata1)
            self.assertEqual(len(testdata1), len(self.data))
            self.assertEqual(testdata1, self.data)

            testdata2 = b''.join(zipdata2)
            self.assertEqual(len(testdata2), len(self.data))
            self.assertEqual(testdata2, self.data)

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

            testdata = b''.join(zipdata1)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)

    def test_random_open(self):
        for f in get_files(self):
            self.zip_random_open_test(f, self.compression)


class StoredTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                       unittest.TestCase):
    compression = zipfile.ZIP_STORED

#@requires_zlib
#class DeflateTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
#                                        unittest.TestCase):
#    compression = zipfile.ZIP_DEFLATED
#
#@requires_bz2
#class Bzip2TestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
#                                      unittest.TestCase):
#    compression = zipfile.ZIP_BZIP2
#
#@requires_lzma
#class LzmaTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
#                                     unittest.TestCase):
#    compression = zipfile.ZIP_LZMA
#
#
#@requires_zlib
#class TestsWithMultipleOpens(unittest.TestCase):
#    @classmethod
#    def setUpClass(cls):
#        cls.data1 = b'111' + getrandbytes(10000)
#        cls.data2 = b'222' + getrandbytes(10000)
#
#    def make_test_archive(self, f):
#        # Create the ZIP archive
#        with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zipfp:
#            zipfp.writestr('ones', self.data1)
#            zipfp.writestr('twos', self.data2)
#
#    def test_same_file(self):
#        # Verify that (when the ZipFile is in control of creating file objects)
#        # multiple open() calls can be made without interfering with each other.
#        self.make_test_archive(TESTFN2)
#        with zipfile.ZipFile(TESTFN2, mode="r") as zipf:
#            with zipf.open('ones') as zopen1, zipf.open('ones') as zopen2:
#                data1 = zopen1.read(500)
#                data2 = zopen2.read(500)
#                data1 += zopen1.read()
#                data2 += zopen2.read()
#            self.assertEqual(data1, data2)
#            self.assertEqual(data1, self.data1)
#
#    def test_different_file(self):
#        # Verify that (when the ZipFile is in control of creating file objects)
#        # multiple open() calls can be made without interfering with each other.
#        self.make_test_archive(TESTFN2)
#        with zipfile.ZipFile(TESTFN2, mode="r") as zipf:
#            with zipf.open('ones') as zopen1, zipf.open('twos') as zopen2:
#                data1 = zopen1.read(500)
#                data2 = zopen2.read(500)
#                data1 += zopen1.read()
#                data2 += zopen2.read()
#            self.assertEqual(data1, self.data1)
#            self.assertEqual(data2, self.data2)
#
#    def test_interleaved(self):
#        # Verify that (when the ZipFile is in control of creating file objects)
#        # multiple open() calls can be made without interfering with each other.
#        self.make_test_archive(TESTFN2)
#        with zipfile.ZipFile(TESTFN2, mode="r") as zipf:
#            with zipf.open('ones') as zopen1, zipf.open('twos') as zopen2:
#                data1 = zopen1.read(500)
#                data2 = zopen2.read(500)
#                data1 += zopen1.read()
#                data2 += zopen2.read()
#            self.assertEqual(data1, self.data1)
#            self.assertEqual(data2, self.data2)
#
#    def test_read_after_close(self):
#        self.make_test_archive(TESTFN2)
#        with contextlib.ExitStack() as stack:
#            with zipfile.ZipFile(TESTFN2, 'r') as zipf:
#                zopen1 = stack.enter_context(zipf.open('ones'))
#                zopen2 = stack.enter_context(zipf.open('twos'))
#            data1 = zopen1.read(500)
#            data2 = zopen2.read(500)
#            data1 += zopen1.read()
#            data2 += zopen2.read()
#        self.assertEqual(data1, self.data1)
#        self.assertEqual(data2, self.data2)
#
#    def test_read_after_write(self):
#        with zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_DEFLATED) as zipf:
#            zipf.writestr('ones', self.data1)
#            zipf.writestr('twos', self.data2)
#            with zipf.open('ones') as zopen1:
#                data1 = zopen1.read(500)
#        self.assertEqual(data1, self.data1[:500])
#        with zipfile.ZipFile(TESTFN2, 'r') as zipf:
#            data1 = zipf.read('ones')
#            data2 = zipf.read('twos')
#        self.assertEqual(data1, self.data1)
#        self.assertEqual(data2, self.data2)
#
#    def test_write_after_read(self):
#        with zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_DEFLATED) as zipf:
#            zipf.writestr('ones', self.data1)
#            with zipf.open('ones') as zopen1:
#                zopen1.read(500)
#                zipf.writestr('twos', self.data2)
#        with zipfile.ZipFile(TESTFN2, 'r') as zipf:
#            data1 = zipf.read('ones')
#            data2 = zipf.read('twos')
#        self.assertEqual(data1, self.data1)
#        self.assertEqual(data2, self.data2)
#
#    def test_many_opens(self):
#        # Verify that read() and open() promptly close the file descriptor,
#        # and don't rely on the garbage collector to free resources.
#        self.make_test_archive(TESTFN2)
#        with zipfile.ZipFile(TESTFN2, mode="r") as zipf:
#            for x in range(100):
#                zipf.read('ones')
#                with zipf.open('ones') as zopen1:
#                    pass
#        with open(os.devnull) as f:
#            self.assertLess(f.fileno(), 100)
#
#    def tearDown(self):
#        unlink(TESTFN2)
#
#
