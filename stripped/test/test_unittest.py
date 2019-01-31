import os                                                                       ###
import unittest                                                                 ###
import unittest.test

from test import support


def test_main():
    res = unittest.main(module=None, verbosity=support.verbose, start='/lib/unittest/test', separate=True)  ###
    errors = len(res.result.errors)                                             ###
    failures = len(res.result.failures)                                         ###
    if errors or failures:                                                      ###
        raise support.TestFailed('Errors {}, Failures {}'.format(errors, failures))  ###

