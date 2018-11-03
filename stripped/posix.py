# MIT License
# Copyright 2018 Noralf Trønnes

import collections
import _os
from _os import (chdir, getcwd, listdir, remove, rename, rmdir, sep, sync, uname, unlink, urandom)

stat_result = collections.namedtuple('os.stat_result', ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid',
                                                        'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime'))

def stat(path):
    return stat_result(*_os.stat(path))

lstat = stat

statvfs_result = collections.namedtuple('os.statvfs_result', ('f_bsize', 'f_frsize', 'f_blocks', 'f_bfree', 'f_bavail',
                                                              'f_files', 'f_ffree', 'f_favail', 'f_flag', 'f_namemax'))

del collections

def statvfs(path):
    return statvfs_result(*_os.statvfs(path))

def mkdir(path, mode=0o777, dir_fd=None):
    _os.mkdir(path)

def getcwdb():
    return getcwd().encode('utf-8', 'surrogateescape')

# This should have had keys and values as bytes, but str is fine since we use it as-is in os
environ = {}
