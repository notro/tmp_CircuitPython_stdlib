import os
import io

import unittest
import tarfile

from test import support

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarname = support.findfile("testtar.tar")
tmpname = os.path.join(TEMPDIR, "tmp.tar")

################################################################################
#class CommandLineTest(unittest.TestCase):
#
#    def tarfilecmd(self, *args, **kwargs):
#        rc, out, err = script_helper.assert_python_ok('-m', 'tarfile', *args,
#                                                      **kwargs)
#        return out.replace(os.linesep.encode(), b'\n')
#
#    def tarfilecmd_failure(self, *args):
#        return script_helper.assert_python_failure('-m', 'tarfile', *args)
#
#    def make_simple_tarfile(self, tar_name):
#        files = [support.findfile('tokenize_tests.txt'),
#                 support.findfile('tokenize_tests-no-coding-cookie-'
#                                  'and-utf8-bom-sig-only.txt')]
#        self.addCleanup(support.unlink, tar_name)
#        with tarfile.open(tar_name, 'w') as tf:
#            for tardata in files:
#                tf.add(tardata, arcname=os.path.basename(tardata))
#
#    def test_test_command(self):
#        for tar_name in testtarnames:
#            for opt in '-t', '--test':
#                out = self.tarfilecmd(opt, tar_name)
#                self.assertEqual(out, b'')
#
#    def test_test_command_verbose(self):
#        for tar_name in testtarnames:
#            for opt in '-v', '--verbose':
#                out = self.tarfilecmd(opt, '-t', tar_name)
#                self.assertIn(b'is a tar archive.\n', out)
#
#    def test_test_command_invalid_file(self):
#        zipname = support.findfile('zipdir.zip')
#        rc, out, err = self.tarfilecmd_failure('-t', zipname)
#        self.assertIn(b' is not a tar archive.', err)
#        self.assertEqual(out, b'')
#        self.assertEqual(rc, 1)
#
#        for tar_name in testtarnames:
#            with self.subTest(tar_name=tar_name):
#                with open(tar_name, 'rb') as f:
#                    data = f.read()
#                try:
#                    with open(tmpname, 'wb') as f:
#                        f.write(data[:511])
#                    rc, out, err = self.tarfilecmd_failure('-t', tmpname)
#                    self.assertEqual(out, b'')
#                    self.assertEqual(rc, 1)
#                finally:
#                    support.unlink(tmpname)
#
#    def test_list_command(self):
#        for tar_name in testtarnames:
#            with support.captured_stdout() as t:
#                with tarfile.open(tar_name, 'r') as tf:
#                    tf.list(verbose=False)
#            expected = t.getvalue().encode('ascii', 'backslashreplace')
#            for opt in '-l', '--list':
#                out = self.tarfilecmd(opt, tar_name,
#                                      PYTHONIOENCODING='ascii')
#                self.assertEqual(out, expected)
#
#    def test_list_command_verbose(self):
#        for tar_name in testtarnames:
#            with support.captured_stdout() as t:
#                with tarfile.open(tar_name, 'r') as tf:
#                    tf.list(verbose=True)
#            expected = t.getvalue().encode('ascii', 'backslashreplace')
#            for opt in '-v', '--verbose':
#                out = self.tarfilecmd(opt, '-l', tar_name,
#                                      PYTHONIOENCODING='ascii')
#                self.assertEqual(out, expected)
#
#    def test_list_command_invalid_file(self):
#        zipname = support.findfile('zipdir.zip')
#        rc, out, err = self.tarfilecmd_failure('-l', zipname)
#        self.assertIn(b' is not a tar archive.', err)
#        self.assertEqual(out, b'')
#        self.assertEqual(rc, 1)
#
#    def test_create_command(self):
#        files = [support.findfile('tokenize_tests.txt'),
#                 support.findfile('tokenize_tests-no-coding-cookie-'
#                                  'and-utf8-bom-sig-only.txt')]
#        for opt in '-c', '--create':
#            try:
#                out = self.tarfilecmd(opt, tmpname, *files)
#                self.assertEqual(out, b'')
#                with tarfile.open(tmpname) as tar:
#                    tar.getmembers()
#            finally:
#                support.unlink(tmpname)
#
#    def test_create_command_verbose(self):
#        files = [support.findfile('tokenize_tests.txt'),
#                 support.findfile('tokenize_tests-no-coding-cookie-'
#                                  'and-utf8-bom-sig-only.txt')]
#        for opt in '-v', '--verbose':
#            try:
#                out = self.tarfilecmd(opt, '-c', tmpname, *files)
#                self.assertIn(b' file created.', out)
#                with tarfile.open(tmpname) as tar:
#                    tar.getmembers()
#            finally:
#                support.unlink(tmpname)
#
#    def test_create_command_dotless_filename(self):
#        files = [support.findfile('tokenize_tests.txt')]
#        try:
#            out = self.tarfilecmd('-c', dotlessname, *files)
#            self.assertEqual(out, b'')
#            with tarfile.open(dotlessname) as tar:
#                tar.getmembers()
#        finally:
#            support.unlink(dotlessname)
#
#    def test_create_command_dot_started_filename(self):
#        tar_name = os.path.join(TEMPDIR, ".testtar")
#        files = [support.findfile('tokenize_tests.txt')]
#        try:
#            out = self.tarfilecmd('-c', tar_name, *files)
#            self.assertEqual(out, b'')
#            with tarfile.open(tar_name) as tar:
#                tar.getmembers()
#        finally:
#            support.unlink(tar_name)
#
#    def test_create_command_compressed(self):
#        files = [support.findfile('tokenize_tests.txt'),
#                 support.findfile('tokenize_tests-no-coding-cookie-'
#                                  'and-utf8-bom-sig-only.txt')]
#        for filetype in (GzipTest, Bz2Test, LzmaTest):
#            if not filetype.open:
#                continue
#            try:
#                tar_name = tmpname + '.' + filetype.suffix
#                out = self.tarfilecmd('-c', tar_name, *files)
#                with filetype.taropen(tar_name) as tar:
#                    tar.getmembers()
#            finally:
#                support.unlink(tar_name)
#
#    def test_extract_command(self):
#        self.make_simple_tarfile(tmpname)
#        for opt in '-e', '--extract':
#            try:
#                with support.temp_cwd(tarextdir):
#                    out = self.tarfilecmd(opt, tmpname)
#                self.assertEqual(out, b'')
#            finally:
#                support.rmtree(tarextdir)
#
#    def test_extract_command_verbose(self):
#        self.make_simple_tarfile(tmpname)
#        for opt in '-v', '--verbose':
#            try:
#                with support.temp_cwd(tarextdir):
#                    out = self.tarfilecmd(opt, '-e', tmpname)
#                self.assertIn(b' file is extracted.', out)
#            finally:
#                support.rmtree(tarextdir)
#
#    def test_extract_command_different_directory(self):
#        self.make_simple_tarfile(tmpname)
#        try:
#            with support.temp_cwd(tarextdir):
#                out = self.tarfilecmd('-e', tmpname, 'spamdir')
#            self.assertEqual(out, b'')
#        finally:
#            support.rmtree(tarextdir)
#
#    def test_extract_command_invalid_file(self):
#        zipname = support.findfile('zipdir.zip')
#        with support.temp_cwd(tarextdir):
#            rc, out, err = self.tarfilecmd_failure('-e', zipname)
#        self.assertIn(b' is not a tar archive.', err)
#        self.assertEqual(out, b'')
#        self.assertEqual(rc, 1)
#
#
class ContextManagerTest(unittest.TestCase):

    def test_basic(self):
        with tarfile.open(tarname) as tar:
            self.assertFalse(tar.closed, "closed inside runtime context")
        self.assertTrue(tar.closed, "context manager failed")

    def test_closed(self):
        # The __enter__() method is supposed to raise OSError
        # if the TarFile object is already closed.
        tar = tarfile.open(tarname)
        tar.close()
        with self.assertRaises(OSError):
            with tar:
                pass

    def test_exception(self):
        # Test if the OSError exception is passed through properly.
        with self.assertRaises(Exception) as exc:
            with tarfile.open(tarname) as tar:
                raise OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception raised in context manager")
        self.assertTrue(tar.closed, "context manager failed")

    def test_no_eof(self):
        # __exit__() must not write end-of-archive blocks if an
        # exception was raised.
        try:
            with tarfile.open(tmpname, "w") as tar:
                raise Exception
        except:
            pass
        self.assertEqual(os.path.getsize(tmpname), 0,
                "context manager wrote an end-of-archive block")
        self.assertTrue(tar.closed, "context manager failed")

    def test_eof(self):
        # __exit__() must write end-of-archive blocks, i.e. call
        # TarFile.close() if there was no error.
        with tarfile.open(tmpname, "w"):
            pass
        self.assertNotEqual(os.path.getsize(tmpname), 0,
                "context manager wrote no end-of-archive block")

