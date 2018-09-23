"Test posix functions"

from test import support

# Skip these tests if there is no posix module.
posix = support.import_module('posix')

import errno
import sys
import time
import os
import shutil
import stat
import tempfile
import unittest

_DUMMY_SYMLINK = os.path.join(tempfile.gettempdir(),
                              support.TESTFN + '-dummy-symlink')

class PosixTester(unittest.TestCase):

    def setUp(self):
        # create empty file
        fp = open(support.TESTFN, 'w+')
        fp.close()
        self.teardown_files = [ support.TESTFN ]

    def tearDown(self):
        for teardown_file in self.teardown_files:
            support.unlink(teardown_file)

    def testNoArgFunctions(self):
        # test posix functions which take no arguments and have
        # no side-effects which we need to cleanup (e.g., fork, wait, abort)
        NO_ARG_FUNCTIONS = [ "ctermid", "getcwd", "getcwdb", "uname",
                             "times", "getloadavg",
                             "getegid", "geteuid", "getgid", "getgroups",
                             "getpid", "getpgrp", "getppid", "getuid", "sync",
                           ]

        for name in NO_ARG_FUNCTIONS:
            posix_func = getattr(posix, name, None)
            if posix_func is not None:
                posix_func()
                self.assertRaises(TypeError, posix_func, 1)


    @unittest.skipUnless(hasattr(posix, 'statvfs'),
                         'test needs posix.statvfs()')
    def test_statvfs(self):
        self.assertTrue(posix.statvfs(os.curdir))


    @unittest.skipUnless(hasattr(posix, 'truncate'), "test needs posix.truncate()")
    def test_truncate(self):
        with open(support.TESTFN, 'w') as fp:
            fp.write('test')
            fp.flush()
        posix.truncate(support.TESTFN, 0)


    @unittest.skipUnless(hasattr(posix, 'stat'),
                         'test needs posix.stat()')
    def test_stat(self):
        self.assertTrue(posix.stat(support.TESTFN))
        self.assertTrue(posix.stat(os.fsencode(support.TESTFN)))

        self.assertRaises(TypeError,                                            ###
                posix.stat, None)
        self.assertRaises(TypeError,                                            ###
                posix.stat, list(support.TESTFN))
        self.assertRaises(TypeError,                                            ###
                posix.stat, list(os.fsencode(support.TESTFN)))


    @unittest.skipUnless(hasattr(posix, 'chdir'), 'test needs posix.chdir()')
    def test_chdir(self):
        posix.chdir(os.curdir)
        self.assertRaises(OSError, posix.chdir, support.TESTFN)

    def test_listdir(self):
        self.assertTrue(support.TESTFN in posix.listdir(os.curdir))

    def test_listdir_default(self):
        # When listdir is called without argument,
        # it's the same as listdir(os.curdir).
        self.assertTrue(support.TESTFN in posix.listdir())

    @unittest.expectedFailure                                                   ###
    def test_listdir_bytes(self):
        # When listdir is called with a bytes object,
        # the returned strings are of type bytes.
        self.assertTrue(os.fsencode(support.TESTFN) in posix.listdir(b'.'))


    @unittest.skipUnless(hasattr(posix, 'getcwd'), 'test needs posix.getcwd()')
    def test_getcwd_long_pathnames(self):
        dirname = 'getcwd-test-directory-0123456789abcdef-01234567890abcdef'
        curdir = os.getcwd()
        base_path = os.path.abspath(support.TESTFN) + '.getcwd'

        try:
            os.mkdir(base_path)
            os.chdir(base_path)
        except:
            #  Just returning nothing instead of the SkipTest exception, because
            #  the test results in Error in that case.  Is that ok?
            #  raise unittest.SkipTest("cannot create directory for testing")
            return

            def _create_and_do_getcwd(dirname, current_path_length = 0):
                try:
                    os.mkdir(dirname)
                except:
                    raise unittest.SkipTest("mkdir cannot create directory sufficiently deep for getcwd test")

                os.chdir(dirname)
                try:
                    os.getcwd()
                    if current_path_length < 1027:
                        _create_and_do_getcwd(dirname, current_path_length + len(dirname) + 1)
                finally:
                    os.chdir('..')
                    os.rmdir(dirname)

            _create_and_do_getcwd(dirname)

        finally:
            os.chdir(curdir)
            support.rmtree(base_path)

