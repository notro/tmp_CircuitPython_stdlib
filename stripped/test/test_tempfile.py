# tempfile.py unit tests.
import tempfile
import errno
import io
import os
import sys
import re
import contextlib

import unittest
from test import support                                                        ###


if hasattr(os, 'stat'):
    import stat
    has_stat = 1
else:
    has_stat = 0


TEST_FILES = 10                                                                 ###

# This is organized as one test for each chunk of code in tempfile.py,
# in order of their appearance in the file.  Testing which requires
# threads is not done here.

# Common functionality.
class BaseTestCase(unittest.TestCase):

    str_check = re.compile(r"^[a-z0-9_-]+$")                                    ###



    def nameCheck(self, name, dir, pre, suf):
        (ndir, nbase) = os.path.split(name)
        npre  = nbase[:len(pre)]
        nsuf  = nbase[len(nbase)-len(suf):]

        # check for equality of the absolute paths!
        self.assertEqual(os.path.abspath(ndir), os.path.abspath(dir),
                         "file '%s' not in directory '%s'" % (name, dir))
        self.assertEqual(npre, pre,
                         "file '%s' does not begin with '%s'" % (nbase, pre))
        self.assertEqual(nsuf, suf,
                         "file '%s' does not end with '%s'" % (nbase, suf))

        nbase = nbase[len(pre):len(nbase)-len(suf)]
        self.assertTrue(self.str_check.match(nbase),
                     "random string '%s' does not match ^[a-z0-9_-]{8}$"
                     % nbase)
        self.assertEqual(len(nbase), 8)                                         ###




class TestRandomNameSequence(BaseTestCase):
    """Test the internal iterator object _RandomNameSequence."""

    def setUp(self):
        self.r = tempfile._RandomNameSequence()

    def test_get_six_char_str(self):
        # _RandomNameSequence returns a six-character string
        s = next(self.r)
        self.nameCheck(s, '', '', '')

    def test_many(self):
        # _RandomNameSequence returns no duplicate strings (stochastic)

        dict = {}
        r = self.r
        for i in range(TEST_FILES):
            s = next(r)
            self.nameCheck(s, '', '', '')
            self.assertNotIn(s, dict)
            dict[s] = 1

    def supports_iter(self):
        # _RandomNameSequence supports the iterator protocol

        i = 0
        r = self.r
        for s in r:
            i += 1
            if i == 20:
                break




class TestCandidateTempdirList(BaseTestCase):
    """Test the internal function _candidate_tempdir_list."""

    def test_nonempty_list(self):
        # _candidate_tempdir_list returns a nonempty list of strings

        cand = tempfile._candidate_tempdir_list()

        self.assertFalse(len(cand) == 0)
        for c in cand:
            self.assertIsInstance(c, str)



# We test _get_default_tempdir some more by testing gettempdir.



class TestGetCandidateNames(BaseTestCase):
    """Test the internal function _get_candidate_names."""

    def test_retval(self):
        # _get_candidate_names returns a _RandomNameSequence object
        obj = tempfile._get_candidate_names()
        self.assertIsInstance(obj, tempfile._RandomNameSequence)

    def test_same_thing(self):
        # _get_candidate_names always returns the same object
        a = tempfile._get_candidate_names()
        b = tempfile._get_candidate_names()

        self.assertTrue(a is b)


@contextlib.contextmanager
def _inside_empty_temp_dir():
    dir = tempfile.mkdtemp()
    try:
        with support.swap_attr(tempfile, 'tempdir', dir):
            yield
    finally:
        support.rmtree(dir)


def _mock_candidate_names(*names):
    return support.swap_attr(tempfile,
                             '_get_candidate_names',
                             lambda: iter(names))