#    def test_fileobj(self):
#        # Test that __exit__() did not close the external file
#        # object.
#        with open(tmpname, "wb") as fobj:
#            try:
#                with tarfile.open(fileobj=fobj, mode="w") as tar:
#                    raise Exception
#            except:
#                pass
#            self.assertFalse(fobj.closed, "external file object was closed")
#            self.assertTrue(tar.closed, "context manager failed")
#

#@unittest.skipIf(hasattr(os, "link"), "requires os.link to be missing")
#class LinkEmulationTest(ReadTest, unittest.TestCase):
#
#    # Test for issue #8741 regression. On platforms that do not support
#    # symbolic or hard links tarfile tries to extract these types of members
#    # as the regular files they point to.
#    def _test_link_extraction(self, name):
#        self.tar.extract(name, TEMPDIR)
#        with open(os.path.join(TEMPDIR, name), "rb") as f:
#            data = f.read()
#        self.assertEqual(md5sum(data), md5_regtype)
#
#    # See issues #1578269, #8879, and #17689 for some history on these skips
#    @unittest.skipIf(hasattr(os.path, "islink"),
#                     "Skip emulation - has os.path.islink but not os.link")
#    def test_hardlink_extraction1(self):
#        self._test_link_extraction("ustar/lnktype")
#
#    @unittest.skipIf(hasattr(os.path, "islink"),
#                     "Skip emulation - has os.path.islink but not os.link")
#    def test_hardlink_extraction2(self):
#        self._test_link_extraction("./ustar/linktest2/lnktype")
#
#    @unittest.skipIf(hasattr(os, "symlink"),
#                     "Skip emulation if symlink exists")
#    def test_symlink_extraction1(self):
#        self._test_link_extraction("ustar/symtype")
#
#    @unittest.skipIf(hasattr(os, "symlink"),
#                     "Skip emulation if symlink exists")
#    def test_symlink_extraction2(self):
#        self._test_link_extraction("./ustar/linktest2/symtype")
#
#
#class Bz2PartialReadTest(Bz2Test, unittest.TestCase):
#    # Issue5068: The _BZ2Proxy.read() method loops forever
#    # on an empty or partial bzipped file.
#
#    def _test_partial_input(self, mode):
#        class MyBytesIO(io.BytesIO):
#            hit_eof = False
#            def read(self, n):
#                if self.hit_eof:
#                    raise AssertionError("infinite loop detected in "
#                                         "tarfile.open()")
#                self.hit_eof = self.tell() == len(self.getvalue())
#                return super(MyBytesIO, self).read(n)
#            def seek(self, *args):
#                self.hit_eof = False
#                return super(MyBytesIO, self).seek(*args)
#
#        data = bz2.compress(tarfile.TarInfo("foo").tobuf())
#        for x in range(len(data) + 1):
#            try:
#                tarfile.open(fileobj=MyBytesIO(data[:x]), mode=mode)
#            except tarfile.ReadError:
#                pass # we have no interest in ReadErrors
#
#    def test_partial_input(self):
#        self._test_partial_input("r")
#
#    def test_partial_input_bz2(self):
#        self._test_partial_input("r:bz2")
#

def setUpModule():
    tearDownModule()                                                            ### Might run out of memory and this wasn't called
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)
#
#    global testtarnames
#    testtarnames = [tarname]
#    with open(tarname, "rb") as fobj:
#        data = fobj.read()
#
#    # Create compressed tarfiles.
#    for c in GzipTest, Bz2Test, LzmaTest:
#        if c.open:
#            support.unlink(c.tarname)
#            testtarnames.append(c.tarname)
#            with c.open(c.tarname, "wb") as tar:
#                tar.write(data)

def tearDownModule():
    if os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)

#if __name__ == "__main__":
#    unittest.main()
