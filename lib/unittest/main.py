"""Unittest main program"""

import sys
#import argparse
import os
from fnmatch import fnmatch                                                     ###
import gc                                                                       ###
import time                                                                     ###

from . import loader, runner
#from .signals import installHandler
from . import mp_function_attributes                                            ###

__unittest = True

#MAIN_EXAMPLES = """\
#Examples:
#  %(prog)s test_module               - run tests from test_module
#  %(prog)s module.TestClass          - run tests from module.TestClass
#  %(prog)s module.Class.test_method  - run specified test method
#"""
#
#MODULE_EXAMPLES = """\
#Examples:
#  %(prog)s                           - run default set of tests
#  %(prog)s MyTestSuite               - run suite 'MyTestSuite'
#  %(prog)s MyTestCase.testSomething  - run MyTestCase.testSomething
#  %(prog)s MyTestCase                - run all 'test*' test methods
#                                       in MyTestCase
#"""

def _convert_name(name):
    # on Linux / Mac OS X 'foo.PY' is not importable, but on
    # Windows it is. Simpler to do a case insensitive match
    # a better check would be to check that the name is a
    # valid Python module name.
    if os.path.isfile(name) and name.lower().endswith('.py'):
        if os.path.isabs(name):
            rel_path = os.path.relpath(name, os.getcwd())
            if os.path.isabs(rel_path) or rel_path.startswith(os.pardir):
                return name
            name = rel_path
        # on Windows both '\' and '/' are used as path
        # separators. Better to replace both than rely on os.path.sep
        return name[:-3].replace('\\', '.').replace('/', '.')
    return name

def _convert_names(names):
    return [_convert_name(name) for name in names]


class TestProgram(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    # defaults for testing
    module=None
    verbosity = 1
    failfast = catchbreak = buffer = progName = warnings = None
    _discovery_parser = None

    def __init__(self, module='__main__', defaultTest=None, argv=None,
                    testRunner=None, testLoader=loader.defaultTestLoader,
#                    exit=True, verbosity=1, failfast=None, catchbreak=None,
                    exit=False, verbosity=1, failfast=False, catchbreak=False,  ###
#                    buffer=None, warnings=None):
                    buffer=False, warnings=None,                                ###
                    quiet=False, separate=False,                                ###
                    tests=[], start='.', pattern='test*.mpy', top=None):        ###
        if isinstance(module, str):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)
        else:
            self.module = module
#        if argv is None:
#            argv = sys.argv
        if argv is not None:                                                    ###
            raise NotImplementedError('argparse and thus argv is not implemented')  ###

        self.exit = exit
        self.failfast = failfast
        self.catchbreak = catchbreak
#        self.verbosity = verbosity
        self.verbosity = 0 if quiet else verbosity                              ###
        self.separate = separate                                                ###
        self.tests = tests                                                      ###
        self.start = start                                                      ###
        self.pattern = pattern                                                  ###    .mpy .py
        self.top = top                                                          ###
        self.buffer = buffer
#        if warnings is None and not sys.warnoptions:
        if warnings is None:                                                    ###
            # even if DreprecationWarnings are ignored by default
            # print them anyway unless other warnings settings are
            # specified by the warnings arg or the -W python flag
            self.warnings = 'default'
        else:
            # here self.warnings is set either to the value passed
            # to the warnings args or to None.
            # If the user didn't pass a value self.warnings will
            # be None. This means that the behavior is unchanged
            # and depends on the values passed to -W.
            self.warnings = warnings
        self.defaultTest = defaultTest
        self.testRunner = testRunner
        self.testLoader = testLoader
#        self.progName = os.path.basename(argv[0])
        self.progName = 'UnitTest'                                              ###
        self.saved_modules = dict(sys.modules)                                  ###
        self.saved_globals = dict(globals())                                    ###
        if self.tests is None:                                                  ### For testing
            return                                                              ###
#        self.parseArgs(argv)
#        self.runTests()
        if self.parseArgs(argv):                                                ###
            self.runTests()                                                     ###

#    def usageExit(self, msg=None):
#        if msg:
#            print(msg)
#        if self._discovery_parser is None:
#            self._initArgParsers()
#        self._print_help()
#        sys.exit(2)
#
#    def _print_help(self, *args, **kwargs):
#        if self.module is None:
#            print(self._main_parser.format_help())
#            print(MAIN_EXAMPLES % {'prog': self.progName})
#            self._discovery_parser.print_help()
#        else:
#            print(self._main_parser.format_help())
#            print(MODULE_EXAMPLES % {'prog': self.progName})

    def parseArgs(self, argv):
#        self._initArgParsers()
        if self.module is None:
