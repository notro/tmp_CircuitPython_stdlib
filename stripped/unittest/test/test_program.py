import io

import os
import sys
from test import support
import unittest
import unittest.test


class Test_TestProgram(unittest.TestCase):

    def test_discovery_from_dotted_path(self):
        loader = unittest.TestLoader()

        tests = [self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))

        self.wasRun = False
        def _find_tests(start_dir, pattern):
            self.wasRun = True
            self.assertEqual(start_dir, expectedPath)
            return tests
        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertTrue(self.wasRun)
        self.assertEqual(suite._tests, tests)

    # Horrible white box test
    def testNoExit(self):
        result = object()
        test = object()

        class FakeRunner(object):
            def run(self, test):
                self.test = test
                return result

        runner = FakeRunner()

        oldParseArgs = unittest.TestProgram.parseArgs
        def restoreParseArgs():
            unittest.TestProgram.parseArgs = oldParseArgs
        unittest.TestProgram.parseArgs = lambda *args: None
        self.addCleanup(restoreParseArgs)

        def removeTest():
            del unittest.TestProgram.test
        unittest.TestProgram.test = test
        self.addCleanup(removeTest)

        program = unittest.TestProgram(testRunner=runner, exit=False, verbosity=2)

        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    class FooBar(unittest.TestCase):
        def testPass(self):
            assert True
        def testFail(self):
            assert False

    class FooBarLoader(unittest.TestLoader):
        """Test loader that returns a suite containing FooBar."""
        def loadTestsFromModule(self, module):
            return self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

        def loadTestsFromNames(self, names, module):
            return self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

    def test_defaultTest_with_string(self):
        class FakeRunner(object):
            def run(self, test):
                self.test = test
                return True

        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner, exit=False,
                                       defaultTest='unittest.test',
                                       testLoader=self.FooBarLoader())
        self.assertEqual(('unittest.test',), program.testNames)

    def test_defaultTest_with_iterable(self):
        class FakeRunner(object):
            def run(self, test):
                self.test = test
                return True

        runner = FakeRunner()
        program = unittest.TestProgram(
            testRunner=runner, exit=False,
            defaultTest=['unittest.test', 'unittest.test2'],
            testLoader=self.FooBarLoader())
        self.assertEqual(['unittest.test', 'unittest.test2'],
                          program.testNames)

    def test_NonExit(self):
        program = unittest.main(exit=False,
                                testRunner=unittest.TextTestRunner(stream=io.StringIO()),
                                testLoader=self.FooBarLoader())
        self.assertTrue(hasattr(program, 'result'))


    def test_Exit(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            exit=True,
            testLoader=self.FooBarLoader())




class InitialisableProgram(unittest.TestProgram):
    exit = False
    result = None
    verbosity = 1
    defaultTest = None
    testRunner = None
    testLoader = unittest.defaultTestLoader
    module = '__main__'
    progName = 'test'
    test = 'test'
    def __init__(self, *args):
        pass

RESULT = object()

class FakeRunner(object):
    initArgs = None
    test = None
    raiseError = False

    def __init__(self, **kwargs):
        FakeRunner.initArgs = kwargs
        if FakeRunner.raiseError:
            FakeRunner.raiseError = False
            raise TypeError

    def run(self, test):
        FakeRunner.test = test
        return RESULT

class TestCommandLineArgs(unittest.TestCase):

    def setUp(self):
        self.program = InitialisableProgram()
        self.program.createTests = lambda: None
        FakeRunner.initArgs = None
        FakeRunner.test = None
        FakeRunner.raiseError = False

    def testVerbosity(self):
        program = unittest.TestProgram(tests=None, quiet=True)                  ###
        self.assertEqual(program.verbosity, 0)                                  ###

    def testRunTestsRunnerClass(self):
        program = self.program

        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.warnings = 'warnings'

        program.runTests()

        self.assertEqual(FakeRunner.initArgs, {'verbosity': 'verbosity',
                                                'failfast': 'failfast',
                                                'buffer': 'buffer',
                                                'warnings': 'warnings'})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testRunTestsRunnerInstance(self):
        program = self.program

        program.testRunner = FakeRunner()
        FakeRunner.initArgs = None

        program.runTests()

        # A new FakeRunner should not have been instantiated
        self.assertIsNone(FakeRunner.initArgs)

        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testRunTestsOldRunnerClass(self):
        program = self.program

        FakeRunner.raiseError = True
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.test = 'test'

        program.runTests()

        # If initialising raises a type error it should be retried
        # without the new keyword arguments
        self.assertEqual(FakeRunner.initArgs, {})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def _patch_isfile(self, names, exists=True):
        def isfile(path):
            return path in names
        original = os.path.isfile
        os.path.isfile = isfile
        def restore():
            os.path.isfile = original
        self.addCleanup(restore)


    def testParseArgsFileNames(self):
        # running tests with filenames instead of module names
        program = unittest.TestProgram(tests=None)                              ###
        argv = ['progname', 'foo.py', 'bar.Py', 'baz.PY', 'wing.txt']
        program.tests = argv[1:]                                                ###
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        # note that 'wing.txt' is not a Python file so the name should
        # *not* be converted to a module name
        expected = ['foo', 'bar', 'baz', 'wing.txt']
        self.assertEqual(program.testNames, expected)


    def testParseArgsFilePaths(self):
        program = unittest.TestProgram(tests=None)                              ###
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        program.tests = argv[1:]                                                ###
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)


    def testParseArgsNonExistentFiles(self):
        program = unittest.TestProgram(tests=None)                              ###
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        program.tests = argv[1:]                                                ###
        self._patch_isfile([])

        program.createTests = lambda: None
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

    def testParseArgsAbsolutePathsThatCanBeConverted(self):
        cur_dir = os.getcwd()
        program = unittest.TestProgram(tests=None)                              ###
        def _join(name):
            return os.path.join(cur_dir, name)
        argv = ['progname', _join('foo/bar/baz.py'), _join('green\\red.py')]
        program.tests = argv[1:]                                                ###
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    def testParseArgsAbsolutePathsThatCannotBeConverted(self):
        program = unittest.TestProgram(tests=None)                              ###
        # even on Windows '/...' is considered absolute by os.path.abspath
        argv = ['progname', '/foo/bar/baz.py', '/green/red.py']
        program.tests = argv[1:]                                                ###
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

        # it may be better to use platform specific functions to normalise paths
        # rather than accepting '.PY' and '\' as file separator on Linux / Mac
        # it would also be better to check that a filename is a valid module
        # identifier (we have a regex for this in loader.py)
        # for invalid filenames should we raise a useful error rather than
        # leaving the current error message (import of filename fails) in place?


if __name__ == '__main__':
    unittest.main()
