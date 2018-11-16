"""Supporting definitions for the Python regression tests."""

import contextlib
import os
import shutil
import sys
import unittest
UnicodeDecodeError = UnicodeError                                               ###
FileNotFoundError = OSError                                                     ###
NotADirectoryError = OSError                                                    ###

def import_module(name, deprecated=False, *, required_on=()):
        try:
            return __import__(name)                                             ###
        except ImportError as msg:
            raise unittest.SkipTest(str(msg))


verbose = 1              # Flag set to 0 by regrtest.py
if True:                                                                        ###
    _unlink = os.unlink
    _rmdir = os.rmdir
    _rmtree = shutil.rmtree

def unlink(filename):
    try:
        _unlink(filename)
    except (FileNotFoundError, NotADirectoryError):
        pass

def rmdir(dirname):
    try:
        _rmdir(dirname)
    except FileNotFoundError:
        pass

def rmtree(path):
    try:
        _rmtree(path)
    except FileNotFoundError:
        pass

TESTFN = '$test'                                                                ###

# FS_NONASCII: non-ASCII character encodable by os.fsencode(),
# or None if there is no such character.
FS_NONASCII = None
for character in (
    # First try printable and common characters to have a readable filename.
    # For each character, the encoding list are just example of encodings able
    # to encode the character (the list is not exhaustive).

    # U+00E6 (Latin Small Letter Ae): cp1252, iso-8859-1
    '\u00E6',
    # U+0130 (Latin Capital Letter I With Dot Above): cp1254, iso8859_3
    '\u0130',
    # U+0141 (Latin Capital Letter L With Stroke): cp1250, cp1257
    '\u0141',
    # U+03C6 (Greek Small Letter Phi): cp1253
    '\u03C6',
    # U+041A (Cyrillic Capital Letter Ka): cp1251
    '\u041A',
    # U+05D0 (Hebrew Letter Alef): Encodable to cp424
    '\u05D0',
    # U+060C (Arabic Comma): cp864, cp1006, iso8859_6, mac_arabic
    '\u060C',
    # U+062A (Arabic Letter Teh): cp720
    '\u062A',
    # U+0E01 (Thai Character Ko Kai): cp874
    '\u0E01',

    # Then try more "special" characters. "special" because they may be
    # interpreted or displayed differently depending on the exact locale
    # encoding and the font.

    # U+00A0 (No-Break Space)
    '\u00A0',
    # U+20AC (Euro Sign)
    '\u20AC',
):
    try:
        os.fsdecode(os.fsencode(character))
    except UnicodeError:
        pass
    else:
        FS_NONASCII = character
        break

# TESTFN_UNICODE is a non-ascii filename
TESTFN_UNICODE = TESTFN + "-\xe0\xf2\u0258\u0141\u011f"
TESTFN_ENCODING = 'utf-8'                                                       ###

# TESTFN_UNENCODABLE is a filename (str type) that should *not* be able to be
# encoded by the filesystem encoding (in strict mode). It can be None if we
# cannot generate such filename.
TESTFN_UNENCODABLE = None

# TESTFN_UNDECODABLE is a filename (bytes type) that should *not* be able to be
# decoded from the filesystem encoding (in strict mode). It can be None if we
# cannot generate such filename (ex: the latin1 encoding can decode any byte
# sequence). On UNIX, TESTFN_UNDECODABLE can be decoded by os.fsdecode() thanks
# to the surrogateescape error handler (PEP 383), but not from the filesystem
# encoding in strict mode.
TESTFN_UNDECODABLE = None
for name in (
    # b'\xff' is not decodable by os.fsdecode() with code page 932. Windows
    # accepts it to create a file or a directory, or don't accept to enter to
    # such directory (when the bytes name is used). So test b'\xe7' first: it is
    # not decodable from cp932.
    b'\xe7w\xf0',
    # undecodable from ASCII, UTF-8
    b'\xff',
    # undecodable from iso8859-3, iso8859-6, iso8859-7, cp424, iso8859-8, cp856
    # and cp857
    b'\xae\xd5'
    # undecodable from UTF-8 (UNIX and Mac OS X)
    b'\xed\xb2\x80', b'\xed\xb4\x80',
    # undecodable from shift_jis, cp869, cp874, cp932, cp1250, cp1251, cp1252,
    # cp1253, cp1254, cp1255, cp1257, cp1258
    b'\x81\x98',
):
    try:
        name.decode(TESTFN_ENCODING)
    except UnicodeDecodeError:
        TESTFN_UNDECODABLE = os.fsencode(TESTFN) + name
        break

if FS_NONASCII:
    TESTFN_NONASCII = TESTFN + '-' + FS_NONASCII
else:
    TESTFN_NONASCII = None

# Save the initial cwd
SAVEDCWD = os.getcwd()

