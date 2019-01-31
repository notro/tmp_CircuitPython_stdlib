import unittest                                                                 ###
import sys
from test.test_json import PyTest, CTest


class TestScanstring:
    pass                                                                        ###

@unittest.skip('Missing json.decoder.scanstring')                               ###
class TestCScanstring(TestScanstring, CTest): pass
