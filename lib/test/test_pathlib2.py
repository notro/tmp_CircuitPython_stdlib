import io
import os
import errno
import pathlib
import stat
import sys
import unittest

from test import support
TESTFN = support.TESTFN

FileNotFoundError = OSError


################################################################################################################
################################################################################################################
#
# Tests for the concrete classes
#

# Make sure any symbolic links in the base test path are resolved
BASE = os.path.realpath(TESTFN)
join = lambda *x: os.path.join(BASE, *x)
rel_join = lambda *x: os.path.join(TESTFN, *x)

#def symlink_skip_reason():
#    if not pathlib.supports_symlinks:
#        return "no system support for symlinks"
#    try:
#        os.symlink(__file__, BASE)
#    except OSError as e:
#        return str(e)
#    else:
#        support.unlink(BASE)
#    return None
#
#symlink_skip_reason = symlink_skip_reason()
symlink_skip_reason = True                                                      ###
#
#only_nt = unittest.skipIf(os.name != 'nt',
#                          'test requires a Windows-compatible system')
#only_posix = unittest.skipIf(os.name == 'nt',
#                             'test requires a POSIX-compatible system')
#with_symlinks = unittest.skipIf(symlink_skip_reason, symlink_skip_reason)
#
#
#@only_posix
#class PosixPathAsPureTest(PurePosixPathTest):
#    cls = pathlib.PosixPath
#
#@only_nt
#class WindowsPathAsPureTest(PureWindowsPathTest):
#    cls = pathlib.WindowsPath
#
#
class _BasePathTest(object):
    """Tests for the FS-accessing functionalities of the Path classes."""

    # (BASE)
    #  |
    #  |-- brokenLink -> non-existing
    #  |-- dirA
    #  |   `-- linkC -> ../dirB
    #  |-- dirB
    #  |   |-- fileB
    #  |   `-- linkD -> ../dirB
    #  |-- dirC
    #  |   |-- dirD
    #  |   |   `-- fileD
    #  |   `-- fileC
    #  |-- dirE  # No permissions
    #  |-- fileA
    #  |-- linkA -> fileA
    #  `-- linkB -> dirB
    #

    def setUp(self):
        def cleanup():
#            os.chmod(join('dirE'), 0o777)
            support.rmtree(BASE)
        self.addCleanup(cleanup)
        os.mkdir(BASE)
        os.mkdir(join('dirA'))
        os.mkdir(join('dirB'))
        os.mkdir(join('dirC'))
        os.mkdir(join('dirC', 'dirD'))
        os.mkdir(join('dirE'))
        with open(join('fileA'), 'wb') as f:
            f.write(b"this is file A\n")
        with open(join('dirB', 'fileB'), 'wb') as f:
            f.write(b"this is file B\n")
        with open(join('dirC', 'fileC'), 'wb') as f:
            f.write(b"this is file C\n")
        with open(join('dirC', 'dirD', 'fileD'), 'wb') as f:
            f.write(b"this is file D\n")
#        os.chmod(join('dirE'), 0)
#        if not symlink_skip_reason:
#            # Relative symlinks
#            os.symlink('fileA', join('linkA'))
#            os.symlink('non-existing', join('brokenLink'))
#            self.dirlink('dirB', join('linkB'))
#            self.dirlink(os.path.join('..', 'dirB'), join('dirA', 'linkC'))
#            # This one goes upwards, creating a loop
#            self.dirlink(os.path.join('..', 'dirB'), join('dirB', 'linkD'))

#    if os.name == 'nt':
#        # Workaround for http://bugs.python.org/issue13772
#        def dirlink(self, src, dest):
#            os.symlink(src, dest, target_is_directory=True)
#    else:
#        def dirlink(self, src, dest):
#            os.symlink(src, dest)
#
    def assertSame(self, path_a, path_b):
        self.assertTrue(os.path.samefile(str(path_a), str(path_b)),
                        "%r and %r don't point to the same file" %
                        (path_a, path_b))

    def assertFileNotFound(self, func, *args, **kwargs):
        with self.assertRaises(FileNotFoundError) as cm:
            func(*args, **kwargs)
