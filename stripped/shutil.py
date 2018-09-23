import os
import sys
import stat
from os.path import abspath
import fnmatch
class Error(OSError):
    pass

class SameFileError(Error):
    """Raised when source and destination are the same file."""

class SpecialFileError(OSError):
    """Raised when trying to do a kind of operation (e.g. copying) which is
    not supported on a special file (e.g. a named pipe)"""

class ExecError(OSError):
    """Raised when a command could not be executed"""

class ReadError(OSError):
    """Raised when an archive cannot be read"""

class RegistryError(Exception):
    """Raised when a registry operation with the archiving
    and unpacking registeries fails"""


def copyfileobj(fsrc, fdst, length=128):                                        ###
    """copy data from file-like object fsrc to file-like object fdst"""
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

def _samefile(src, dst):

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

def copyfile(src, dst, *, follow_symlinks=True):
    """Copy data from src to dst.

    If follow_symlinks is not set and src is a symbolic link, a new
    symlink will be created instead of copying the file it points to.

    """
    if _samefile(src, dst):
        raise SameFileError("{!r} and {!r} are the same file".format(src, dst))

    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass

    if True:                                                                    ###
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copyfileobj(fsrc, fdst)
    return dst

def copy(src, dst, *, follow_symlinks=True):
    """Copy data and mode bits ("cp src dst"). Return the file's destination.

    The destination may be a directory.

    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    If source and destination are the same file, a SameFileError will be
    raised.

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    return dst

def copy2(src, dst, *, follow_symlinks=True):
    """Copy data and all stat info ("cp -p src dst"). Return the file's
    destination."

    The destination may be a directory.

    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    return dst

def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.

    Patterns is a sequence of glob-style patterns
    that are used to exclude files"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns

def copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2,
             ignore_dangling_symlinks=False):
    """Recursively copy a directory tree.

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added in the list of errors raised in
    an Error exception at the end of the copy process.

    You can set the optional ignore_dangling_symlinks flag to true if you
    want to silence this exception. Notice that this has no effect on
    platforms that don't support os.symlink.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    The optional copy_function argument is a callable that will be used
    to copy each file. It will be called with the source path and the
    destination path as arguments. By default, copy2() is used, but any
    function that supports the same signature (like copy()) can be used.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):                                          ###
                copytree(srcname, dstname, symlinks, ignore, copy_function)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    if errors:
        raise Error(errors)
    return dst

# version vulnerable to race conditions
def _rmtree_unsafe(path, onerror):
    names = []
    try:
        names = os.listdir(path)
    except OSError:
        if onerror is None:                                                      ###
            raise                                                                ###
        onerror(os.listdir, path, sys.exc_info())
    for name in names:
        fullname = os.path.join(path, name)
        try:
            mode = os.lstat(fullname).st_mode
        except OSError:
            mode = 0
        if stat.S_ISDIR(mode):
            _rmtree_unsafe(fullname, onerror)
        else:
            try:
                os.unlink(fullname)
            except OSError:
                if onerror is None:                                             ###
                    raise                                                       ###
                onerror(os.unlink, fullname, sys.exc_info())
    try:
        os.rmdir(path)
    except OSError:
        if onerror is None:                                                      ###
            raise                                                                ###
        onerror(os.rmdir, path, sys.exc_info())

def rmtree(path, ignore_errors=False, onerror=None):
    """Recursively delete a directory tree.

    If ignore_errors is set, errors are ignored; otherwise, if onerror
    is set, it is called to handle the error with arguments (func,
    path, exc_info) where func is platform and implementation dependent;
    path is the argument to that function that caused it to fail; and
    exc_info is a tuple returned by sys.exc_info().  If ignore_errors
    is false and onerror is None, an exception is raised.

    """
    if ignore_errors:
        def onerror(*args):
            pass
    return _rmtree_unsafe(path, onerror)                                        ###

def _basename(path):
    # A basename() variant which first strips the trailing slash, if present.
    # Thus we always get the last component of the path, even for directories.
    sep = os.path.sep + (os.path.altsep or '')
    return os.path.basename(path.rstrip(sep))

def move(src, dst):
    """Recursively move a file or directory to another location. This is
    similar to the Unix "mv" command. Return the file or directory's
    destination.

    If the destination is a directory or a symlink to a directory, the source
    is moved inside the directory. The destination path must not already
    exist.

    If the destination already exists but is not a directory, it may be
    overwritten depending on os.rename() semantics.

    If the destination is on our current filesystem, then rename() is used.
    Otherwise, src is copied to the destination and then removed. Symlinks are
    recreated under the new name if os.rename() fails because of cross
    filesystem renames.

    A lot more could be done here...  A look at a mv.c shows a lot of
    the issues this implementation glosses over.

    """
    real_dst = dst
    if os.path.isdir(dst):
        if _samefile(src, dst):
            # We might be on a case insensitive filesystem,
            # perform the rename anyway.
            os.rename(src, dst)
            return

        real_dst = os.path.join(dst, _basename(src))
        if os.path.exists(real_dst):
            raise Error("Destination path '%s' already exists" % real_dst)
    try:
        os.rename(src, real_dst)
    except OSError:
        if os.path.isdir(src):                                                  ###
            if _destinsrc(src, dst):
                raise Error("Cannot move a directory '%s' into itself '%s'." % (src, dst))
            copytree(src, real_dst, symlinks=True)
            rmtree(src)
        else:
            copy2(src, real_dst)
            os.unlink(src)
    return real_dst

def _destinsrc(src, dst):
    src = abspath(src)
    dst = abspath(dst)
    if not src.endswith(os.path.sep):
        src += os.path.sep
    if not dst.endswith(os.path.sep):
        dst += os.path.sep
    return dst.startswith(src)

