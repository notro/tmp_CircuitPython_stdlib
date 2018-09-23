# Copyright (C) 2003 Python Software Foundation

import unittest
import shutil
import tempfile
import sys
import stat
import os
import os.path
import errno
import functools
from shutil import (Error, SameFileError)                                       ###

from test import support
from test.support import TESTFN                                                 ###


TESTFN2 = TESTFN + "2"

FileNotFoundError = OSError                                                     ###
NotADirectoryError = OSError                                                    ###

def _fake_rename(*args, **kwargs):
    # Pretend the destination path is on a different filesystem.
    raise OSError(getattr(errno, 'EXDEV', 18), "Invalid cross-device link")

def mock_rename(func):
    def wrap(*args, **kwargs):
        try:
            builtin_rename = os.rename
            os.rename = _fake_rename
            return func(*args, **kwargs)
        finally:
            os.rename = builtin_rename
    return wrap

def write_file(path, content, binary=False):
    """Write *content* to a file located at *path*.

    If *path* is a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* is true, the file will be opened in binary
    mode.
    """
    if isinstance(path, tuple):
        path = os.path.join(*path)
    with open(path, 'wb' if binary else 'w') as fp:
        fp.write(content)

def read_file(path, binary=False):
    """Return contents from a file located at *path*.

    If *path* is a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* is true, the file will be opened in binary
    mode.
    """
    if isinstance(path, tuple):
        path = os.path.join(*path)
    with open(path, 'rb' if binary else 'r') as fp:
        return fp.read()

def rlistdir(path):
    res = []
    for name in sorted(os.listdir(path)):
        p = os.path.join(path, name)
        if os.path.isdir(p) and not os.path.islink(p):
            res.append(name + '/')
            for n in rlistdir(p):
                res.append(name + '/' + n)
        else:
            res.append(name)
    return res


