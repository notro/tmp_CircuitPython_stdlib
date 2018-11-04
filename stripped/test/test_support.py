import shutil
import sys
import os
import unittest
import tempfile
import errno
from test import support

TESTFN = support.TESTFN
TESTDIRN = os.path.basename(tempfile.mkdtemp(dir='.'))
FileExistsError = OSError                                                       ### Missing
FileNotFoundError = OSError                                                     ###


class TestSupport(unittest.TestCase):
    def setUp(self):
        support.unlink(TESTFN)
        support.rmtree(TESTDIRN)
    tearDown = setUp

    def test_unlink(self):
        with open(TESTFN, "w") as f:
            pass
        support.unlink(TESTFN)
        self.assertFalse(os.path.exists(TESTFN))
        support.unlink(TESTFN)

    def test_rmtree(self):
        os.mkdir(TESTDIRN)
        os.mkdir(os.path.join(TESTDIRN, TESTDIRN))
        support.rmtree(TESTDIRN)
        self.assertFalse(os.path.exists(TESTDIRN))
        support.rmtree(TESTDIRN)

    # Tests for temp_dir()

    def test_temp_dir(self):
        """Test that temp_dir() creates and destroys its directory."""
        parent_dir = tempfile.mkdtemp()
        parent_dir = os.path.realpath(parent_dir)

        try:
            path = os.path.join(parent_dir, 'temp')
            self.assertFalse(os.path.isdir(path))
            with support.temp_dir(path) as temp_path:
                self.assertEqual(temp_path, path)
                self.assertTrue(os.path.isdir(path))
            self.assertFalse(os.path.isdir(path))
        finally:
            support.rmtree(parent_dir)

    def test_temp_dir__path_none(self):
        """Test passing no path."""
        with support.temp_dir() as temp_path:
            self.assertTrue(os.path.isdir(temp_path))
        self.assertFalse(os.path.isdir(temp_path))

    def test_temp_dir__existing_dir__quiet_default(self):
        """Test passing a directory that already exists."""
        def call_temp_dir(path):
            with support.temp_dir(path) as temp_path:
                raise Exception("should not get here")

        path = tempfile.mkdtemp()
        path = os.path.realpath(path)
        try:
            self.assertTrue(os.path.isdir(path))
            self.assertRaises(FileExistsError, call_temp_dir, path)
            # Make sure temp_dir did not delete the original directory.
            self.assertTrue(os.path.isdir(path))
        finally:
            shutil.rmtree(path)

    def test_temp_dir__existing_dir__quiet_true(self):
        """Test passing a directory that already exists with quiet=True."""
        path = tempfile.mkdtemp()
        path = os.path.realpath(path)

        try:
            with self.assertRaises(NameError):                                  ### No warnings module yet
                with support.temp_dir(path, quiet=True) as temp_path:
                    self.assertEqual(path, temp_path)
            # Make sure temp_dir did not delete the original directory.
            self.assertTrue(os.path.isdir(path))
        finally:
            shutil.rmtree(path)


    # Tests for change_cwd()

    def test_change_cwd(self):
        original_cwd = os.getcwd()

        with support.temp_dir() as temp_path:
            with support.change_cwd(temp_path) as new_cwd:
                self.assertEqual(new_cwd, temp_path)
                self.assertEqual(os.getcwd(), new_cwd)

        self.assertEqual(os.getcwd(), original_cwd)

    def test_change_cwd__non_existent_dir(self):
        """Test passing a non-existent directory."""
        original_cwd = os.getcwd()

        def call_change_cwd(path):
            with support.change_cwd(path) as new_cwd:
                raise Exception("should not get here")

        with support.temp_dir() as parent_dir:
            non_existent_dir = os.path.join(parent_dir, 'does_not_exist')
            self.assertRaises(FileNotFoundError, call_change_cwd,
                              non_existent_dir)

        self.assertEqual(os.getcwd(), original_cwd)

    def test_change_cwd__non_existent_dir__quiet_true(self):
        """Test passing a non-existent directory with quiet=True."""
        original_cwd = os.getcwd()

        with support.temp_dir() as parent_dir:
            bad_dir = os.path.join(parent_dir, 'does_not_exist')
            with self.assertRaises(NameError):                                  ### No warnings module yet
                with support.change_cwd(bad_dir, quiet=True) as new_cwd:
                    self.assertEqual(new_cwd, original_cwd)
                    self.assertEqual(os.getcwd(), new_cwd)

    # Tests for change_cwd()

    # Tests for temp_cwd()

    def test_temp_cwd(self):
        here = os.getcwd()
        with support.temp_cwd(name=TESTFN):
            self.assertEqual(os.path.basename(os.getcwd()), TESTFN)
        self.assertFalse(os.path.exists(TESTFN))


    def test_temp_cwd__name_none(self):
        """Test passing None to temp_cwd()."""
        original_cwd = os.getcwd()
        with support.temp_cwd(name=None) as new_cwd:
            self.assertNotEqual(new_cwd, original_cwd)
            self.assertTrue(os.path.isdir(new_cwd))
            self.assertEqual(os.getcwd(), new_cwd)
        self.assertEqual(os.getcwd(), original_cwd)

    def test_swap_attr(self):
        class Obj:
            x = 1
        obj = Obj()
        with support.swap_attr(obj, "x", 5):
            self.assertEqual(obj.x, 5)
        self.assertEqual(obj.x, 1)

    def test_swap_item(self):
        D = {"item":1}
        with support.swap_item(D, "item", 5):
            self.assertEqual(D["item"], 5)
        self.assertEqual(D["item"], 1)

    # XXX -follows a list of untested API
    # make_legacy_pyc
    # is_resource_enabled
    # requires
    # fcmp
    # umaks
    # findfile
    # check_warnings
    # EnvironmentVarGuard
    # TransientResource
    # transient_internet
    # run_with_locale
    # set_memlimit
    # bigmemtest
    # precisionbigmemtest
    # bigaddrspacetest
    # requires_resource
    # run_doctest
    # threading_cleanup
    # reap_threads
    # reap_children
    # strip_python_stderr
    # args_from_interpreter_flags
    # can_symlink
    # skip_unless_symlink
    # SuppressCrashReport


