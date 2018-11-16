import os
import sys
import json
import unittest


pyjson = json                                                                   ###

# create two base classes that will be used by the other tests
class PyTest(unittest.TestCase):
    json = pyjson
    loads = staticmethod(pyjson.loads)
    dumps = staticmethod(pyjson.dumps)


# test PyTest and CTest checking if the functions come from the right module
class TestPyTest(PyTest):
    def test_pyjson(self):
        self.assertEqual(self.json.scanner.make_scanner.__module__,
                         'json.scanner')
        self.assertEqual(self.json.decoder.scanstring.__module__,
                         'json.decoder')
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         'json.encoder')

CTest = None                                                                    ### Avoid fixing up the import line in every test