#        self.assertEqual(cm.exception.errno, errno.ENOENT)
        self.assertEqual(cm.exception.args[0], errno.ENOENT)                    ###

    def _test_cwd(self, p):
        q = self.cls(os.getcwd())
        self.assertEqual(p, q)
        self.assertEqual(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertTrue(p.is_absolute())

    def test_cwd(self):
        p = self.cls.cwd()
        self._test_cwd(p)

#    def test_empty_path(self):
#        # The empty path points to '.'
#        p = self.cls('')
#        self.assertEqual(p.stat(), os.stat('.'))
#
    def test_exists(self):
        P = self.cls
        p = P(BASE)
        self.assertIs(True, p.exists())
        self.assertIs(True, (p / 'dirA').exists())
        self.assertIs(True, (p / 'fileA').exists())
        self.assertIs(False, (p / 'fileA' / 'bah').exists())
#        if not symlink_skip_reason:
#            self.assertIs(True, (p / 'linkA').exists())
#            self.assertIs(True, (p / 'linkB').exists())
#            self.assertIs(True, (p / 'linkB' / 'fileB').exists())
#            self.assertIs(False, (p / 'linkA' / 'bah').exists())
        self.assertIs(False, (p / 'foo').exists())
        self.assertIs(False, P('/xyzzy').exists())

    def test_open_common(self):
        p = self.cls(BASE)
        with (p / 'fileA').open('r') as f:
#            self.assertIsInstance(f, io.TextIOBase)
            self.assertEqual(f.read(), "this is file A\n")
        with (p / 'fileA').open('rb') as f:
#            self.assertIsInstance(f, io.BufferedIOBase)
            self.assertEqual(f.read().strip(), b"this is file A")
        with (p / 'fileA').open('rb', buffering=0) as f:
#            self.assertIsInstance(f, io.RawIOBase)
            self.assertEqual(f.read().strip(), b"this is file A")

    def test_iterdir(self):
        P = self.cls
        p = P(BASE)
        it = p.iterdir()
        paths = set(it)
        expected = ['dirA', 'dirB', 'dirC', 'dirE', 'fileA']
#        if not symlink_skip_reason:
#            expected += ['linkA', 'linkB', 'brokenLink']
        self.assertEqual(paths, { P(BASE, q) for q in expected })

#    @with_symlinks
#    def test_iterdir_symlink(self):
#        # __iter__ on a symlink to a directory
#        P = self.cls
#        p = P(BASE, 'linkB')
#        paths = set(p.iterdir())
#        expected = { P(BASE, 'linkB', q) for q in ['fileB', 'linkD'] }
#        self.assertEqual(paths, expected)
#
    def test_iterdir_nodir(self):
        # __iter__ on something that is not a directory
        p = self.cls(BASE, 'fileA')
        with self.assertRaises(OSError) as cm:
            next(p.iterdir())
        # ENOENT or EINVAL under Windows, ENOTDIR otherwise
        # (see issue #12802)
#        self.assertIn(cm.exception.errno, (errno.ENOTDIR,
        self.assertIn(cm.exception.args[0], (                                   ###
                                           errno.ENOENT, errno.EINVAL))

    def test_glob_common(self):
        def _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) for q in expected })
        P = self.cls
        p = P(BASE)
        it = p.glob("fileA")
#        self.assertIsInstance(it, collections.Iterator)
        _check(it, ["fileA"])
        _check(p.glob("fileB"), [])
        _check(p.glob("dir*/file*"), ["dirB/fileB", "dirC/fileC"])
        if symlink_skip_reason:
            _check(p.glob("*A"), ['dirA', 'fileA'])
        else:
            _check(p.glob("*A"), ['dirA', 'fileA', 'linkA'])
        if symlink_skip_reason:
            _check(p.glob("*B/*"), ['dirB/fileB'])
        else:
            _check(p.glob("*B/*"), ['dirB/fileB', 'dirB/linkD',
                                    'linkB/fileB', 'linkB/linkD'])
        if symlink_skip_reason:
            _check(p.glob("*/fileB"), ['dirB/fileB'])
        else:
            _check(p.glob("*/fileB"), ['dirB/fileB', 'linkB/fileB'])

    def test_rglob_common(self):
        def _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) for q in expected })
        P = self.cls
        p = P(BASE)
        it = p.rglob("fileA")
