"""Test cases for traceback module"""

from io import StringIO
import sys
import unittest
import re

import traceback


class SyntaxTracebackCases(unittest.TestCase):
    # For now, a very minimal set of tests.  I want to be sure that
    # formatting of SyntaxErrors works based on changes for 2.1.

    def get_exception_format(self, func, exc):
        try:
            func()
        except exc as value:
            return traceback.format_exception_only(exc, value)
        else:
            raise ValueError("call did not raise exception")


    def syntax_error_bad_indentation2(self):
        eval(" print(2)")                                                       ###


    def test_bad_indentation(self):

        err = self.get_exception_format(self.syntax_error_bad_indentation2,
                                        IndentationError)
        self.assertIn("IndentationError", err[1])                               ###

    def test_base_exception(self):
        # Test that exceptions derived from BaseException are formatted right
        e = KeyboardInterrupt()
        lst = traceback.format_exception_only(e.__class__, e)
        self.assertEqual(lst, ['KeyboardInterrupt\n'])

    def test_format_exception_only_bad__str__(self):
        class X(Exception):
            def __str__(self):
                1/0
        err = traceback.format_exception_only(X, X())
        self.assertEqual(len(err), 1)
        str_value = '<unprintable %s object>' % X.__name__
        str_name = X.__name__                                                   ###
        self.assertEqual(err[0], "%s: %s\n" % (str_name, str_value))

    def test_without_exception(self):
        err = traceback.format_exception_only(None, None)
        self.assertEqual(err, ['None\n'])



cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")

boundaries = re.compile(
    '(%s|%s)' % (re.escape(cause_message), re.escape(context_message)))


class BaseExceptionReportingTests:

    def get_exception(self, exception_or_callable):
        if isinstance(exception_or_callable, Exception):
            return exception_or_callable
        try:
            exception_or_callable()
        except Exception as e:
            return e

    def zero_div(self):
        1/0 # In zero_div

    def check_zero_div(self, msg):
        lines = msg.splitlines()
        self.assertTrue(lines[-3].startswith('  File'))
        self.assertIn('1/0 # In zero_div', lines[-2])
        self.assertTrue(lines[-1].startswith('ZeroDivisionError'), lines[-1])

    def test_simple(self):
        lines = self.get_report(self.zero_div).splitlines()                     ###
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith('Traceback'))
        self.assertTrue(lines[1].startswith('  File'))
        self.assertIn('zero_div', lines[2])                                     ###
        self.assertTrue(lines[3].startswith('ZeroDivisionError'))



class PyExcReportingTests(BaseExceptionReportingTests, unittest.TestCase):
    #
    # This checks reporting through the 'traceback' module, with both
    # format_exception() and print_exception().
    #

    def get_report(self, e):
        e = self.get_exception(e)
        tb = sys.exc_info()[2]                                                  ###
        s = ''.join(
            traceback.format_exception(type(e), e, tb))                         ###
        return s


