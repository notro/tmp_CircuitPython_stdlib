"""Unit tests for the io module."""

# Tests of io are scattered over the test suite:
# * test_bufio - tests file buffering
# * test_memoryio - tests BytesIO and StringIO
# * test_fileio - tests FileIO
# * test_file - tests the file interface
# * test_io - tests everything else in the io module
# * test_univnewlines - tests universal newline support
# * test_largefile - tests operations on a file greater than 2**32 bytes
#     (only enabled with -ulargefile)

################################################################################
# ATTENTION TEST WRITERS!!!
################################################################################
# When writing tests for io, it's important to test both the C and Python
# implementations. This is usually done by writing a base test that refers to
# the type it is testing as an attribute. Then it provides custom subclasses to
# test both implementations. This file has lots of examples.
################################################################################

import errno
import os
import sys
import unittest
from test import support

import io  # C implementation of io
import io as pyio                                                               ###

def _default_chunk_size():
    """Get the default TextIOWrapper chunk size"""
    with open(__file__, "r", encoding="latin-1") as f:
        return f._CHUNK_SIZE




class MockFileIO:

    def __init__(self, data):
        self.read_history = []
        super().__init__(data)

    def read(self, n=None):
        res = super().read(n)
        self.read_history.append(None if res is None else len(res))
        return res

    def readinto(self, b):
        res = super().readinto(b)
        self.read_history.append(res)
        return res


class PyMockFileIO(MockFileIO, pyio.BytesIO):
    pass


class MockUnseekableIO:
    def seekable(self):
        return False

    def seek(self, *args):
        raise self.UnsupportedOperation("not seekable")

    def tell(self, *args):
        raise self.UnsupportedOperation("not seekable")


class PyMockUnseekableIO(MockUnseekableIO, pyio.BytesIO):
    UnsupportedOperation = OSError                                              ###




#@unittest.skip('MemoryError')                                                   ###
class IOTest(unittest.TestCase):

    def setUp(self):
        support.unlink(support.TESTFN)

    def tearDown(self):
        support.unlink(support.TESTFN)

    def write_ops(self, f):
        self.assertEqual(f.write(b"blah."), 5)
        f.seek(0)

        self.assertEqual(f.write(b"blah."), 5)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"Hello."), 6)
        self.assertEqual(f.seek(-1, 1), 5)
        self.assertEqual(f.write(bytearray(b" world\n")), 7)                    ### Since we don't have truncate
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"h"), 1)
        self.assertEqual(f.seek(-1, 2), 11)                                     ### truncate...

        self.assertRaises(TypeError, f.seek, 0.0)

    def read_ops(self, f, buffered=False):
        data = f.read(5)
        self.assertEqual(data, b"hello")
        data = bytearray(data)
        self.assertEqual(f.readinto(data), 5)
        self.assertEqual(data, b" worl")
        self.assertEqual(f.readinto(data), 2)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[:2], b"d\n")
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.read(20), b"hello world\n")
        self.assertEqual(f.read(1), b"")
        self.assertEqual(f.readinto(bytearray(b"x")), 0)
        self.assertEqual(f.seek(-6, 2), 6)
        self.assertEqual(f.read(5), b"world")
        self.assertEqual(f.read(0), b"")
        self.assertEqual(f.readinto(bytearray()), 0)
        self.assertEqual(f.seek(-6, 1), 5)
        self.assertEqual(f.read(5), b" worl")
        self.assertRaises(TypeError, f.seek, 0.0)
        if buffered:
            f.seek(0)
            self.assertEqual(f.read(), b"hello world\n")
            f.seek(6)
            self.assertEqual(f.read(), b"world\n")
            self.assertEqual(f.read(), b"")


    @unittest.skip('Hangs')                                                     ###
    def test_invalid_operations(self):
        # Try writing on a file opened in read mode and vice-versa.
        exc = self.UnsupportedOperation
        for mode in ("w", "wb"):
            with self.open(support.TESTFN, mode) as fp:
                self.assertRaises(exc, fp.read)
                self.assertRaises(exc, fp.readline)
        with self.open(support.TESTFN, "wb", buffering=0) as fp:
            self.assertRaises(exc, fp.read)
            self.assertRaises(exc, fp.readline)
        with self.open(support.TESTFN, "rb", buffering=0) as fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        with self.open(support.TESTFN, "rb") as fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        with self.open(support.TESTFN, "r") as fp:
            self.assertRaises(exc, fp.write, "blah")
            self.assertRaises(exc, fp.writelines, ["blah\n"])
            # Non-zero seeking from current or end pos
            self.assertRaises(exc, fp.seek, 1, self.SEEK_CUR)
            self.assertRaises(exc, fp.seek, -1, self.SEEK_END)

    def test_raw_file_io(self):
        with self.open(support.TESTFN, "wb", buffering=0) as f:
            self.write_ops(f)
        with self.open(support.TESTFN, "rb", buffering=0) as f:
            self.read_ops(f)

    def test_buffered_file_io(self):
        with self.open(support.TESTFN, "wb") as f:
            self.write_ops(f)
        with self.open(support.TESTFN, "rb") as f:
            self.read_ops(f, True)

    def test_readline(self):
        with self.open(support.TESTFN, "wb") as f:
            f.write(b"abc\ndef\nxyzzy\nfoo\x00bar\nanother line")
        with self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.readline(), b"abc\n")
            self.assertEqual(f.readline(10), b"def\n")
            self.assertEqual(f.readline(2), b"xy")
            self.assertEqual(f.readline(4), b"zzy\n")
            self.assertEqual(f.readline(), b"foo\x00bar\n")

    def test_raw_bytes_io(self):
        f = self.BytesIO()
        self.write_ops(f)
        data = f.getvalue()
        self.assertEqual(data, b"hello world\n")
        f = self.BytesIO(data)
        self.read_ops(f, True)


    def test_with_open(self):
        for bufsize in (0, 1, 100):
            f = None
            with self.open(support.TESTFN, "wb", bufsize) as f:
                f.write(b"xxx")
            f = None
            try:
                with self.open(support.TESTFN, "wb", bufsize) as f:
                    1/0
            except ZeroDivisionError:
                pass                                                            ###
            else:
                self.fail("1/0 didn't raise an exception")


    def test_close_flushes(self):
        with self.open(support.TESTFN, "wb") as f:
            f.write(b"xxx")
        with self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"xxx")

    def test_multi_close(self):
        f = self.open(support.TESTFN, "wb", buffering=0)
        f.close()
        f.close()
        f.close()




