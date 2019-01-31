import os
import sys
import json
import unittest

from test import support

cjson = json                                                                    ###

PyTest = None                                                                   ### Avoid fixing up the import line in every test

class CTest(unittest.TestCase):
    if cjson is not None:
        json = cjson
        loads = staticmethod(cjson.loads)
        dumps = staticmethod(cjson.dumps)


def load_tests(loader, _, pattern):
    suite = unittest.TestSuite()

    pkg_dir = os.path.dirname(__file__)
    return support.load_package_tests(pkg_dir, loader, suite, pattern)
