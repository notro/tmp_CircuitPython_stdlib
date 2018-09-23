import unittest
import os

import stat as py_stat                                                          ###

class TestFilemode:
    statmod = None

    file_flags = {'SF_APPEND', 'SF_ARCHIVED', 'SF_IMMUTABLE', 'SF_NOUNLINK',
                  'SF_SNAPSHOT', 'UF_APPEND', 'UF_COMPRESSED', 'UF_HIDDEN',
                  'UF_IMMUTABLE', 'UF_NODUMP', 'UF_NOUNLINK', 'UF_OPAQUE'}

    formats = {'S_IFBLK', 'S_IFCHR', 'S_IFDIR', 'S_IFIFO', 'S_IFLNK',
               'S_IFREG', 'S_IFSOCK'}

    format_funcs = {'S_ISBLK', 'S_ISCHR', 'S_ISDIR', 'S_ISFIFO', 'S_ISLNK',
                    'S_ISREG', 'S_ISSOCK'}

    stat_struct = {
        'ST_MODE': 0,
        'ST_INO': 1,
        'ST_DEV': 2,
        'ST_NLINK': 3,
        'ST_UID': 4,
        'ST_GID': 5,
        'ST_SIZE': 6,
        'ST_ATIME': 7,
        'ST_MTIME': 8,
        'ST_CTIME': 9}

    # permission bit value are defined by POSIX
    permission_bits = {
        'S_ISUID': 0o4000,
        'S_ISGID': 0o2000,
        'S_ENFMT': 0o2000,
        'S_ISVTX': 0o1000,
        'S_IRWXU': 0o700,
        'S_IRUSR': 0o400,
        'S_IREAD': 0o400,
        'S_IWUSR': 0o200,
        'S_IWRITE': 0o200,
        'S_IXUSR': 0o100,
        'S_IEXEC': 0o100,
        'S_IRWXG': 0o070,
        'S_IRGRP': 0o040,
        'S_IWGRP': 0o020,
        'S_IXGRP': 0o010,
        'S_IRWXO': 0o007,
        'S_IROTH': 0o004,
        'S_IWOTH': 0o002,
        'S_IXOTH': 0o001}


    def test_module_attributes(self):
        for key, value in self.stat_struct.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        for key, value in self.permission_bits.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        for key in self.file_flags:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        for key in self.formats:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        for key in self.format_funcs:
            func = getattr(self.statmod, key)
            self.assertTrue(callable(func))
            self.assertEqual(func(0), 0)




class TestFilemodePyStat(TestFilemode, unittest.TestCase):
    statmod = py_stat


