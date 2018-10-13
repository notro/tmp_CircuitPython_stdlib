"""Unittest main program"""

import sys
import os
from fnmatch import fnmatch                                                     ###
import gc                                                                       ###
import time                                                                     ###

from . import loader, runner
from . import mp_function_attributes                                            ###

__unittest = True


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
                    exit=False, verbosity=1, failfast=False, catchbreak=False,  ###
                    buffer=False, warnings=None,                                ###
                    quiet=False, separate=False,                                ###
                    tests=[], start='.', pattern='test*.mpy', top=None):        ###
        if isinstance(module, str):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)
        else:
            self.module = module
        if argv is not None:                                                    ###
            raise NotImplementedError('argparse and thus argv is not implemented')  ###

        self.exit = exit
        self.failfast = failfast
        self.catchbreak = catchbreak
        self.verbosity = 0 if quiet else verbosity                              ###
        self.separate = separate                                                ###
        self.tests = tests                                                      ###
        self.start = start                                                      ###
        self.pattern = pattern                                                  ###    .mpy .py
        self.top = top                                                          ###
        self.buffer = buffer
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
        self.progName = 'UnitTest'                                              ###
        self.saved_modules = dict(sys.modules)                                  ###
        self.saved_globals = dict(globals())                                    ###
        if self.tests is None:                                                  ### For testing
            return                                                              ###
        if self.parseArgs(argv):                                                ###
            self.runTests()                                                     ###


    def parseArgs(self, argv):
        if self.module is None:
            if not self.tests:
                # this allows "python -m unittest -v" to still work for
                # test discovery.
                self._do_discovery([])
                return

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
        loader = self.testLoader if Loader is None else Loader()
        self.get_testRunner()                                                   ###
        if self.separate:                                                       ###
            self._do_discovery_separate(loader)                                 ###
            return                                                              ###
        self.test = loader.discover(self.start, self.pattern, self.top)
        self.runTests()                                                         ###

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