#            if len(argv) > 1 and argv[1].lower() == 'discover':
#                self._do_discovery(argv[2:])
#                return
#            self._main_parser.parse_args(argv[1:], self)
            if not self.tests:
                # this allows "python -m unittest -v" to still work for
                # test discovery.
                self._do_discovery([])
                return
#        else:
#            self._main_parser.parse_args(argv[1:], self)

        if self.tests:
            self.testNames = _convert_names(self.tests)
            if __name__ == '__main__':
                # to support python -m unittest ...
                self.module = None
        elif self.defaultTest is None:
            # createTests will load tests from self.module
            self.testNames = None
        elif isinstance(self.defaultTest, str):
            self.testNames = (self.defaultTest,)
        else:
            self.testNames = list(self.defaultTest)
        self.createTests()
        return True                                                             ###

    def createTests(self):
        if self.testNames is None:
            self.test = self.testLoader.loadTestsFromModule(self.module)
        else:
            self.test = self.testLoader.loadTestsFromNames(self.testNames,
                                                           self.module)

#    def _initArgParsers(self):
#        parent_parser = self._getParentArgParser()
#        self._main_parser = self._getMainArgParser(parent_parser)
#        self._discovery_parser = self._getDiscoveryArgParser(parent_parser)
#
#    def _getParentArgParser(self):
#        parser = argparse.ArgumentParser(add_help=False)
#
#        parser.add_argument('-v', '--verbose', dest='verbosity',
#                            action='store_const', const=2,
#                            help='Verbose output')
#        parser.add_argument('-q', '--quiet', dest='verbosity',
#                            action='store_const', const=0,
#                            help='Quiet output')
#
#        if self.failfast is None:
#            parser.add_argument('-f', '--failfast', dest='failfast',
#                                action='store_true',
#                                help='Stop on first fail or error')
#            self.failfast = False
#        if self.catchbreak is None:
#            parser.add_argument('-c', '--catch', dest='catchbreak',
#                                action='store_true',
#                                help='Catch Ctrl-C and display results so far')
#            self.catchbreak = False
#        if self.buffer is None:
#            parser.add_argument('-b', '--buffer', dest='buffer',
#                                action='store_true',
#                                help='Buffer stdout and stderr during tests')
#            self.buffer = False
#
#        return parser
#
#    def _getMainArgParser(self, parent):
#        parser = argparse.ArgumentParser(parents=[parent])
#        parser.prog = self.progName
#        parser.print_help = self._print_help
#
#        parser.add_argument('tests', nargs='*',
#                            help='a list of any number of test modules, '
#                            'classes and test methods.')
#
#        return parser
#
#    def _getDiscoveryArgParser(self, parent):
#        parser = argparse.ArgumentParser(parents=[parent])
#        parser.prog = '%s discover' % self.progName
#        parser.epilog = ('For test discovery all test modules must be '
#                         'importable from the top level directory of the '
#                         'project.')
#
#        parser.add_argument('-s', '--start-directory', dest='start',
#                            help="Directory to start discovery ('.' default)")
#        parser.add_argument('-p', '--pattern', dest='pattern',
#                            help="Pattern to match tests ('test*.py' default)")
#        parser.add_argument('-t', '--top-level-directory', dest='top',
#                            help='Top level directory of project (defaults to '
#                                 'start directory)')
#        for arg in ('start', 'pattern', 'top'):
#            parser.add_argument(arg, nargs='?',
#                                default=argparse.SUPPRESS,
#                                help=argparse.SUPPRESS)
#
#        return parser

    def gc_collect(self):                                                       ###
        if self.verbosity > 2:                                                  ###
            mfree = gc.mem_free()                                               ###
        gc.collect()                                                            ###
        if self.verbosity > 2:                                                  ###
            tpl = 'gc_collect: mem_free: {:3.0f}k -> {:3.0f}k\n'                ###
            msg = tpl.format(mfree / 1024, gc.mem_free() / 1024)                ###
            self.testRunner.stream.write(msg)                                   ###
                                                                                ###
    def cleanup(self):                                                          ###
        self.result = None                                                      ###
        mp_function_attributes.func_clearattrs()                                ###
        for mod in sys.modules:                                                 ###
            if mod not in self.saved_modules:                                   ###
                if self.verbosity > 2:                                          ###
                    print('del sys.modules[' + repr(mod) + ']')                 ###
                del sys.modules[mod]                                            ###
                                                                                ###
        for name in globals():                                                  ###
            if name not in self.saved_globals:                                  ###
                if self.verbosity > 2:                                          ###
                    print('del globals()[{!r}]'.format(name))                   ###
                del globals()[name]                                             ###
                                                                                ###
        self.gc_collect()                                                       ###
                                                                                ###
        if self.verbosity > 3:                                                  ###
            print('globals()', len(globals()), globals())                       ###
            print()                                                             ###
            print('sys.modules', len(sys.modules), sys.modules)                 ###
            print()                                                             ###
                                                                                ###
    def _do_discovery_separate(self, loader):                                   ###
        run = 0                                                                 ###
        errors = 0                                                              ###
        failures = 0                                                            ###
        skipped = 0                                                             ###
        expectedFails = 0                                                       ###
        unexpectedSuccesses = 0                                                 ###
        t_start = time.monotonic()                                              ###
                                                                                ###
        for path in sorted(os.listdir(self.start)):                             ###
            if not fnmatch(path, self.pattern):                                 ###
                if self.verbosity > 2:                                          ###
                    self.testRunner.stream.write('SKIPPED {}\n'.format(path))   ###
                continue                                                        ###
                                                                                ###
            heading = '\n\n'                                                    ###
            heading += '#' * 70                                                 ###
            heading += '\n#\n'                                                  ###
            heading += '# {:50}(mem_free: {:3.0f}k)\n'.format(path, gc.mem_free() / 1024)  ###
            heading += '#\n'                                                    ###
            heading += '\n'                                                     ###
            self.testRunner.stream.write(heading)                               ###
                                                                                ###
            self.test = loader.discover(self.start, path)                       ###
            self.gc_collect()                                                   ###
            self.runTests()                                                     ###
                                                                                ###
            run += self.result.testsRun                                         ###
            errors += len(self.result.errors)                                   ###
            failures += len(self.result.failures)                               ###
            skipped += len(self.result.skipped)                                 ###
            expectedFails += len(self.result.expectedFailures)                  ###
            unexpectedSuccesses += len(self.result.unexpectedSuccesses)         ###
            self.cleanup()                                                      ###
            self.testRunner = None                                              ###
            self.get_testRunner()                                               ###
                                                                                ###
        t_end = time.monotonic() - t_start                                      ###
        msg = '\n'                                                              ###
        msg += '+' * 70                                                         ###
        msg += '\n\n'                                                           ###
        msg += 'Total:\n'                                                       ###
        msg += '\n'                                                             ###
        msg += 'Ran {} tests in {:.3f}s\n'.format(run, t_end)                   ###
        msg += '\n'                                                             ###
        if errors or failures:                                                  ###
            msg += 'FAILED'                                                     ###
            if failures:                                                        ###
                msg += ' (failures={})'.format(failures)                        ###
            if errors:                                                          ###
                msg += ' (errors={})'.format(errors)                            ###
        else:                                                                   ###
            msg += 'OK'                                                         ###
        if skipped:                                                             ###
            msg += ' (skipped={})'.format(skipped)                              ###
        if expectedFails:                                                       ###
            msg += ' (expected failures={})'.format(expectedFails)              ###
        if unexpectedSuccesses:                                                 ###
            msg += ' (unexpected successes={})'.format(unexpectedSuccesses)     ###
        msg += '\n'                                                             ###
                                                                                ###
        self.testRunner.stream.write(msg)                                       ###
                                                                                ###
    def _do_discovery(self, argv, Loader=None):