@contextlib.contextmanager
def temp_dir(path=None, quiet=False):
    """Return a context manager that creates a temporary directory.

    Arguments:

      path: the directory to create temporarily.  If omitted or None,
        defaults to creating a temporary directory using tempfile.mkdtemp.

      quiet: if False (the default), the context manager raises an exception
        on error.  Otherwise, if the path is specified and cannot be
        created, only a warning is issued.

    """
    dir_created = False
    if path is None:
        import tempfile                                                         ### Don't burden everyone with this import
        path = tempfile.mkdtemp()
        dir_created = True
        path = os.path.realpath(path)
    else:
        try:
            os.mkdir(path)
            dir_created = True
        except OSError:
            if not quiet:
                raise
            warnings.warn('tests may fail, unable to create temp dir: ' + path,
                          RuntimeWarning, stacklevel=3)
    try:
        yield path
    finally:
        if dir_created:
            shutil.rmtree(path)

@contextlib.contextmanager
def change_cwd(path, quiet=False):
    """Return a context manager that changes the current working directory.

    Arguments:

      path: the directory to use as the temporary current working directory.

      quiet: if False (the default), the context manager raises an exception
        on error.  Otherwise, it issues only a warning and keeps the current
        working directory the same.

    """
    saved_dir = os.getcwd()
    try:
        os.chdir(path)
    except OSError:
        if not quiet:
            raise
        warnings.warn('tests may fail, unable to change CWD to: ' + path,
                      RuntimeWarning, stacklevel=3)
    try:
        yield os.getcwd()
    finally:
        os.chdir(saved_dir)


@contextlib.contextmanager
def temp_cwd(name='tempcwd', quiet=False):
    """
    Context manager that temporarily creates and changes the CWD.

    The function temporarily changes the current working directory
    after creating a temporary directory in the current directory with
    name *name*.  If *name* is None, the temporary directory is
    created using tempfile.mkdtemp.

    If *quiet* is False (default) and it is not possible to
    create or change the CWD, an error is raised.  If *quiet* is True,
    only a warning is raised and the original CWD is used.

    """
    with temp_dir(path=name, quiet=quiet) as temp_path:
        with change_cwd(temp_path, quiet=quiet) as cwd_dir:
            yield cwd_dir

# TEST_HOME_DIR refers to the top level directory of the "test" package
# that contains Python's regression test suite
TEST_SUPPORT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_HOME_DIR = os.path.dirname(TEST_SUPPORT_DIR)

def findfile(filename, subdir=None):
    """Try to find a file on sys.path or in the test directory.  If it is not
    found the argument passed to the function is returned (this does not
    necessarily signal failure; could still be the legitimate path).

    Setting *subdir* indicates a relative path to use to find the file
    rather than looking directly in the path directories.
    """
    if os.path.isabs(filename):
        return filename
    if subdir is not None:
        filename = os.path.join(subdir, filename)
    path = [TEST_HOME_DIR] + sys.path
    for dn in path:
        fn = os.path.join(dn, filename)
        if os.path.exists(fn): return fn
    return filename

@contextlib.contextmanager
def swap_attr(obj, attr, new_val):
    """Temporary swap out an attribute with a new object.

    Usage:
        with swap_attr(obj, "attr", 5):
            ...

        This will set obj.attr to 5 for the duration of the with: block,
        restoring the old value at the end of the block. If `attr` doesn't
        exist on `obj`, it will be created and then deleted at the end of the
        block.
    """
    if hasattr(obj, attr):
        real_val = getattr(obj, attr)
        setattr(obj, attr, new_val)
        try:
            yield
        finally:
            setattr(obj, attr, real_val)
    else:
        setattr(obj, attr, new_val)
        try:
            yield
        finally:
            delattr(obj, attr)

@contextlib.contextmanager
def swap_item(obj, item, new_val):
    """Temporary swap out an item with a new object.

    Usage:
        with swap_item(obj, "item", 5):
            ...

        This will set obj["item"] to 5 for the duration of the with: block,
        restoring the old value at the end of the block. If `item` doesn't
        exist on `obj`, it will be created and then deleted at the end of the
        block.
    """
    if item in obj:
        real_val = obj[item]
        obj[item] = new_val
        try:
            yield
        finally:
            obj[item] = real_val
    else:
        obj[item] = new_val
        try:
            yield
        finally:
            del obj[item]

def can_symlink():
    return False                                                                ###
def patch(test_instance, object_to_patch, attr_name, new_value):
    # check that 'attr_name' is a real attribute for 'object_to_patch'
    # will raise AttributeError if it does not exist
    getattr(object_to_patch, attr_name)

    # keep a copy of the old value
    attr_is_local = False
    try:
        old_value = object_to_patch.__dict__[attr_name]
    except (AttributeError, KeyError):
        old_value = getattr(object_to_patch, attr_name, None)
    else:
        attr_is_local = True

    # restore the value when the test is done
    def cleanup():
            setattr(object_to_patch, attr_name, old_value)

    test_instance.addCleanup(cleanup)

    # actually override the attribute
    setattr(object_to_patch, attr_name, new_value)