class PyIOTest(IOTest):
    pass


# XXX Tests for open()

class MiscIOTest(unittest.TestCase):

    def tearDown(self):
        support.unlink(support.TESTFN)

    def test_io_after_close(self):
        ValueError = OSError                                                    ###
        for kwargs in [
                {"mode": "w"},
            ]:
            f = self.open(support.TESTFN, **kwargs)
            f.close()
            self.assertRaises(ValueError, f.flush)
            self.assertRaises(ValueError, f.read)
            if hasattr(f, "readinto"):
                self.assertRaises(ValueError, f.readinto, bytearray(1024))
            self.assertRaises(ValueError, f.readline)
            self.assertRaises(ValueError, f.readlines)
            self.assertRaises(ValueError, next, f)

    def test_create_fail(self):
        FileExistsError = OSError                                               ###
        # 'x' mode fails if file is existing
        with self.open(support.TESTFN, 'w'):
            pass
        self.assertRaises(FileExistsError, self.open, support.TESTFN, 'x')

    def test_create_writes(self):
        # 'x' mode opens for writing
        with self.open(support.TESTFN, 'xb') as f:
            f.write(b"spam")
        with self.open(support.TESTFN, 'rb') as f:
            self.assertEqual(b"spam", f.read())


class PyMiscIOTest(MiscIOTest):
    io = pyio


class OpenWrapper:                                                              ###
    def __new__(cls, *args, **kwargs):                                          ###
        return open(*args, **kwargs)                                            ###
                                                                                ###
                                                                                ###
def load_tests(*args):
    tests = (PyIOTest,                                                          ###
             PyMiscIOTest,                                                      ###
             )                                                                  ###

    # Put the namespaces of the IO module we are testing and some useful mock
    # classes in the __dict__ of each test.
    mocks = (MockFileIO, MockUnseekableIO)                                      ###
    all_members = ['BytesIO', 'FileIO', 'StringIO', 'TextIOWrapper', 'open', 'SEEK_SET', 'SEEK_CUR', 'SEEK_END']  ###
    py_io_ns = {name : getattr(pyio, name) for name in all_members}
    globs = globals()
    py_io_ns.update((x.__name__, globs["Py" + x.__name__]) for x in mocks)
    # Avoid turning open into a bound method.
    py_io_ns["open"] = OpenWrapper                                              ###
    for test in tests:
            for name, obj in py_io_ns.items():
                setattr(test, name, obj)

    suite = unittest.TestSuite([unittest.makeSuite(test) for test in tests])
    return suite