#        self.start = '.'
#        self.pattern = 'test*.py'
#        self.top = None
#        if argv is not None:
#            # handle command line args for test discovery
#            if self._discovery_parser is None:
#                # for testing
#                self._initArgParsers()
#            self._discovery_parser.parse_args(argv, self)
#
        loader = self.testLoader if Loader is None else Loader()
        self.get_testRunner()                                                   ###
        if self.separate:                                                       ###
            self._do_discovery_separate(loader)                                 ###
            return                                                              ###
        self.test = loader.discover(self.start, self.pattern, self.top)
        self.runTests()                                                         ###

#    def runTests(self):
#        if self.catchbreak:
#            installHandler()
    def get_testRunner(self):                                                   ###
        if self.testRunner is None:
            self.testRunner = runner.TextTestRunner
        if isinstance(self.testRunner, type):
            try:
                testRunner = self.testRunner(verbosity=self.verbosity,
                                             failfast=self.failfast,
                                             buffer=self.buffer,
                                             warnings=self.warnings)
            except TypeError:
                # didn't accept the verbosity, buffer or failfast arguments
                testRunner = self.testRunner()
            self.testRunner = testRunner                                        ###
        else:
            # it is assumed to be a TestRunner instance
            testRunner = self.testRunner
        return testRunner                                                       ###
                                                                                ###
    def runTests(self):                                                         ###
        testRunner = self.get_testRunner()                                      ###
        self.result = testRunner.run(self.test)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())

main = TestProgram
