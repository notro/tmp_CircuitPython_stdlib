#! /usr/bin/env python3

# This is a stripped down version used as a backend for running a modified      ###
# regrtest from the host                                                        ###
                                                                                ###
"""
Script to run Python regression tests.

Run this script with -h or --help for documentation.
"""

import importlib
import io
import os
import sys
import tempfile
import time
import traceback
import unittest


# Some times __path__ and __file__ are not absolute (e.g. while running from
# Lib/) and, if we change the CWD to run the tests in a temporary dir, some
# imports might fail.  This affects only the modules imported before os.chdir().
# These modules are searched first in sys.path[0] (so '' -- the CWD) and if
# they are found in the CWD their __file__ and __path__ will be relative (this
# happens before the chdir).  All the modules imported after the chdir, are
# not found in the CWD, and since the other paths in sys.path[1:] are absolute
# (site.py absolutize them), the __file__ and __path__ will be absolute too.
# Therefore it is necessary to absolutize manually the __file__ and __path__ of
# the packages to prevent later imports to fail when the CWD is different.
for module in sys.modules.values():
    if hasattr(module, '__path__'):
        module.__path__ = [os.path.abspath(path) for path in module.__path__]
    if hasattr(module, '__file__'):
        module.__file__ = os.path.abspath(module.__file__)



# Test result constants.
PASSED = 1
FAILED = 0
ENV_CHANGED = -1
SKIPPED = -2
RESOURCE_DENIED = -3
INTERRUPTED = -4
CHILD_ERROR = -5   # error in a child process

from test import support

RESOURCE_NAMES = ('audio', 'curses', 'largefile', 'network',
                  'decimal', 'cpu', 'subprocess', 'urlfetch', 'gui')

TEMPDIR = tempfile.gettempdir()                                                 ###
TEMPDIR = os.path.abspath(TEMPDIR)


def findtests(testdir=None, stdtests=None, nottests=None):                      ### All parameters are filled by the host
    """Return a list of all applicable test modules."""
    testdir = findtestdir(testdir)
    names = os.listdir(testdir)
    tests = []
    others = set(stdtests) | nottests
    for name in names:
        mod, ext = os.path.splitext(name)
        if mod[:5] == "test_" and ext in (".mpy", ".py", "") and mod not in others:  ###
            tests.append(mod)
    return stdtests + sorted(tests)


def runtest(test, verbose, quiet,
            huntrleaks=False, use_resources=None,
            output_on_failure=False, failfast=False, match_tests=None,
            timeout=None):
    """Run a single test.

    test -- the name of the test
    verbose -- if true, print more messages
    quiet -- if true, don't print 'skipped' messages (probably redundant)
    huntrleaks -- run multiple times to test for leaks; requires a debug
                  build; a triple corresponding to -R's three arguments
    use_resources -- list of extra resources to use
    output_on_failure -- if true, display test output on failure
    timeout -- dump the traceback and exit if a test takes more than
               timeout seconds
    failfast, match_tests -- See regrtest command-line flags for these.

    Returns the tuple result, test_time, where result is one of the constants:
        INTERRUPTED      KeyboardInterrupt when run under -j
        RESOURCE_DENIED  test skipped because resource denied
        SKIPPED          test skipped for some other reason
        ENV_CHANGED      test failed because it changed the execution environment
        FAILED           test failed
        PASSED           test passed
    """

    if use_resources is not None:
        support.use_resources = use_resources
    use_timeout = (timeout is not None)
    if use_timeout:
        faulthandler.dump_traceback_later(timeout, exit=True)
    try:
        support.match_tests = match_tests
        if failfast:
            support.failfast = True
        if output_on_failure:
            raise NotImplementedError("stdout can't be redirected")             ###
        else:
            support.verbose = verbose  # Tell tests to be moderately quiet
            result = runtest_inner(test, verbose, quiet, huntrleaks,
                                   display_failure=not verbose)
        return result
    finally:
        cleanup_test_droppings(test, verbose)

# Unit tests are supposed to leave the execution environment unchanged
# once they complete.  But sometimes tests have bugs, especially when
# tests fail, and the changes to environment go on to mess up other
# tests.  This can cause issues with buildbot stability, since tests
# are run in random order and so problems may appear to come and go.
# There are a few things we can save and restore to mitigate this, and
# the following context manager handles this task.

