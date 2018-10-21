import sys
import os
import unittest
from array import array

import io

from test.support import TESTFN                                                 ###

class AutoFileTests:
    # file tests for which a test file is automatically set up

    def setUp(self):
        try:                                                                    ###
            self.open = self.open.__func__                                      ### self.open is somehow bound
        except:                                                                 ###
            pass                                                                ###
        self.f = self.open(TESTFN, 'wb')

    def tearDown(self):
        if self.f:
            self.f.close()
        os.remove(TESTFN)

    def testReadinto(self):
        # verify readinto
        self.f.write(b'12')
        self.f.close()
        a = array('b', b'x'*10)
        self.f = self.open(TESTFN, 'rb')
        n = self.f.readinto(a)
        self.assertEqual(b'12', bytes(a)[:n])                                   ###

    def testErrors(self):
        f = self.f

        if hasattr(f, "readinto"):
            self.assertRaises((OSError, TypeError), f.readinto, "")
        f.close()

    def testMethods(self):
        methods = [                                                             ###
                   ('flush', ()),
                   ('__next__', ()),
                   ('read', ()),
                   ('readline', ()),
                   ('readlines', ()),
                   ]

        # __exit__ should close the file
        self.f.__exit__(None, None, None)

        for methodname, args in methods:
            method = getattr(self.f, methodname)
            # should raise on closed file
            self.assertRaises(OSError, method, *args)                           ###

        # file is closed, __exit__ shouldn't do anything
        self.assertEqual(self.f.__exit__(None, None, None), None)
        # it must also return None if an exception was given
        try:
            1/0
        except:
            self.assertEqual(self.f.__exit__(*sys.exc_info()), None)

    def testReadWhenWriting(self):
        self.assertRaises(OSError, self.f.read)

class CAutoFileTests(AutoFileTests, unittest.TestCase):
    open = io.open



class OtherFileTests:

    def setUp(self):                                                            ###
        try:                                                                    ###
            self.open = self.open.__func__                                      ###
        except:                                                                 ###
            pass                                                                ###
                                                                                ###
    def testSetBufferSize(self):
        # make sure that explicitly setting the buffer size doesn't cause
        # misbehaviour especially with repeated close() calls
        for s in (-1, 0, 1, 512):
            try:
                f = self.open(TESTFN, 'wb', s)
                f.write(str(s).encode("ascii"))
                f.close()
                f.close()
                f = self.open(TESTFN, 'rb', s)
                d = int(f.read().decode("ascii"))
                f.close()
                f.close()
            except OSError as msg:
                self.fail('error setting buffer size %d: %s' % (s, str(msg)))
            self.assertEqual(d, s)

class COtherFileTests(OtherFileTests, unittest.TestCase):
    open = io.open



def tearDownModule():
    # Historically, these tests have been sloppy about removing TESTFN.
    # So get rid of it no matter what.
    if os.path.exists(TESTFN):
        os.unlink(TESTFN)

