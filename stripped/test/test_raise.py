# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Tests for the raise statement."""

import unittest




class Context:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        return True


class TestRaise(unittest.TestCase):
    def test_reraise(self):
        try:
            try:
                raise IndexError()
            except IndexError as e:
                exc1 = e
                raise
        except IndexError as exc2:
            self.assertTrue(exc1 is exc2)
        else:
            self.fail("No exception raised")

    def test_except_reraise(self):
        def reraise():
            try:
                raise TypeError("foo")
            except:
                try:
                    raise KeyError("caught")
                except KeyError:
                    pass
                raise
        self.assertRaises(TypeError, reraise)

    def test_finally_reraise(self):
        def reraise():
            try:
                raise TypeError("foo")
            except:
                try:
                    raise KeyError("caught")
                finally:
                    raise
        self.assertRaises(KeyError, reraise)

    def test_with_reraise1(self):
        def reraise():
            try:
                raise TypeError("foo")
            except:
                with Context():
                    pass
                raise
        self.assertRaises(TypeError, reraise)

    def test_with_reraise2(self):
        def reraise():
            try:
                raise TypeError("foo")
            except:
                with Context():
                    raise KeyError("caught")
                raise
        self.assertRaises(TypeError, reraise)

    def test_yield_reraise(self):
        def reraise():
            try:
                raise TypeError("foo")
            except:
                yield 1
                raise
        g = reraise()
        next(g)
        self.assertRaises(TypeError, lambda: next(g))
        self.assertRaises(StopIteration, lambda: next(g))

    def test_erroneous_exception(self):
        class MyException(Exception):
            def __init__(self):
                raise RuntimeError()

        try:
            raise MyException
        except RuntimeError:
            pass
        else:
            self.fail("No exception raised")

    def test_assert_with_tuple_arg(self):
        try:
            assert False, (3,)
        except AssertionError as e:
            self.assertEqual(str(e), "(3,)")



class TestRemovedFunctionality(unittest.TestCase):
    def test_tuples(self):
        try:
            raise (IndexError, KeyError) # This should be a tuple!
        except TypeError:
            pass
        else:
            self.fail("No exception raised")

    def test_strings(self):
        try:
            raise "foo"
        except TypeError:
            pass
        else:
            self.fail("No exception raised")