#        self.assertIsInstance(it, collections.Iterator)
        _check(it, ["fileA"])
        _check(p.rglob("fileB"), ["dirB/fileB"])
        _check(p.rglob("*/fileA"), [])
        if symlink_skip_reason:
            _check(p.rglob("*/fileB"), ["dirB/fileB"])
        else:
            _check(p.rglob("*/fileB"), ["dirB/fileB", "dirB/linkD/fileB",
                                        "linkB/fileB", "dirA/linkC/fileB"])
        _check(p.rglob("file*"), ["fileA", "dirB/fileB",
                                  "dirC/fileC", "dirC/dirD/fileD"])
        p = P(BASE, "dirC")
        _check(p.rglob("file*"), ["dirC/fileC", "dirC/dirD/fileD"])
        _check(p.rglob("*/*"), ["dirC/dirD/fileD"])

#    @with_symlinks
#    def test_rglob_symlink_loop(self):
#        # Don't get fooled by symlink loops (Issue #26012)
#        P = self.cls
#        p = P(BASE)
#        given = set(p.rglob('*'))
#        expect = {'brokenLink',
#                  'dirA', 'dirA/linkC',
#                  'dirB', 'dirB/fileB', 'dirB/linkD',
#                  'dirC', 'dirC/dirD', 'dirC/dirD/fileD', 'dirC/fileC',
#                  'dirE',
#                  'fileA',
#                  'linkA',
#                  'linkB',
#                  }
#        self.assertEqual(given, {p / x for x in expect})
#
    def test_glob_dotdot(self):
        # ".." is not special in globs
        P = self.cls
        p = P(BASE)
        self.assertEqual(set(p.glob("..")), { P(BASE, "..") })
        self.assertEqual(set(p.glob("dirA/../file*")), { P(BASE, "dirA/../fileA") })
        self.assertEqual(set(p.glob("../xyzzy")), set())

    def _check_resolve_relative(self, p, expected):
        q = p.resolve()
        self.assertEqual(q, expected)

    def _check_resolve_absolute(self, p, expected):
        q = p.resolve()
        self.assertEqual(q, expected)

#    @with_symlinks
#    def test_resolve_common(self):
#        P = self.cls
#        p = P(BASE, 'foo')
#        with self.assertRaises(OSError) as cm:
#            p.resolve()
#        self.assertEqual(cm.exception.errno, errno.ENOENT)
#        # These are all relative symlinks
#        p = P(BASE, 'dirB', 'fileB')
#        self._check_resolve_relative(p, p)
#        p = P(BASE, 'linkA')
#        self._check_resolve_relative(p, P(BASE, 'fileA'))
#        p = P(BASE, 'dirA', 'linkC', 'fileB')
#        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
#        p = P(BASE, 'dirB', 'linkD', 'fileB')
#        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
#        # Now create absolute symlinks
#        d = tempfile.mkdtemp(suffix='-dirD')
#        self.addCleanup(support.rmtree, d)
#        os.symlink(os.path.join(d), join('dirA', 'linkX'))
#        os.symlink(join('dirB'), os.path.join(d, 'linkY'))
#        p = P(BASE, 'dirA', 'linkX', 'linkY', 'fileB')
#        self._check_resolve_absolute(p, P(BASE, 'dirB', 'fileB'))
#
#    @with_symlinks
#    def test_resolve_dot(self):
#        # See https://bitbucket.org/pitrou/pathlib/issue/9/pathresolve-fails-on-complex-symlinks
#        p = self.cls(BASE)
#        self.dirlink('.', join('0'))
#        self.dirlink(os.path.join('0', '0'), join('1'))
#        self.dirlink(os.path.join('1', '1'), join('2'))
#        q = p / '2'
#        self.assertEqual(q.resolve(), p)
#
    def test_with(self):
        p = self.cls(BASE)
        it = p.iterdir()
        it2 = p.iterdir()
        next(it2)
        with p:
            pass
        # I/O operation on closed path
        self.assertRaises(ValueError, next, it)
        self.assertRaises(ValueError, next, it2)
        self.assertRaises(ValueError, p.open)
        self.assertRaises(ValueError, p.resolve)
        self.assertRaises(ValueError, p.absolute)
        self.assertRaises(ValueError, p.__enter__)

#    def test_chmod(self):
#        p = self.cls(BASE) / 'fileA'
#        mode = p.stat().st_mode
#        # Clear writable bit
#        new_mode = mode & ~0o222
#        p.chmod(new_mode)
#        self.assertEqual(p.stat().st_mode, new_mode)
#        # Set writable bit
#        new_mode = mode | 0o222
#        p.chmod(new_mode)
#        self.assertEqual(p.stat().st_mode, new_mode)
#
#    # XXX also need a test for lchmod
#
    def test_stat(self):
        p = self.cls(BASE) / 'fileA'
        st = p.stat()
        self.assertEqual(p.stat(), st)
