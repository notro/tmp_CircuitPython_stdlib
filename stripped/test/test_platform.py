import os
import platform
import sys
import unittest

from test import support

class PlatformTest(unittest.TestCase):
    def test_architecture(self):
        res = platform.architecture()

    def test_platform(self):
        for aliased in (False, True):
            for terse in (False, True):
                res = platform.platform(aliased, terse)

    def test_system(self):
        res = platform.system()

    def test_node(self):
        res = platform.node()

    def test_release(self):
        res = platform.release()

    def test_version(self):
        res = platform.version()

    def test_machine(self):
        res = platform.machine()

    def test_processor(self):
        res = platform.processor()

    def test_system_alias(self):
        res = platform.system_alias(
            platform.system(),
            platform.release(),
            platform.version(),
        )

    def test_uname(self):
        res = platform.uname()
        self.assertTrue(any(res))
        self.assertEqual(res[0], res.system)
        self.assertEqual(res[1], res.node)
        self.assertEqual(res[2], res.release)
        self.assertEqual(res[3], res.version)
        self.assertEqual(res[4], res.machine)
        self.assertEqual(res[5], res.processor)

