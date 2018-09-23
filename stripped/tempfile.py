"""Temporary files.

This module provides generic, low- and high-level interfaces for
creating temporary files and directories.  All of the interfaces
provided by this module can be used without fear of race conditions
except for 'mktemp'.  'mktemp' is subject to race conditions and
should not be used; it is provided for backward compatibility only.

This module also provides some data items to the user:

  TMP_MAX  - maximum number of names that will be tried before
             giving up.
  tempdir  - If this is set to a string before the first use of
             any routine from this module, it will be considered as
             another candidate location to store temporary files.
"""



# Imports.

import io as _io
import os as _os
import shutil as _shutil
import errno as _errno


if hasattr(_os, 'TMP_MAX'):
    TMP_MAX = _os.TMP_MAX
else:
    TMP_MAX = 10000

# Although it does not have an underscore for historical reasons, this
# variable is an internal implementation detail (see issue 10354).
template = "tmp"

# Internal routines.


if hasattr(_os, "lstat"):
    _stat = _os.lstat
elif hasattr(_os, "stat"):
    _stat = _os.stat
else:
    # Fallback.  All we need is something that raises OSError if the
    # file doesn't exist.
    def _stat(fn):
        fd = _os.open(fn, _os.O_RDONLY)
        _os.close(fd)

def _exists(fn):
    try:
        _stat(fn)
    except OSError:
        return False
    else:
        return True

class _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"


    def __iter__(self):
        return self

    def __next__(self):
        c = self.characters
        letters = [c[b % 37] for b in _os.urandom(8)]                           ###
        return ''.join(letters)

def _candidate_tempdir_list():
    """Generate a list of candidate temporary directories which
    _get_default_tempdir will try."""

    dirlist = []

    dirlist.append('/tmp')                                                      ###

    # As a last resort, the current directory.
    try:
        dirlist.append(_os.getcwd())
    except (AttributeError, OSError):
        dirlist.append(_os.curdir)

    return dirlist

def _get_default_tempdir():
    """Calculate the default directory to use for temporary files.
    This routine should be called exactly once.

    We determine whether or not a candidate temp dir is usable by
    trying to create and write to a file in that directory.  If this
    is successful, the test file is deleted.  To prevent denial of
    service, the name of the test file must be randomized."""

    namer = _RandomNameSequence()
    dirlist = _candidate_tempdir_list()

    for dir in dirlist:
        if dir != _os.curdir:
            dir = _os.path.abspath(dir)
        # Try only a few names per directory.
        for seq in range(100):
            name = next(namer)
            filename = _os.path.join(dir, name)
            try:
                try:                                                        ###
                    with open(filename, 'wb') as f:                         ###
                        f.write(b'blat')                                    ###
                finally:
                    _os.unlink(filename)
                return dir
            except OSError:
                break   # no point trying more names in this directory
    raise FileNotFoundError(_errno.ENOENT,
                            "No usable temporary directory found in %s" %
                            dirlist)

_name_sequence = None

def _get_candidate_names():
    """Common setup sequence for all user-callable interfaces."""

    global _name_sequence
    if _name_sequence is None:
                _name_sequence = _RandomNameSequence()
    return _name_sequence




# User visible interfaces.

def gettempprefix():
    """Accessor for tempdir.template."""
    return template

tempdir = None

def gettempdir():
    """Accessor for tempfile.tempdir."""
    global tempdir
    if tempdir is None:
                tempdir = _get_default_tempdir()
    return tempdir



def mkdtemp(suffix="", prefix=template, dir=None):
    """User-callable function to create and return a unique temporary
    directory.  The return value is the pathname of the directory.

    Arguments are as for mkstemp, except that the 'text' argument is
    not accepted.

    The directory is readable, writable, and searchable only by the
    creating user.

    Caller is responsible for deleting the directory when done with it.
    """

    if dir is None:
        dir = gettempdir()

    names = _get_candidate_names()

    FileExistsError = OSError                                                   ###
    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        try:
            _os.mkdir(file, 0o700)
            return file
        except FileExistsError:
            continue    # try again

    raise FileExistsError(_errno.EEXIST,
                          "No usable temporary directory name found")

def mktemp(suffix="", prefix=template, dir=None):
    """User-callable function to return a unique temporary file name.  The
    file is not created.

    Arguments are as for mkstemp, except that the 'text' argument is
    not accepted.

    This function is unsafe and should not be used.  The file name
    refers to a file that did not exist at some point, but by the time
    you get around to creating it, someone else may have beaten you to
    the punch.
    """

##    from warnings import warn as _warn
##    _warn("mktemp is a potential security risk to your program",
##          RuntimeWarning, stacklevel=2)

    if dir is None:
        dir = gettempdir()

    names = _get_candidate_names()
    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        if not _exists(file):
            return file

    raise FileExistsError(_errno.EEXIST,
                          "No usable temporary filename found")