#        # Change file mode by flipping write bit
#        p.chmod(st.st_mode ^ 0o222)
#        self.addCleanup(p.chmod, st.st_mode)
#        self.assertNotEqual(p.stat(), st)

#    @with_symlinks
#    def test_lstat(self):
#        p = self.cls(BASE)/ 'linkA'
#        st = p.stat()
#        self.assertNotEqual(st, p.lstat())
#
#    def test_lstat_nosymlink(self):
#        p = self.cls(BASE) / 'fileA'
#        st = p.stat()
#        self.assertEqual(st, p.lstat())
#
#    @unittest.skipUnless(pwd, "the pwd module is needed for this test")
#    def test_owner(self):
#        p = self.cls(BASE) / 'fileA'
#        uid = p.stat().st_uid
#        try:
#            name = pwd.getpwuid(uid).pw_name
#        except KeyError:
#            self.skipTest(
#                "user %d doesn't have an entry in the system database" % uid)
#        self.assertEqual(name, p.owner())
#
#    @unittest.skipUnless(grp, "the grp module is needed for this test")
#    def test_group(self):
#        p = self.cls(BASE) / 'fileA'
#        gid = p.stat().st_gid
#        try:
#            name = grp.getgrgid(gid).gr_name
#        except KeyError:
#            self.skipTest(
#                "group %d doesn't have an entry in the system database" % gid)
#        self.assertEqual(name, p.group())
#
    def test_unlink(self):
        p = self.cls(BASE) / 'fileA'
        p.unlink()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    def test_rmdir(self):
        p = self.cls(BASE) / 'dirA'
        for q in p.iterdir():
            q.unlink()
        p.rmdir()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    def test_rename(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # Renaming to another path
        q = P / 'dirA' / 'fileAA'
        p.rename(q)
        self.assertEqual(q.stat().st_size, size)
        self.assertFileNotFound(p.stat)
        # Renaming to a str of a relative path
        r = rel_join('fileAAA')
        q.rename(r)
        self.assertEqual(os.stat(r).st_size, size)
        self.assertFileNotFound(q.stat)

#    def test_replace(self):
#        P = self.cls(BASE)
#        p = P / 'fileA'
#        size = p.stat().st_size
#        # Replacing a non-existing path
#        q = P / 'dirA' / 'fileAA'
#        p.replace(q)
#        self.assertEqual(q.stat().st_size, size)
#        self.assertFileNotFound(p.stat)
#        # Replacing another (existing) path
#        r = rel_join('dirB', 'fileB')
#        q.replace(r)
#        self.assertEqual(os.stat(r).st_size, size)
#        self.assertFileNotFound(q.stat)
#
    def test_touch_common(self):
        P = self.cls(BASE)
        p = P / 'newfileA'
        self.assertFalse(p.exists())
        p.touch()
        self.assertTrue(p.exists())
#        st = p.stat()
#        old_mtime = st.st_mtime
#        old_mtime_ns = st.st_mtime_ns
#        # Rewind the mtime sufficiently far in the past to work around
#        # filesystem-specific timestamp granularity.
#        os.utime(str(p), (old_mtime - 10, old_mtime - 10))
#        # The file mtime should be refreshed by calling touch() again
#        p.touch()
#        st = p.stat()
#        self.assertGreaterEqual(st.st_mtime_ns, old_mtime_ns)
#        self.assertGreaterEqual(st.st_mtime, old_mtime)
#        # Now with exist_ok=False
#        p = P / 'newfileB'
#        self.assertFalse(p.exists())
#        p.touch(mode=0o700, exist_ok=False)
#        self.assertTrue(p.exists())
#        self.assertRaises(OSError, p.touch, exist_ok=False)

    def test_touch_nochange(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        p.touch()
        with p.open('rb') as f:
            self.assertEqual(f.read().strip(), b"this is file A")

    def test_mkdir(self):
        P = self.cls(BASE)
        p = P / 'newdirA'
        self.assertFalse(p.exists())
        p.mkdir()
        self.assertTrue(p.exists())
        self.assertTrue(p.is_dir())
        with self.assertRaises(OSError) as cm:
            p.mkdir()
#        self.assertEqual(cm.exception.errno, errno.EEXIST)
        self.assertEqual(cm.exception.args[0], errno.EEXIST)                    ###

    def test_mkdir_parents(self):
        # Creating a chain of directories
        p = self.cls(BASE, 'newdirB', 'newdirC')
        self.assertFalse(p.exists())
        with self.assertRaises(OSError) as cm:
            p.mkdir()
#        self.assertEqual(cm.exception.errno, errno.ENOENT)
        self.assertEqual(cm.exception.args[0], errno.ENOENT)                    ###
        p.mkdir(parents=True)
        self.assertTrue(p.exists())
        self.assertTrue(p.is_dir())
        with self.assertRaises(OSError) as cm:
            p.mkdir(parents=True)
#        self.assertEqual(cm.exception.errno, errno.EEXIST)
        self.assertEqual(cm.exception.args[0], errno.EEXIST)                    ###
        # test `mode` arg
        mode = stat.S_IMODE(p.stat().st_mode) # default mode
        p = self.cls(BASE, 'newdirD', 'newdirE')
        p.mkdir(0o555, parents=True)
        self.assertTrue(p.exists())
        self.assertTrue(p.is_dir())
        if os.name != 'nt':
            # the directory's permissions follow the mode argument
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o7555 & mode)
        # the parent's permissions follow the default process settings
        self.assertEqual(stat.S_IMODE(p.parent.stat().st_mode), mode)

#    @with_symlinks
#    def test_symlink_to(self):
#        P = self.cls(BASE)
#        target = P / 'fileA'
#        # Symlinking a path target
#        link = P / 'dirA' / 'linkAA'
#        link.symlink_to(target)
#        self.assertEqual(link.stat(), target.stat())
#        self.assertNotEqual(link.lstat(), target.stat())
#        # Symlinking a str target
#        link = P / 'dirA' / 'linkAAA'
#        link.symlink_to(str(target))
#        self.assertEqual(link.stat(), target.stat())
#        self.assertNotEqual(link.lstat(), target.stat())
#        self.assertFalse(link.is_dir())
#        # Symlinking to a directory
#        target = P / 'dirB'
#        link = P / 'dirA' / 'linkAAAA'
#        link.symlink_to(target, target_is_directory=True)
#        self.assertEqual(link.stat(), target.stat())
#        self.assertNotEqual(link.lstat(), target.stat())
#        self.assertTrue(link.is_dir())
#        self.assertTrue(list(link.iterdir()))
#
    def test_is_dir(self):
        P = self.cls(BASE)
        self.assertTrue((P / 'dirA').is_dir())
        self.assertFalse((P / 'fileA').is_dir())
        self.assertFalse((P / 'non-existing').is_dir())
        self.assertFalse((P / 'fileA' / 'bah').is_dir())
#        if not symlink_skip_reason:
#            self.assertFalse((P / 'linkA').is_dir())
#            self.assertTrue((P / 'linkB').is_dir())
#            self.assertFalse((P/ 'brokenLink').is_dir())

    def test_is_file(self):
        P = self.cls(BASE)
        self.assertTrue((P / 'fileA').is_file())
        self.assertFalse((P / 'dirA').is_file())
        self.assertFalse((P / 'non-existing').is_file())
        self.assertFalse((P / 'fileA' / 'bah').is_file())
#        if not symlink_skip_reason:
#            self.assertTrue((P / 'linkA').is_file())
#            self.assertFalse((P / 'linkB').is_file())
#            self.assertFalse((P/ 'brokenLink').is_file())

#    def test_is_symlink(self):
#        P = self.cls(BASE)
#        self.assertFalse((P / 'fileA').is_symlink())
#        self.assertFalse((P / 'dirA').is_symlink())
#        self.assertFalse((P / 'non-existing').is_symlink())
#        self.assertFalse((P / 'fileA' / 'bah').is_symlink())
#        if not symlink_skip_reason:
#            self.assertTrue((P / 'linkA').is_symlink())
#            self.assertTrue((P / 'linkB').is_symlink())
#            self.assertTrue((P/ 'brokenLink').is_symlink())
#
    def test_is_fifo_false(self):
        P = self.cls(BASE)
        self.assertFalse((P / 'fileA').is_fifo())
        self.assertFalse((P / 'dirA').is_fifo())
        self.assertFalse((P / 'non-existing').is_fifo())
        self.assertFalse((P / 'fileA' / 'bah').is_fifo())

#    @unittest.skipUnless(hasattr(os, "mkfifo"), "os.mkfifo() required")
#    def test_is_fifo_true(self):
#        P = self.cls(BASE, 'myfifo')
#        os.mkfifo(str(P))
#        self.assertTrue(P.is_fifo())
#        self.assertFalse(P.is_socket())
#        self.assertFalse(P.is_file())
#
    def test_is_socket_false(self):
        P = self.cls(BASE)
        self.assertFalse((P / 'fileA').is_socket())
        self.assertFalse((P / 'dirA').is_socket())
        self.assertFalse((P / 'non-existing').is_socket())
        self.assertFalse((P / 'fileA' / 'bah').is_socket())

#    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
#    def test_is_socket_true(self):
#        P = self.cls(BASE, 'mysock')
#        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#        self.addCleanup(sock.close)
#        try:
#            sock.bind(str(P))
#        except OSError as e:
#            if "AF_UNIX path too long" in str(e):
#                self.skipTest("cannot bind Unix socket: " + str(e))
#        self.assertTrue(P.is_socket())
#        self.assertFalse(P.is_fifo())
#        self.assertFalse(P.is_file())
#
    def test_is_block_device_false(self):
        P = self.cls(BASE)
        self.assertFalse((P / 'fileA').is_block_device())
        self.assertFalse((P / 'dirA').is_block_device())
        self.assertFalse((P / 'non-existing').is_block_device())
        self.assertFalse((P / 'fileA' / 'bah').is_block_device())

    def test_is_char_device_false(self):
        P = self.cls(BASE)
        self.assertFalse((P / 'fileA').is_char_device())
        self.assertFalse((P / 'dirA').is_char_device())
        self.assertFalse((P / 'non-existing').is_char_device())
        self.assertFalse((P / 'fileA' / 'bah').is_char_device())

#    def test_is_char_device_true(self):
#        # Under Unix, /dev/null should generally be a char device
#        P = self.cls('/dev/null')
#        if not P.exists():
#            self.skipTest("/dev/null required")
#        self.assertTrue(P.is_char_device())
#        self.assertFalse(P.is_block_device())
#        self.assertFalse(P.is_file())
#
#    def test_pickling_common(self):
#        p = self.cls(BASE, 'fileA')
#        for proto in range(0, pickle.HIGHEST_PROTOCOL + 1):
#            dumped = pickle.dumps(p, proto)
#            pp = pickle.loads(dumped)
#            self.assertEqual(pp.stat(), p.stat())
#
#    def test_parts_interning(self):
#        P = self.cls
#        p = P('/usr/bin/foo')
#        q = P('/usr/local/bin')
#        # 'usr'
#        self.assertIs(p.parts[1], q.parts[1])
#        # 'bin'
#        self.assertIs(p.parts[2], q.parts[3])
#
#    def _check_complex_symlinks(self, link0_target):
#        # Test solving a non-looping chain of symlinks (issue #19887)
#        P = self.cls(BASE)
#        self.dirlink(os.path.join('link0', 'link0'), join('link1'))
#        self.dirlink(os.path.join('link1', 'link1'), join('link2'))
#        self.dirlink(os.path.join('link2', 'link2'), join('link3'))
#        self.dirlink(link0_target, join('link0'))
#
#        # Resolve absolute paths
#        p = (P / 'link0').resolve()
#        self.assertEqual(p, P)
#        self.assertEqual(str(p), BASE)
#        p = (P / 'link1').resolve()
#        self.assertEqual(p, P)
#        self.assertEqual(str(p), BASE)
#        p = (P / 'link2').resolve()
#        self.assertEqual(p, P)
#        self.assertEqual(str(p), BASE)
#        p = (P / 'link3').resolve()
#        self.assertEqual(p, P)
#        self.assertEqual(str(p), BASE)
#
#        # Resolve relative paths
#        old_path = os.getcwd()
#        os.chdir(BASE)
#        try:
#            p = self.cls('link0').resolve()
#            self.assertEqual(p, P)
#            self.assertEqual(str(p), BASE)
#            p = self.cls('link1').resolve()
#            self.assertEqual(p, P)
#            self.assertEqual(str(p), BASE)
#            p = self.cls('link2').resolve()
#            self.assertEqual(p, P)
#            self.assertEqual(str(p), BASE)
#            p = self.cls('link3').resolve()
#            self.assertEqual(p, P)
#            self.assertEqual(str(p), BASE)
#        finally:
#            os.chdir(old_path)
#
#    @with_symlinks
#    def test_complex_symlinks_absolute(self):
#        self._check_complex_symlinks(BASE)
#
#    @with_symlinks
#    def test_complex_symlinks_relative(self):
#        self._check_complex_symlinks('.')
#
#    @with_symlinks
#    def test_complex_symlinks_relative_dot_dot(self):
#        self._check_complex_symlinks(os.path.join('dirA', '..'))


class PathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.Path

    def test_concrete_class(self):
        p = self.cls('a')
        self.assertIs(type(p),
            pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath)

#    def test_unsupported_flavour(self):
#        if os.name == 'nt':
#            self.assertRaises(NotImplementedError, pathlib.PosixPath)
#        else:
#            self.assertRaises(NotImplementedError, pathlib.WindowsPath)
#

#@only_posix
class PosixPathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.PosixPath

#    def _check_symlink_loop(self, *args):
#        path = self.cls(*args)
#        with self.assertRaises(RuntimeError):
#            print(path.resolve())
#
#    def test_open_mode(self):
#        old_mask = os.umask(0)
#        self.addCleanup(os.umask, old_mask)
#        p = self.cls(BASE)
#        with (p / 'new_file').open('wb'):
#            pass
#        st = os.stat(join('new_file'))
#        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
#        os.umask(0o022)
#        with (p / 'other_new_file').open('wb'):
#            pass
#        st = os.stat(join('other_new_file'))
#        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)
#
#    def test_touch_mode(self):
#        old_mask = os.umask(0)
#        self.addCleanup(os.umask, old_mask)
#        p = self.cls(BASE)
#        (p / 'new_file').touch()
#        st = os.stat(join('new_file'))
#        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
#        os.umask(0o022)
#        (p / 'other_new_file').touch()
#        st = os.stat(join('other_new_file'))
#        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)
#        (p / 'masked_new_file').touch(mode=0o750)
#        st = os.stat(join('masked_new_file'))
#        self.assertEqual(stat.S_IMODE(st.st_mode), 0o750)
#
#    @with_symlinks
#    def test_resolve_loop(self):
#        # Loop detection for broken symlinks under POSIX
#        P = self.cls
#        # Loops with relative symlinks
#        os.symlink('linkX/inside', join('linkX'))
#        self._check_symlink_loop(BASE, 'linkX')
#        os.symlink('linkY', join('linkY'))
#        self._check_symlink_loop(BASE, 'linkY')
#        os.symlink('linkZ/../linkZ', join('linkZ'))
#        self._check_symlink_loop(BASE, 'linkZ')
#        # Loops with absolute symlinks
#        os.symlink(join('linkU/inside'), join('linkU'))
#        self._check_symlink_loop(BASE, 'linkU')
#        os.symlink(join('linkV'), join('linkV'))
#        self._check_symlink_loop(BASE, 'linkV')
#        os.symlink(join('linkW/../linkW'), join('linkW'))
#        self._check_symlink_loop(BASE, 'linkW')
#
    def test_glob(self):
        P = self.cls
        p = P(BASE)
        given = set(p.glob("FILEa"))
#        expect = set() if not support.fs_is_case_insensitive(BASE) else given
#        self.assertEqual(given, expect)
        self.assertEqual(set(p.glob("FILEa*")), set())

    def test_rglob(self):
        P = self.cls
        p = P(BASE, "dirC")
        given = set(p.rglob("FILEd"))
#        expect = set() if not support.fs_is_case_insensitive(BASE) else given
#        self.assertEqual(given, expect)
        self.assertEqual(set(p.rglob("FILEd*")), set())


#@only_nt
#class WindowsPathTest(_BasePathTest, unittest.TestCase):
#    cls = pathlib.WindowsPath
#
#    def test_glob(self):
#        P = self.cls
#        p = P(BASE)
#        self.assertEqual(set(p.glob("FILEa")), { P(BASE, "fileA") })
#
#    def test_rglob(self):
#        P = self.cls
#        p = P(BASE, "dirC")
#        self.assertEqual(set(p.rglob("FILEd")), { P(BASE, "dirC/dirD/fileD") })
#
#
#if __name__ == "__main__":
#    unittest.main()
