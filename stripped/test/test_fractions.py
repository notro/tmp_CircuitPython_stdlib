"""Tests for Lib/fractions.py."""

import unittest
try:                                                                            ###
    import fractions                                                            ###
except ImportError as msg:                                                      ###
    raise unittest.SkipTest(str(msg))                                           ###
else:                                                                           ###
    print('\n\n\nfractions is avaiable\n\n')                                    ###