class TestShutil(unittest.TestCase):

    def setUp(self):
        super(TestShutil, self).setUp()
        self.tempdirs = []

    def tearDown(self):
        super(TestShutil, self).tearDown()
        while self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name in ('nt', 'cygwin'))


    def mkdtemp(self):
        """Create a temporary directory that will be cleaned up.

        Returns the path of the directory.
        """
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        return d


    def test_rmtree_errors(self):
        # filename is guaranteed not to exist
        filename = tempfile.mktemp()
        self.assertRaises(FileNotFoundError, shutil.rmtree, filename)
        # test that ignore_errors option is honored
        shutil.rmtree(filename, ignore_errors=True)

        # existing file
        tmpdir = self.mkdtemp()
        write_file((tmpdir, "tstfile"), "")
        filename = os.path.join(tmpdir, "tstfile")
        with self.assertRaises(NotADirectoryError) as cm:
            shutil.rmtree(filename)
        # The reason for this rather odd construct is that Windows sprinkles
        # a \*.* at the end of file names. But only sometimes on some buildbots
        possible_args = [filename, os.path.join(filename, '*.*')]
        self.assertTrue(os.path.exists(filename))
        # test that ignore_errors option is honored
        shutil.rmtree(filename, ignore_errors=True)
        self.assertTrue(os.path.exists(filename))
        errors = []
        def onerror(*args):
            errors.append(args)
        shutil.rmtree(filename, onerror=onerror)
        self.assertEqual(len(errors), 2)
        self.assertIs(errors[0][0], os.listdir)
        self.assertEqual(errors[0][1], filename)
        self.assertIsInstance(errors[0][2][1], NotADirectoryError)
        self.assertIs(errors[1][0], os.rmdir)
        self.assertEqual(errors[1][1], filename)
        self.assertIsInstance(errors[1][2][1], NotADirectoryError)



    def check_args_to_onerror(self, func, arg, exc):
        # test_rmtree_errors deliberately runs rmtree
        # on a directory that is chmod 500, which will fail.
        # This function is run when shutil.rmtree fails.
        # 99.9% of the time it initially fails to remove
        # a file in the directory, so the first time through
        # func is os.remove.
        # However, some Linux machines running ZFS on
        # FUSE experienced a failure earlier in the process
        # at os.listdir.  The first failure may legally
        # be either.
        if self.errorState < 2:
            if func is os.unlink:
                self.assertEqual(arg, self.child_file_path)
            elif func is os.rmdir:
                self.assertEqual(arg, self.child_dir_path)
            else:
                self.assertIs(func, os.listdir)
                self.assertIn(arg, [TESTFN, self.child_dir_path])
            self.assertTrue(issubclass(exc[0], OSError))
            self.errorState += 1
        else:
            self.assertEqual(func, os.rmdir)
            self.assertEqual(arg, TESTFN)
            self.assertTrue(issubclass(exc[0], OSError))
            self.errorState = 3

    def test_rmtree_does_not_choke_on_failing_lstat(self):
        try:
            orig_lstat = os.lstat
            def raiser(fn, *args, **kwargs):
                if fn != TESTFN:
                    raise OSError()
                else:
                    return orig_lstat(fn)
            os.lstat = raiser

            os.mkdir(TESTFN)
            write_file((TESTFN, 'foo'), 'foo')
            shutil.rmtree(TESTFN)
        finally:
            os.lstat = orig_lstat


    def test_copytree_simple(self):
        src_dir = tempfile.mkdtemp()
        dst_dir = os.path.join(tempfile.mkdtemp(), 'destination')
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, os.path.dirname(dst_dir))
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        shutil.copytree(src_dir, dst_dir)
        self.assertTrue(os.path.isfile(os.path.join(dst_dir, 'test.txt')))
        self.assertTrue(os.path.isdir(os.path.join(dst_dir, 'test_dir')))
        self.assertTrue(os.path.isfile(os.path.join(dst_dir, 'test_dir',
                                                    'test.txt')))
        actual = read_file((dst_dir, 'test.txt'))
        self.assertEqual(actual, '123')
        actual = read_file((dst_dir, 'test_dir', 'test.txt'))
        self.assertEqual(actual, '456')


    def test_copytree_with_exclude(self):
        # creating data
        join = os.path.join
        exists = os.path.exists
        src_dir = tempfile.mkdtemp()
        try:
            dst_dir = join(tempfile.mkdtemp(), 'destination')
            write_file((src_dir, 'test.txt'), '123')
            write_file((src_dir, 'test.tmp'), '123')
            os.mkdir(join(src_dir, 'test_dir'))
            write_file((src_dir, 'test_dir', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2'))
            write_file((src_dir, 'test_dir2', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2', 'subdir'))
            os.mkdir(join(src_dir, 'test_dir2', 'subdir2'))
            write_file((src_dir, 'test_dir2', 'subdir', 'test.txt'), '456')
            write_file((src_dir, 'test_dir2', 'subdir2', 'test.py'), '456')

            # testing glob-like patterns
            try:
                patterns = shutil.ignore_patterns('*.tmp', 'test_dir2')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should not be copied
                self.assertTrue(exists(join(dst_dir, 'test.txt')))
                self.assertFalse(exists(join(dst_dir, 'test.tmp')))
                self.assertFalse(exists(join(dst_dir, 'test_dir2')))
            finally:
                shutil.rmtree(dst_dir)
            try:
                patterns = shutil.ignore_patterns('*.tmp', 'subdir*')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should not be copied
                self.assertFalse(exists(join(dst_dir, 'test.tmp')))
                self.assertFalse(exists(join(dst_dir, 'test_dir2', 'subdir2')))
                self.assertFalse(exists(join(dst_dir, 'test_dir2', 'subdir')))
            finally:
                shutil.rmtree(dst_dir)

            # testing callable-style
            try:
                def _filter(src, names):
                    res = []
                    for name in names:
                        path = os.path.join(src, name)

                        if (os.path.isdir(path) and
                            path.split()[-1] == 'subdir'):
                            res.append(name)
                        elif os.path.splitext(path)[-1] in ('.py'):
                            res.append(name)
                    return res

                shutil.copytree(src_dir, dst_dir, ignore=_filter)

                # checking the result: some elements should not be copied
                self.assertFalse(exists(join(dst_dir, 'test_dir2', 'subdir2',
                                             'test.py')))
                self.assertFalse(exists(join(dst_dir, 'test_dir2', 'subdir')))

            finally:
                shutil.rmtree(dst_dir)
        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(os.path.dirname(dst_dir))


    def test_copytree_special_func(self):

        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        copied = []
        def _copy(src, dst):
            copied.append((src, dst))

        shutil.copytree(src_dir, dst_dir, copy_function=_copy)
        self.assertEqual(len(copied), 2)


    def _copy_file(self, method):
        fname = 'test.txt'
        tmpdir = self.mkdtemp()
        write_file((tmpdir, fname), 'xxx')
        file1 = os.path.join(tmpdir, fname)
        tmpdir2 = self.mkdtemp()
        method(file1, tmpdir2)
        file2 = os.path.join(tmpdir2, fname)
        return (file1, file2)


    def _create_files(self, base_dir='dist'):
        # creating something to tar
        root_dir = self.mkdtemp()
        dist = os.path.join(root_dir, base_dir)
        os.makedirs(dist, exist_ok=True)
        write_file((dist, 'file1'), 'xxx')
        write_file((dist, 'file2'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub'))
        write_file((dist, 'sub', 'file3'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub2'))
        if base_dir:
            write_file((root_dir, 'outer'), 'xxx')
        return root_dir, base_dir


    def test_copy_return_value(self):
        # copy and copy2 both return their destination path.
        for fn in (shutil.copy, shutil.copy2):
            src_dir = self.mkdtemp()
            dst_dir = self.mkdtemp()
            src = os.path.join(src_dir, 'foo')
            write_file(src, 'foo')
            rv = fn(src, dst_dir)
            self.assertEqual(rv, os.path.join(dst_dir, 'foo'))
            rv = fn(src, os.path.join(dst_dir, 'bar'))
            self.assertEqual(rv, os.path.join(dst_dir, 'bar'))

    def test_copyfile_return_value(self):
        # copytree returns its destination path.
        src_dir = self.mkdtemp()
        dst_dir = self.mkdtemp()
        dst_file = os.path.join(dst_dir, 'bar')
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        rv = shutil.copyfile(src_file, dst_file)
        self.assertTrue(os.path.exists(rv))
        self.assertEqual(read_file(src_file), read_file(dst_file))

    def test_copyfile_same_file(self):
        # copyfile() should raise SameFileError if the source and destination
        # are the same.
        src_dir = self.mkdtemp()
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        self.assertRaises(SameFileError, shutil.copyfile, src_file, src_file)
        # But Error should work too, to stay backward compatible.
        self.assertRaises(Error, shutil.copyfile, src_file, src_file)

    def test_copytree_return_value(self):
        # copytree returns its destination path.
        src_dir = self.mkdtemp()
        dst_dir = src_dir + "dest"
        self.addCleanup(shutil.rmtree, dst_dir, True)
        src = os.path.join(src_dir, 'foo')
        write_file(src, 'foo')
        rv = shutil.copytree(src_dir, dst_dir)
        self.assertEqual(['foo'], os.listdir(rv))




class TestMove(unittest.TestCase):

    def setUp(self):
        filename = "foo"
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.src_file = os.path.join(self.src_dir, filename)
        self.dst_file = os.path.join(self.dst_dir, filename)
        with open(self.src_file, "wb") as f:
            f.write(b"spam")

    def tearDown(self):
        for d in (self.src_dir, self.dst_dir):
            try:
                if d:
                    shutil.rmtree(d)
            except:
                pass

    def _check_move_file(self, src, dst, real_dst):
        with open(src, "rb") as f:
            contents = f.read()
        shutil.move(src, dst)
        with open(real_dst, "rb") as f:
            self.assertEqual(contents, f.read())
        self.assertFalse(os.path.exists(src))

    def _check_move_dir(self, src, dst, real_dst):
        contents = sorted(os.listdir(src))
        shutil.move(src, dst)
        self.assertEqual(contents, sorted(os.listdir(real_dst)))
        self.assertFalse(os.path.exists(src))

    def test_move_file(self):
        # Move a file to another location on the same filesystem.
        self._check_move_file(self.src_file, self.dst_file, self.dst_file)

    def test_move_file_to_dir(self):
        # Move a file inside an existing dir on the same filesystem.
        self._check_move_file(self.src_file, self.dst_dir, self.dst_file)

    @mock_rename
    def test_move_file_other_fs(self):
        # Move a file to an existing dir on another filesystem.
        self.test_move_file()

    @mock_rename
    def test_move_file_to_dir_other_fs(self):
        # Move a file to another location on another filesystem.
        self.test_move_file_to_dir()

    def test_move_dir(self):
        # Move a dir to another location on the same filesystem.
        dst_dir = tempfile.mktemp()
        try:
            self._check_move_dir(self.src_dir, dst_dir, dst_dir)
        finally:
            try:
                shutil.rmtree(dst_dir)
            except:
                pass

    @mock_rename
    def test_move_dir_other_fs(self):
        # Move a dir to another location on another filesystem.
        self.test_move_dir()

    def test_move_dir_to_dir(self):
        # Move a dir inside an existing dir on the same filesystem.
        self._check_move_dir(self.src_dir, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    @mock_rename
    def test_move_dir_to_dir_other_fs(self):
        # Move a dir inside an existing dir on another filesystem.
        self.test_move_dir_to_dir()

    def test_move_dir_sep_to_dir(self):
        self._check_move_dir(self.src_dir + os.path.sep, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))


    def test_existing_file_inside_dest_dir(self):
        # A file with the same name inside the destination dir already exists.
        with open(self.dst_file, "wb"):
            pass
        self.assertRaises(shutil.Error, shutil.move, self.src_file, self.dst_dir)

    @unittest.expectedFailure                                                   ### https://github.com/adafruit/circuitpython/issues/1192
    def test_dont_move_dir_in_itself(self):
        # Moving a dir inside itself raises an Error.
        dst = os.path.join(self.src_dir, "bar")
        self.assertRaises(shutil.Error, shutil.move, self.src_dir, dst)

    def test_destinsrc_false_negative(self):
        os.mkdir(TESTFN)
        try:
            for src, dst in [('srcdir', 'srcdir/dest')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertTrue(shutil._destinsrc(src, dst),
                             msg='_destinsrc() wrongly concluded that '
                             'dst (%s) is not in src (%s)' % (dst, src))
        finally:
            shutil.rmtree(TESTFN, ignore_errors=True)

    def test_destinsrc_false_positive(self):
        os.mkdir(TESTFN)
        try:
            for src, dst in [('srcdir', 'src/dest'), ('srcdir', 'srcdir.new')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertFalse(shutil._destinsrc(src, dst),
                            msg='_destinsrc() wrongly concluded that '
                            'dst (%s) is in src (%s)' % (dst, src))
        finally:
            shutil.rmtree(TESTFN, ignore_errors=True)


    def test_move_return_value(self):
        rv = shutil.move(self.src_file, self.dst_dir)
        self.assertEqual(rv,
                os.path.join(self.dst_dir, os.path.basename(self.src_file)))

    def test_move_as_rename_return_value(self):
        rv = shutil.move(self.src_file, os.path.join(self.dst_dir, 'bar'))
        self.assertEqual(rv, os.path.join(self.dst_dir, 'bar'))


class TestCopyFile(unittest.TestCase):

    _delete = False

    class Faux(object):
        _entered = False
        _exited_with = None
        _raised = False
        def __init__(self, raise_in_exit=False, suppress_at_exit=True):
            self._raise_in_exit = raise_in_exit
            self._suppress_at_exit = suppress_at_exit
        def read(self, *args):
            return ''
        def __enter__(self):
            self._entered = True
        def __exit__(self, exc_type, exc_val, exc_tb):
            self._exited_with = exc_type, exc_val, exc_tb
            if self._raise_in_exit:
                self._raised = True
                raise OSError("Cannot close")
            return self._suppress_at_exit

    def tearDown(self):
        if self._delete:
            del shutil.open

    def _set_shutil_open(self, func):
        shutil.open = func
        self._delete = True

    def test_w_source_open_fails(self):
        def _open(filename, mode='r'):
            if filename == 'srcfile':
                raise OSError('Cannot open "srcfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError, shutil.copyfile, 'srcfile', 'destfile')

    def test_w_dest_open_fails(self):

        srcfile = self.Faux()

        def _open(filename, mode='r'):
            if filename == 'srcfile':
                return srcfile
            if filename == 'destfile':
                raise OSError('Cannot open "destfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertTrue(srcfile._entered)
        self.assertTrue(srcfile._exited_with[0] is OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot open "destfile"',))

    def test_w_dest_close_fails(self):

        srcfile = self.Faux()
        destfile = self.Faux(True)

        def _open(filename, mode='r'):
            if filename == 'srcfile':
                return srcfile
            if filename == 'destfile':
                return destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertTrue(srcfile._entered)
        self.assertTrue(destfile._entered)
        self.assertTrue(destfile._raised)
        self.assertTrue(srcfile._exited_with[0] is OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot close',))

    def test_w_source_close_fails(self):

        srcfile = self.Faux(True)
        destfile = self.Faux()

        def _open(filename, mode='r'):
            if filename == 'srcfile':
                return srcfile
            if filename == 'destfile':
                return destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError,
                          shutil.copyfile, 'srcfile', 'destfile')
        self.assertTrue(srcfile._entered)
        self.assertTrue(destfile._entered)
        self.assertFalse(destfile._raised)
        self.assertTrue(srcfile._exited_with[0] is None)
        self.assertTrue(srcfile._raised)

    def test_move_dir_caseinsensitive(self):
        # Renames a folder to the same name
        # but a different case.

        self.src_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.src_dir, True)
        dst_dir = os.path.join(
                os.path.dirname(self.src_dir),
                os.path.basename(self.src_dir).upper())
        self.assertNotEqual(self.src_dir, dst_dir)

        try:
            shutil.move(self.src_dir, dst_dir)
            self.assertTrue(os.path.isdir(dst_dir))
        finally:
            os.rmdir(dst_dir)