class saved_test_environment:
    """Save bits of the test environment and restore them at block exit.

        with saved_test_environment(testname, verbose, quiet):
            #stuff

    Unless quiet is True, a warning is printed to stderr if any of
    the saved items was changed by the test.  The attribute 'changed'
    is initially False, but is set to True if a change is detected.

    If verbose is more than 1, the before and after state of changed
    items is also printed.
    """

    changed = False

    def __init__(self, testname, verbose=0, quiet=False):
        self.testname = testname
        self.verbose = verbose
        self.quiet = quiet

    # To add things to save and restore, add a name XXX to the resources list
    # and add corresponding get_XXX/restore_XXX functions.  get_XXX should
    # return the value to be saved and compared against a second call to the
    # get function when test execution completes.  restore_XXX should accept
    # the saved value and restore the resource using it.  It will be called if
    # and only if a change in the value is detected.
    #
    # Note: XXX will have any '.' replaced with '_' characters when determining
    # the corresponding method names.

    resources = ('cwd',                                                         ###
                 'os.environ',                                                  ###
                 'files',                                                       ###
                )                                                               ###

    def get_cwd(self):
        return os.getcwd()
    def restore_cwd(self, saved_cwd):
        os.chdir(saved_cwd)

    def get_os_environ(self):
        return id(os.environ), os.environ, dict(os.environ)
    def restore_os_environ(self, saved_environ):
        os.environ = saved_environ[1]
        os.environ.clear()
        os.environ.update(saved_environ[2])

    def get_files(self):
        return sorted(fn + ('/' if os.path.isdir(fn) else '')
                      for fn in os.listdir())
    def restore_files(self, saved_value):
        fn = support.TESTFN
        if fn not in saved_value and (fn + '/') not in saved_value:
            if os.path.isfile(fn):
                support.unlink(fn)
            elif os.path.isdir(fn):
                support.rmtree(fn)

    def resource_info(self):
        for name in self.resources:
            method_suffix = name.replace('.', '_')
            get_name = 'get_' + method_suffix
            restore_name = 'restore_' + method_suffix
            yield name, getattr(self, get_name), getattr(self, restore_name)

    def __enter__(self):
        self.saved_values = dict((name, get()) for name, get, restore
                                                   in self.resource_info())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        saved_values = self.saved_values
        del self.saved_values
        for name, get, restore in self.resource_info():
            current = get()
            original = saved_values.pop(name)
            # Check for changes to the resource's value
            if current != original:
                self.changed = True
                restore(original)
                if not self.quiet:
                    print("Warning -- {} was modified by {}".format(
                                                 name, self.testname),
                                                 file=sys.stderr)
                    if self.verbose > 1:
                        print("  Before: {}\n  After:  {} ".format(
                                                  original, current),
                                                  file=sys.stderr)
        return False


def runtest_inner(test, verbose, quiet,
                  huntrleaks=False, display_failure=True):
    support.unload(test)

    test_time = 0.0
    try:
        if test.startswith('test.'):
            abstest = test
        else:
            # Always import it from the test package
            abstest = 'test.' + test
        with saved_test_environment(test, verbose, quiet) as environment:
            import gc                                                           ###
            if not quiet:                                                       ###
                before = gc.mem_free()                                          ###
            start_time = time.time()
            the_module = importlib.import_module(abstest)
            if not quiet:                                                       ###
                after = gc.mem_free()                                           ###
                print('Loading module mem_free: before=%.1fkB, after=%.1fkB' % (before / 1024, after / 1024))  ###
            # If the test has a test_main, that will run the appropriate
            # tests.  If not, use normal unittest test loading.
            test_runner = getattr(the_module, "test_main", None)
            if test_runner is None:
                def test_runner():
                    loader = unittest.TestLoader()
                    tests = loader.loadTestsFromModule(the_module)
                    support.run_unittest(tests)
            test_runner()
            test_time = time.time() - start_time
    except support.ResourceDenied as msg:
        if not quiet:
            print(test, "skipped --", msg)
        return RESOURCE_DENIED, test_time
    except unittest.SkipTest as msg:
        if not quiet:
            print(test, "skipped --", msg)
        return SKIPPED, test_time
    except KeyboardInterrupt:
        raise
    except support.TestFailed as msg:
        if display_failure:
            print("test", test, "failed --", msg, file=sys.stderr)
        else:
            print("test", test, "failed", file=sys.stderr)
        return FAILED, test_time
    except MemoryError as msg:                                                  ###
        if not quiet:                                                           ###
            print(test, "Out of memory --", msg, file=sys.stderr)               ###
            return FAILED, test_time                                            ###
        else:                                                                   ###
            raise                                                               ### Let host print message since stdout is not displayed
    except BaseException as msg:                                                ### Why doesn't traceback.format_exc() work?
        print("test", test, "crashed --", msg, file=sys.stderr)
        return FAILED, test_time
    else:
        if environment.changed:
            return ENV_CHANGED, test_time
        return PASSED, test_time

def cleanup_test_droppings(testname, verbose):
    import shutil
    import stat
    import gc

    # First kill any dangling references to open files etc.
    # This can also issue some ResourceWarnings which would otherwise get
    # triggered during the following test run, and possibly produce failures.
    gc.collect()

    # Try to clean up junk commonly left behind.  While tests shouldn't leave
    # any files or directories behind, when a test fails that can be tedious
    # for it to arrange.  The consequences can be especially nasty on Windows,
    # since if a test leaves a file open, it cannot be deleted by name (while
    # there's nothing we can do about that here either, we can display the
    # name of the offending test, which is a real help).
    for name in (support.TESTFN,
                 "db_home",
                ):
        if not os.path.exists(name):
            continue

        if os.path.isdir(name):
            kind, nuker = "directory", shutil.rmtree
        elif os.path.isfile(name):
            kind, nuker = "file", os.unlink
        else:
            raise SystemError("os.path says %r exists but is neither "
                              "directory nor file" % name)

        if verbose:
            print("%r left behind %s %r" % (testname, kind, name))
        try:
            # if we have chmod, fix possible permissions problems
            # that might prevent cleanup
            if (hasattr(os, 'chmod')):
                os.chmod(name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            nuker(name)
        except Exception as msg:
            print(("%r left behind %s %r and it couldn't be "
                "removed: %s" % (testname, kind, name, msg)), file=sys.stderr)


def findtestdir(path=None):
    return path or os.path.dirname(__file__) or os.curdir

