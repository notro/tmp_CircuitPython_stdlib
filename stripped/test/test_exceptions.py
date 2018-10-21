# Python test set -- part 5, built-in exceptions

import sys
import unittest


class NaiveException(Exception):
    def __init__(self, x):
        self.x = x


# XXX This is not really enough, each *operation* should be tested!

class ExceptionTests(unittest.TestCase):

    def raise_catch(self, exc, excname):
        try:
            raise exc("spam")
        except exc as err:
            buf1 = str(err)
        try:
            raise exc("spam")
        except exc as err:
            buf2 = str(err)
        self.assertEqual(buf1, buf2)
        self.assertEqual(exc.__name__, excname)

    def testRaising(self):
        self.raise_catch(AttributeError, "AttributeError")
        self.assertRaises(AttributeError, getattr, sys, "undefined_attribute")

        self.raise_catch(EOFError, "EOFError")
        self.raise_catch(OSError, "OSError")
        self.assertRaises(OSError, open, 'this file does not exist', 'r')

        self.raise_catch(ImportError, "ImportError")
        self.assertRaises(ImportError, __import__, "undefined_module")

        self.raise_catch(IndexError, "IndexError")

        self.raise_catch(KeyError, "KeyError")

        self.raise_catch(KeyboardInterrupt, "KeyboardInterrupt")

        self.raise_catch(MemoryError, "MemoryError")

        self.raise_catch(NameError, "NameError")
        try: x = undefined_variable
        except NameError: pass

        self.raise_catch(OverflowError, "OverflowError")
        x = 1
        for dummy in range(128):
            x += x  # this simply shouldn't blow up

        self.raise_catch(RuntimeError, "RuntimeError")

        self.raise_catch(SyntaxError, "SyntaxError")
        try: exec('/\n')
        except SyntaxError: pass

        self.raise_catch(IndentationError, "IndentationError")

        self.raise_catch(SystemExit, "SystemExit")
        self.assertRaises(SystemExit, sys.exit, 0)

        self.raise_catch(TypeError, "TypeError")
        try: [] + ()
        except TypeError: pass

        self.raise_catch(ValueError, "ValueError")
        self.assertRaises(ValueError, chr, 17<<16)

        self.raise_catch(ZeroDivisionError, "ZeroDivisionError")
        try: x = 1/0
        except ZeroDivisionError: pass

        self.raise_catch(Exception, "Exception")
        try: x = 1/0
        except Exception as e: pass

    def testInfiniteRecursion(self):
        def f():
            return f()
        self.assertRaises(RuntimeError, f)

        def g():
            try:
                return g()
            except ValueError:
                return -1
        self.assertRaises(RuntimeError, g)

    def test_str(self):
        # Make sure both instances and classes have a str representation.
        self.assertTrue(str(Exception))
        self.assertTrue(str(Exception('a')))
        self.assertTrue(str(Exception('a', 'b')))

    def testExceptionCleanupNames(self):
        # Make sure the local variable bound to the exception instance by
        # an "except" statement is only visible inside the except block.
        try:
            raise Exception()
        except Exception as e:
            self.assertTrue(e)
            del e
        self.assertNotIn('e', locals())

    def test_exception_target_in_nested_scope(self):
        # issue 4617: This used to raise a SyntaxError
        # "can not delete variable 'e' referenced in nested scope"
        def print_error():
            e
        try:
            something
        except Exception as e:
            print_error()
            # implicit "del e" here

    def test_generator_leaking2(self):
        # See issue 12475.
        def g():
            yield
        try:
            raise RuntimeError
        except RuntimeError:
            it = g()
            next(it)
        try:
            next(it)
        except StopIteration:
            pass
        self.assertEqual(sys.exc_info(), (None, None, None))

    def test_generator_leaking3(self):
        # See issue #23353.  When gen.throw() is called, the caller's
        # exception state should be save and restored.
        def g():
            try:
                yield
            except ZeroDivisionError:
                yield sys.exc_info()[1]
        it = g()
        next(it)
        try:
            1/0
        except ZeroDivisionError as e:
            self.assertIs(sys.exc_info()[1], e)
            gen_exc = it.throw(e)
            self.assertIs(sys.exc_info()[1], e)
            self.assertIs(gen_exc, e)
        self.assertEqual(sys.exc_info(), (None, None, None))

    def test_generator_leaking4(self):
        # See issue #23353.  When an exception is raised by a generator,
        # the caller's exception state should still be restored.
        def g():
            try:
                1/0
            except ZeroDivisionError:
                yield sys.exc_info()[0]
                raise
        it = g()
        try:
            raise TypeError
        except TypeError:
            # The caller's exception state (TypeError) is temporarily
            # saved in the generator.
            tp = next(it)
        self.assertIs(tp, ZeroDivisionError)
        try:
            next(it)
            # We can't check it immediately, but while next() returns
            # with an exception, it shouldn't have restored the old
            # exception state (TypeError).
        except ZeroDivisionError as e:
            self.assertIs(sys.exc_info()[1], e)
        # We used to find TypeError here.
        self.assertEqual(sys.exc_info(), (None, None, None))

    def test_generator_doesnt_retain_old_exc(self):
        def g():
            self.assertIsInstance(sys.exc_info()[1], RuntimeError)
            yield
            self.assertEqual(sys.exc_info(), (None, None, None))
        it = g()
        try:
            raise RuntimeError
        except RuntimeError:
            next(it)
        self.assertRaises(StopIteration, next, it)

    def test_generator_finalizing_and_exc_info(self):
        # See #7173
        def simple_gen():
            yield 1
        def run_gen():
            gen = simple_gen()
            try:
                raise RuntimeError
            except RuntimeError:
                return next(gen)
        run_gen()
        self.assertEqual(sys.exc_info(), (None, None, None))


class ImportErrorTests(unittest.TestCase):

    def test_non_str_argument(self):
        # Issue #15778
            arg = b'abc'
            exc = ImportError(arg)
            self.assertEqual(str(arg), str(exc))