class TestGetTempPrefix(BaseTestCase):
    """Test gettempprefix()."""

    def test_sane_template(self):
        # gettempprefix returns a nonempty prefix string
        p = tempfile.gettempprefix()

        self.assertIsInstance(p, str)
        self.assertTrue(len(p) > 0)

    def test_usable_template(self):
        # gettempprefix returns a usable prefix string

        # Create a temp directory, avoiding use of the prefix.
        # Then attempt to create a file whose name is
        # prefix + 'xxxxxx.xxx' in that directory.
        p = tempfile.gettempprefix() + "xxxxxx.xxx"
        d = tempfile.mkdtemp(prefix="")
        try:
            p = os.path.join(d, p)
            with open(p, 'w'): pass                                             ###
            os.unlink(p)
        finally:
            os.rmdir(d)


class TestGetTempDir(BaseTestCase):
    """Test gettempdir()."""

    def test_directory_exists(self):
        # gettempdir returns a directory which exists

        dir = tempfile.gettempdir()
        self.assertTrue(os.path.isabs(dir) or dir == os.curdir,
                     "%s is not an absolute path" % dir)
        self.assertTrue(os.path.isdir(dir),
                     "%s is not a directory" % dir)


    def test_same_thing(self):
        # gettempdir always returns the same object
        a = tempfile.gettempdir()
        b = tempfile.gettempdir()

        self.assertTrue(a is b)





class TestMkdtemp(BaseTestCase):                                                ###
    """Test mkdtemp()."""

    def make_temp(self):
        return tempfile.mkdtemp()

    def do_create(self, dir=None, pre="", suf=""):
        if dir is None:
            dir = tempfile.gettempdir()
        name = tempfile.mkdtemp(dir=dir, prefix=pre, suffix=suf)

        try:
            self.nameCheck(name, dir, pre, suf)
            return name
        except:
            os.rmdir(name)
            raise

    def test_basic(self):
        # mkdtemp can create directories
        os.rmdir(self.do_create())
        os.rmdir(self.do_create(pre="a"))
        os.rmdir(self.do_create(suf="b"))
        os.rmdir(self.do_create(pre="a", suf="b"))
        os.rmdir(self.do_create(pre="aa", suf=".txt"))

    def test_basic_many(self):
        # mkdtemp can create many directories (stochastic)
        extant = list(range(TEST_FILES))
        try:
            for i in extant:
                extant[i] = self.do_create(pre="aa")
        finally:
            for i in extant:
                if(isinstance(i, str)):
                    os.rmdir(i)

    def test_choose_directory(self):
        # mkdtemp can create directories in a user-selected directory
        dir = tempfile.mkdtemp()
        try:
            os.rmdir(self.do_create(dir=dir))
        finally:
            os.rmdir(dir)


    def test_collision_with_existing_directory(self):
        # mkdtemp tries another name when a directory with
        # the chosen name already exists
        with _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            dir1 = tempfile.mkdtemp()
            self.assertTrue(dir1.endswith('aaa'))
            dir2 = tempfile.mkdtemp()
            self.assertTrue(dir2.endswith('bbb'))


class TestMktemp(BaseTestCase):
    """Test mktemp()."""

    # For safety, all use of mktemp must occur in a private directory.
    # We must also suppress the RuntimeWarning it generates.
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.dir:
            os.rmdir(self.dir)
            self.dir = None

    class mktemped:

        def __init__(self, dir, pre, suf):
            self.name = tempfile.mktemp(dir=dir, prefix=pre, suffix=suf)
            with open(self.name, 'wb'): pass                                    ###


    def do_create(self, pre="", suf=""):
        file = self.mktemped(self.dir, pre, suf)

        self.nameCheck(file.name, self.dir, pre, suf)
        os.unlink(file.name)                                                    ###
        return file

    def test_basic(self):
        # mktemp can choose usable file names
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    def test_many(self):
        # mktemp can choose many usable file names (stochastic)
        extant = list(range(TEST_FILES))
        for i in extant:
            extant[i] = self.do_create(pre="aa")

##     def test_warning(self):
##         # mktemp issues a warning when used
##         warnings.filterwarnings("error",
##                                 category=RuntimeWarning,
##                                 message="mktemp")
##         self.assertRaises(RuntimeWarning,
##                           tempfile.mktemp, dir=self.dir)


# We test _TemporaryFileWrapper by testing NamedTemporaryFile.


