import copy
import gc
import sys
import unittest



class FinalizationTest(unittest.TestCase):

    @unittest.expectedFailure                                                   ###
    def test_refcycle(self):
        # A generator caught in a refcycle gets finalized anyway.
        finalized = False
        def gen():
            nonlocal finalized
            try:
                g = yield
                yield 1
            finally:
                finalized = True

        g = gen()
        next(g)
        g.send(g)
        self.assertFalse(finalized)
        del g
        self.assertTrue(finalized)

    def test_lambda_generator(self):
        # Issue #23192: Test that a lambda returning a generator behaves
        # like the equivalent function
        f = lambda: (yield 1)
        def g(): return (yield 1)

        # test 'yield from'
        f2 = lambda: (yield from g())
        def g2(): return (yield from g())

        f3 = lambda: (yield from f())
        def g3(): return (yield from f())

        for gen_fun in (f, g, f2, g2, f3, g3):
            gen = gen_fun()
            self.assertEqual(next(gen), 1)
            with self.assertRaises(StopIteration) as cm:
                gen.send(2)


class GeneratorTest(unittest.TestCase):

    def test_copy(self):
        def f():
            yield 1
        g = f()
        with self.assertRaises(TypeError):
            copy.copy(g)



class ExceptionTest(unittest.TestCase):
    # Tests for the issue #23353: check that the currently handled exception
    # is correctly saved/restored in PyEval_EvalFrameEx().

    @unittest.expectedFailure                                                   ###
    def test_except_throw(self):
        def store_raise_exc_generator():
            try:
                self.assertEqual(sys.exc_info()[0], None)
                yield
            except Exception as exc:
                # exception raised by gen.throw(exc)
                self.assertEqual(sys.exc_info()[0], ValueError)
                self.assertIsNone(exc.__context__)
                yield

                # ensure that the exception is not lost
                self.assertEqual(sys.exc_info()[0], ValueError)
                yield

                # we should be able to raise back the ValueError
                raise

        make = store_raise_exc_generator()
        next(make)

        try:
            raise ValueError()
        except Exception as exc:
            try:
                make.throw(exc)
            except Exception:
                pass

        next(make)
        with self.assertRaises(ValueError) as cm:
            next(make)
        self.assertIsNone(cm.exception.__context__)

        self.assertEqual(sys.exc_info(), (None, None, None))

    def test_except_next(self):
        def gen():
            self.assertEqual(sys.exc_info()[0], ValueError)
            yield "done"

        g = gen()
        try:
            raise ValueError
        except Exception:
            self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (None, None, None))

    @unittest.expectedFailure                                                   ###
    def test_except_gen_except(self):
        def gen():
            try:
                self.assertEqual(sys.exc_info()[0], None)
                yield
                # we are called from "except ValueError:", TypeError must
                # inherit ValueError in its context
                raise TypeError()
            except TypeError as exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
            # here we are still called from the "except ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            yield
            self.assertIsNone(sys.exc_info()[0])
            yield "done"

        g = gen()
        next(g)
        try:
            raise ValueError
        except Exception:
            next(g)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (None, None, None))

    @unittest.expectedFailure                                                   ###
    def test_except_throw_exception_context(self):
        def gen():
            try:
                try:
                    self.assertEqual(sys.exc_info()[0], None)
                    yield
                except ValueError:
                    # we are called from "except ValueError:"
                    self.assertEqual(sys.exc_info()[0], ValueError)
                    raise TypeError()
            except Exception as exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
                self.assertEqual(type(exc.__context__), ValueError)
            # we are still called from "except ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            yield
            self.assertIsNone(sys.exc_info()[0])
            yield "done"

        g = gen()
        next(g)
        try:
            raise ValueError
        except Exception as exc:
            g.throw(exc)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (None, None, None))


