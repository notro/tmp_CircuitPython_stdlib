# Due to memory reason test_logging.py had to be split up

import logging
import logging.handlers
#import datetime
import io
#import gc
import os
import re
import sys
import tempfile
from test.support import (patch, swap_attr)
import time
import unittest

# BaseTest is copied wholesale from test_logging.py
class BaseTest(unittest.TestCase):

    """Base class for logging tests."""

    log_format = "%(name)s -> %(levelname)s: %(message)s"
#    expected_log_pat = r"^([\w.]+) -> (\w+): (\d+)$"
    expected_log_pat = r"^(.+) -> (\w+): (\d+)$"
    message_num = 0

    def setUp(self):
        """Setup the default logging stream to an internal StringIO instance,
        so that we can examine log output as we want."""
        logger_dict = logging.getLogger().manager.loggerDict
#        logging._acquireLock()
        try:
#            self.saved_handlers = logging._handlers.copy()
#            self.saved_handler_list = logging._handlerList[:]
            self.saved_loggers = saved_loggers = logger_dict.copy()
            self.saved_name_to_level = logging._nameToLevel.copy()
            self.saved_level_to_name = logging._levelToName.copy()
            self.logger_states = logger_states = {}
            for name in saved_loggers:
                logger_states[name] = getattr(saved_loggers[name],
                                              'disabled', None)
        finally:
#            logging._releaseLock()
            pass                                                                ###

        # Set two unused loggers
        self.logger1 = logging.getLogger("\xab\xd7\xbb")
        self.logger2 = logging.getLogger("\u013f\u00d6\u0047")

        self.root_logger = logging.getLogger("")
        self.original_logging_level = self.root_logger.getEffectiveLevel()

        self.stream = io.StringIO()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_hdlr = logging.StreamHandler(self.stream)
        self.root_formatter = logging.Formatter(self.log_format)
        self.root_hdlr.setFormatter(self.root_formatter)
        if self.logger1.hasHandlers():
            hlist = self.logger1.handlers + self.root_logger.handlers
            raise AssertionError('Unexpected handlers: %s' % hlist)
        if self.logger2.hasHandlers():
            hlist = self.logger2.handlers + self.root_logger.handlers
            raise AssertionError('Unexpected handlers: %s' % hlist)
        self.root_logger.addHandler(self.root_hdlr)
        self.assertTrue(self.logger1.hasHandlers())
        self.assertTrue(self.logger2.hasHandlers())

    def tearDown(self):
        """Remove our logging stream, and restore the original logging
        level."""
        self.stream.close()
        self.root_logger.removeHandler(self.root_hdlr)
        while self.root_logger.handlers:
            h = self.root_logger.handlers[0]
            self.root_logger.removeHandler(h)
            h.close()
        self.root_logger.setLevel(self.original_logging_level)
#        logging._acquireLock()
        try:
            logging._levelToName.clear()
            logging._levelToName.update(self.saved_level_to_name)
            logging._nameToLevel.clear()
            logging._nameToLevel.update(self.saved_name_to_level)
#            logging._handlers.clear()
#            logging._handlers.update(self.saved_handlers)
#            logging._handlerList[:] = self.saved_handler_list
            loggerDict = logging.getLogger().manager.loggerDict
            loggerDict.clear()
            loggerDict.update(self.saved_loggers)
            logger_states = self.logger_states
            for name in self.logger_states:
                if logger_states[name] is not None:
                    self.saved_loggers[name].disabled = logger_states[name]
        finally:
#            logging._releaseLock()
            pass                                                                ###

    def assert_log_lines(self, expected_values, stream=None, pat=None):
        """Match the collected log lines against the regular expression
        self.expected_log_pat, and compare the extracted group values to
        the expected_values list of tuples."""
        stream = stream or self.stream
        pat = re.compile(pat or self.expected_log_pat)
        actual_lines = stream.getvalue().splitlines()
        self.assertEqual(len(actual_lines), len(expected_values))
        for actual, expected in zip(actual_lines, expected_values):
            match = pat.search(actual)
            if not match:
                self.fail("Log line does not match expected pattern:\n" +
                            actual)
            groups = []                                                         ### ure's match object doesn't have groups()
            try:                                                                ###
                for i in range(1, 10):                                          ###
                    groups.append(match.group(i))                               ###
            except IndexError:                                                  ###
                pass                                                            ###
#            self.assertEqual(tuple(match.groups()), expected)
            self.assertEqual(tuple(groups), expected)                           ###
        s = stream.read()
        if s:
            self.fail("Remaining output at end of log stream:\n" + s)

    def next_message(self):
        """Generate a message consisting solely of an auto-incrementing
        integer."""
        self.message_num += 1
        return "%d" % self.message_num


class RecordingHandler(logging.NullHandler):

    def __init__(self, *args, **kwargs):
        super(RecordingHandler, self).__init__(*args, **kwargs)
        self.records = []

    def handle(self, record):
        """Keep track of all the emitted records."""
        self.records.append(record)


# This line delimiter and the next one marks the code that was cut out from test_logging.py
# ----------------------------------------------------------------------------------------------------------------------
class LogRecordTest(BaseTest):
    def test_str_rep(self):
        r = logging.makeLogRecord({})
        s = str(r)
        self.assertTrue(s.startswith('<LogRecord: '))
        self.assertTrue(s.endswith('>'))

    def test_dict_arg(self):
        h = RecordingHandler()
        r = logging.getLogger()
        r.addHandler(h)
        d = {'less' : 'more' }
        logging.warning('less is %(less)s', d)
        self.assertIs(h.records[0].args, d)
        self.assertEqual(h.records[0].message, 'less is more')
        r.removeHandler(h)
        h.close()

#    def test_multiprocessing(self):
#        r = logging.makeLogRecord({})
#        self.assertEqual(r.processName, 'MainProcess')
#        try:
#            import multiprocessing as mp
#            r = logging.makeLogRecord({})
#            self.assertEqual(r.processName, mp.current_process().name)
#        except ImportError:
#            pass
#
#    def test_optional(self):
#        r = logging.makeLogRecord({})
#        NOT_NONE = self.assertIsNotNone
#        if threading:
#            NOT_NONE(r.thread)
#            NOT_NONE(r.threadName)
#        NOT_NONE(r.process)
#        NOT_NONE(r.processName)
#        log_threads = logging.logThreads
#        log_processes = logging.logProcesses
#        log_multiprocessing = logging.logMultiprocessing
#        try:
#            logging.logThreads = False
#            logging.logProcesses = False
#            logging.logMultiprocessing = False
#            r = logging.makeLogRecord({})
#            NONE = self.assertIsNone
#            NONE(r.thread)
#            NONE(r.threadName)
#            NONE(r.process)
#            NONE(r.processName)
#        finally:
#            logging.logThreads = log_threads
#            logging.logProcesses = log_processes
#            logging.logMultiprocessing = log_multiprocessing
#
class BasicConfigTest(unittest.TestCase):

    """Test suite for logging.basicConfig."""

    def setUp(self):
        super(BasicConfigTest, self).setUp()
        self.handlers = logging.root.handlers
#        self.saved_handlers = logging._handlers.copy()
#        self.saved_handler_list = logging._handlerList[:]
        self.original_logging_level = logging.root.level
        self.addCleanup(self.cleanup)
        logging.root.handlers = []

    def tearDown(self):
        for h in logging.root.handlers[:]:
            logging.root.removeHandler(h)
            h.close()
        super(BasicConfigTest, self).tearDown()

    def cleanup(self):
        setattr(logging.root, 'handlers', self.handlers)
#        logging._handlers.clear()
#        logging._handlers.update(self.saved_handlers)
#        logging._handlerList[:] = self.saved_handler_list
        logging.root.level = self.original_logging_level

    def test_no_kwargs(self):
        logging.basicConfig()

        # handler defaults to a StreamHandler to sys.stderr
        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.stream, sys.stderr)

        formatter = handler.formatter
        # format defaults to logging.BASIC_FORMAT
        self.assertEqual(formatter._style._fmt, logging.BASIC_FORMAT)
        # datefmt defaults to None
        self.assertIsNone(formatter.datefmt)
        # style defaults to %
        self.assertIsInstance(formatter._style, logging.PercentStyle)

        # level is not explicitly set
        self.assertEqual(logging.root.level, self.original_logging_level)

#    def test_strformatstyle(self):
#        with captured_stdout() as output:
#            logging.basicConfig(stream=sys.stdout, style="{")
#            logging.error("Log an error")
#            sys.stdout.seek(0)
#            self.assertEqual(output.getvalue().strip(),
#                "ERROR:root:Log an error")
#
#    def test_stringtemplatestyle(self):
#        with captured_stdout() as output:
#            logging.basicConfig(stream=sys.stdout, style="$")
#            logging.error("Log an error")
#            sys.stdout.seek(0)
#            self.assertEqual(output.getvalue().strip(),
#                "ERROR:root:Log an error")
#
    def test_filename(self):

        def cleanup(h1, h2, fn):
            h1.close()
            h2.close()
            os.remove(fn)

        logging.basicConfig(filename='test.log')

        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.FileHandler)

        expected = logging.FileHandler('test.log', 'a')
#        self.assertEqual(handler.stream.mode, expected.stream.mode)
#        self.assertEqual(handler.stream.name, expected.stream.name)
        self.addCleanup(cleanup, handler, expected, 'test.log')

    def test_filemode(self):

        def cleanup(h1, h2, fn):
            h1.close()
            h2.close()
            os.remove(fn)

        logging.basicConfig(filename='test.log', filemode='wb')

        handler = logging.root.handlers[0]
        expected = logging.FileHandler('test.log', 'wb')
#        self.assertEqual(handler.stream.mode, expected.stream.mode)
        self.addCleanup(cleanup, handler, expected, 'test.log')

    def test_stream(self):
        stream = io.StringIO()
        self.addCleanup(stream.close)
        logging.basicConfig(stream=stream)

        self.assertEqual(len(logging.root.handlers), 1)
        handler = logging.root.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.stream, stream)

    def test_format(self):
        logging.basicConfig(format='foo')

        formatter = logging.root.handlers[0].formatter
        self.assertEqual(formatter._style._fmt, 'foo')

    def test_datefmt(self):
        logging.basicConfig(datefmt='bar')

        formatter = logging.root.handlers[0].formatter
        self.assertEqual(formatter.datefmt, 'bar')

#    def test_style(self):
#        logging.basicConfig(style='$')
#
#        formatter = logging.root.handlers[0].formatter
#        self.assertIsInstance(formatter._style, logging.StringTemplateStyle)
#
    def test_level(self):
        old_level = logging.root.level
        self.addCleanup(logging.root.setLevel, old_level)

        logging.basicConfig(level=57)
        self.assertEqual(logging.root.level, 57)
        # Test that second call has no effect
        logging.basicConfig(level=58)
        self.assertEqual(logging.root.level, 57)

    def test_incompatible(self):
        assertRaises = self.assertRaises
        handlers = [logging.StreamHandler()]
        stream = sys.stderr
        assertRaises(ValueError, logging.basicConfig, filename='test.log',
                                                     stream=stream)
        assertRaises(ValueError, logging.basicConfig, filename='test.log',
                                                     handlers=handlers)
        assertRaises(ValueError, logging.basicConfig, stream=stream,
                                                     handlers=handlers)
        # Issue 23207: test for invalid kwargs
        assertRaises(ValueError, logging.basicConfig, loglevel=logging.INFO)
        # Should pop both filename and filemode even if filename is None
        logging.basicConfig(filename=None, filemode='a')

    def test_handlers(self):
        handlers = [
            logging.StreamHandler(),
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(),
        ]
        f = logging.Formatter()
        handlers[2].setFormatter(f)
        logging.basicConfig(handlers=handlers)
        self.assertIs(handlers[0], logging.root.handlers[0])
        self.assertIs(handlers[1], logging.root.handlers[1])
        self.assertIs(handlers[2], logging.root.handlers[2])
        self.assertIsNotNone(handlers[0].formatter)
        self.assertIsNotNone(handlers[1].formatter)
        self.assertIs(handlers[2].formatter, f)
        self.assertIs(handlers[0].formatter, handlers[1].formatter)

    def _test_log(self, method, level=None):
        # logging.root has no handlers so basicConfig should be called
        called = []

        old_basic_config = logging.basicConfig
        def my_basic_config(*a, **kw):
            old_basic_config()
            old_level = logging.root.level
            logging.root.setLevel(100)  # avoid having messages in stderr
            self.addCleanup(logging.root.setLevel, old_level)
            called.append((a, kw))

        patch(self, logging, 'basicConfig', my_basic_config)

        log_method = getattr(logging, method)
        if level is not None:
            log_method(level, "test me")
        else:
            log_method("test me")

        # basicConfig was called with no arguments
        self.assertEqual(called, [((), {})])

    def test_log(self):
        self._test_log('log', logging.WARNING)

    def test_debug(self):
        self._test_log('debug')

    def test_info(self):
        self._test_log('info')

    def test_warning(self):
        self._test_log('warning')

    def test_error(self):
        self._test_log('error')

    def test_critical(self):
        self._test_log('critical')


class LoggerAdapterTest(unittest.TestCase):

    def setUp(self):
        super(LoggerAdapterTest, self).setUp()
#        old_handler_list = logging._handlerList[:]

        self.recording = RecordingHandler()
        self.logger = logging.root
        self.logger.addHandler(self.recording)
        self.addCleanup(self.logger.removeHandler, self.recording)
        self.addCleanup(self.recording.close)

#        def cleanup():
#            logging._handlerList[:] = old_handler_list
#
#        self.addCleanup(cleanup)
#        self.addCleanup(logging.shutdown)
        self.adapter = logging.LoggerAdapter(logger=self.logger, extra=None)

    def test_exception(self):
        msg = 'testing exception: %r'
        exc = None
        try:
            1 / 0
        except ZeroDivisionError as e:
            exc = e
            self.adapter.exception(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.ERROR)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))
#        self.assertEqual(record.exc_info,
#                         (exc.__class__, exc, exc.__traceback__))
        self.assertEqual(record.exc_info[:2], (exc.__class__, exc))             ###

    def test_critical(self):
        msg = 'critical test! %r'
        self.adapter.critical(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.CRITICAL)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))

    def test_is_enabled_for(self):
        old_disable = self.adapter.logger.manager.disable
        self.adapter.logger.manager.disable = 33
        self.addCleanup(setattr, self.adapter.logger.manager, 'disable',
                        old_disable)
        self.assertFalse(self.adapter.isEnabledFor(32))

    def test_has_handlers(self):
        self.assertTrue(self.adapter.hasHandlers())

        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        self.assertFalse(self.logger.hasHandlers())
        self.assertFalse(self.adapter.hasHandlers())


class LoggerTest(BaseTest):

    def setUp(self):
        super(LoggerTest, self).setUp()
        self.recording = RecordingHandler()
        self.logger = logging.Logger(name='blah')
        self.logger.addHandler(self.recording)
        self.addCleanup(self.logger.removeHandler, self.recording)
        self.addCleanup(self.recording.close)
#        self.addCleanup(logging.shutdown)

    def test_set_invalid_level(self):
        self.assertRaises(TypeError, self.logger.setLevel, object())

    def test_exception(self):
        msg = 'testing exception: %r'
        exc = None
        try:
            1 / 0
        except ZeroDivisionError as e:
            exc = e
            self.logger.exception(msg, self.recording)

        self.assertEqual(len(self.recording.records), 1)
        record = self.recording.records[0]
        self.assertEqual(record.levelno, logging.ERROR)
        self.assertEqual(record.msg, msg)
        self.assertEqual(record.args, (self.recording,))
#        self.assertEqual(record.exc_info,
#                         (exc.__class__, exc, exc.__traceback__))
        self.assertEqual(record.exc_info[:2], (exc.__class__, exc))             ###

    def test_log_invalid_level_with_raise(self):
        with swap_attr(logging, 'raiseExceptions', True):
            self.assertRaises(TypeError, self.logger.log, '10', 'test message')

    def test_log_invalid_level_no_raise(self):
        with swap_attr(logging, 'raiseExceptions', False):
            self.logger.log('10', 'test message')  # no exception happens

#    def test_find_caller_with_stack_info(self):
#        called = []
#        patch(self, logging.traceback, 'print_stack',
#              lambda f, file: called.append(file.getvalue()))
#
#        self.logger.findCaller(stack_info=True)
#
#        self.assertEqual(len(called), 1)
#        self.assertEqual('Stack (most recent call last):\n', called[0])
#
    def test_make_record_with_extra_overwrite(self):
        name = 'my record'
        level = 13
        fn = lno = msg = args = exc_info = func = sinfo = None
        rv = logging._logRecordFactory(name, level, fn, lno, msg, args,
                                       exc_info, func, sinfo)

        for key in ('message', 'asctime') + tuple(rv.__dict__.keys()):
            extra = {key: 'some value'}
            self.assertRaises(KeyError, self.logger.makeRecord, name, level,
                              fn, lno, msg, args, exc_info,
                              extra=extra, sinfo=sinfo)

    def test_make_record_with_extra_no_overwrite(self):
        name = 'my record'
        level = 13
        fn = lno = msg = args = exc_info = func = sinfo = None
        extra = {'valid_key': 'some value'}
        result = self.logger.makeRecord(name, level, fn, lno, msg, args,
                                        exc_info, extra=extra, sinfo=sinfo)
        self.assertIn('valid_key', result.__dict__)

    def test_has_handlers(self):
        self.assertTrue(self.logger.hasHandlers())

        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.assertFalse(self.logger.hasHandlers())

    def test_has_handlers_no_propagate(self):
        child_logger = logging.getLogger('blah.child')
        child_logger.propagate = False
        self.assertFalse(child_logger.hasHandlers())

    def test_is_enabled_for(self):
        old_disable = self.logger.manager.disable
        self.logger.manager.disable = 23
        self.addCleanup(setattr, self.logger.manager, 'disable', old_disable)
        self.assertFalse(self.logger.isEnabledFor(22))

    def test_root_logger_aliases(self):
        root = logging.getLogger()
        self.assertIs(root, logging.root)
        self.assertIs(root, logging.getLogger(None))
        self.assertIs(root, logging.getLogger(''))
        self.assertIs(root, logging.getLogger('foo').root)
        self.assertIs(root, logging.getLogger('foo.bar').root)
        self.assertIs(root, logging.getLogger('foo').parent)

        self.assertIsNot(root, logging.getLogger('\0'))
        self.assertIsNot(root, logging.getLogger('foo.bar').parent)

    def test_invalid_names(self):
        self.assertRaises(TypeError, logging.getLogger, any)
        self.assertRaises(TypeError, logging.getLogger, b'foo')


class BaseFileTest(BaseTest):
    "Base class for handler tests that write log files"

    def setUp(self):
        BaseTest.setUp(self)
#        fd, self.fn = tempfile.mkstemp(".log", "test_logging-2-")
#        os.close(fd)
        self.fn = tempfile.mktemp(".log", "test_logging-2-")                    ###
        with open(self.fn, 'w'): pass                                           ###
        self.rmfiles = []

    def tearDown(self):
        for fn in self.rmfiles:
            os.unlink(fn)
        if os.path.exists(self.fn):
            os.unlink(self.fn)
        BaseTest.tearDown(self)

    def assertLogFile(self, filename):
        "Assert a log file is there and register it for deletion"
        self.assertTrue(os.path.exists(filename),
                        msg="Log file %r does not exist" % filename)
        self.rmfiles.append(filename)


class FileHandlerTest(BaseFileTest):
    def test_delay(self):
        os.unlink(self.fn)
        fh = logging.FileHandler(self.fn, delay=True)
        self.assertIsNone(fh.stream)
        self.assertFalse(os.path.exists(self.fn))
        fh.handle(logging.makeLogRecord({}))
        self.assertIsNotNone(fh.stream)
        self.assertTrue(os.path.exists(self.fn))
        fh.close()

class RotatingFileHandlerTest(BaseFileTest):
    def next_rec(self):
        return logging.LogRecord('n', logging.DEBUG, 'p', 1,
                                 self.next_message(), None, None, None)

    def test_should_not_rollover(self):
        # If maxbytes is zero rollover never occurs
        rh = logging.handlers.RotatingFileHandler(self.fn, maxBytes=0)
        self.assertFalse(rh.shouldRollover(None))
        rh.close()

    def test_should_rollover(self):
        rh = logging.handlers.RotatingFileHandler(self.fn, maxBytes=1)
        self.assertTrue(rh.shouldRollover(self.next_rec()))
        rh.close()

    def test_file_created(self):
        # checks that the file is created and assumes it was created
        # by us
        rh = logging.handlers.RotatingFileHandler(self.fn)
        rh.emit(self.next_rec())
        self.assertLogFile(self.fn)
        rh.close()

    def test_rollover_filenames(self):
        def namer(name):
            return name + ".test"
        rh = logging.handlers.RotatingFileHandler(
            self.fn, backupCount=2, maxBytes=1)
        rh.namer = namer
        rh.emit(self.next_rec())
        self.assertLogFile(self.fn)
        rh.emit(self.next_rec())
        self.assertLogFile(namer(self.fn + ".1"))
        rh.emit(self.next_rec())
        self.assertLogFile(namer(self.fn + ".2"))
        self.assertFalse(os.path.exists(namer(self.fn + ".3")))
        rh.close()

#    @requires_zlib
#    def test_rotator(self):
#        def namer(name):
#            return name + ".gz"
#
#        def rotator(source, dest):
#            with open(source, "rb") as sf:
#                data = sf.read()
#                compressed = zlib.compress(data, 9)
#                with open(dest, "wb") as df:
#                    df.write(compressed)
#            os.remove(source)
#
#        rh = logging.handlers.RotatingFileHandler(
#            self.fn, backupCount=2, maxBytes=1)
#        rh.rotator = rotator
#        rh.namer = namer
#        m1 = self.next_rec()
#        rh.emit(m1)
#        self.assertLogFile(self.fn)
#        m2 = self.next_rec()
#        rh.emit(m2)
#        fn = namer(self.fn + ".1")
#        self.assertLogFile(fn)
#        newline = os.linesep
#        with open(fn, "rb") as f:
#            compressed = f.read()
#            data = zlib.decompress(compressed)
#            self.assertEqual(data.decode("ascii"), m1.msg + newline)
#        rh.emit(self.next_rec())
#        fn = namer(self.fn + ".2")
#        self.assertLogFile(fn)
#        with open(fn, "rb") as f:
#            compressed = f.read()
#            data = zlib.decompress(compressed)
#            self.assertEqual(data.decode("ascii"), m1.msg + newline)
#        rh.emit(self.next_rec())
#        fn = namer(self.fn + ".2")
#        with open(fn, "rb") as f:
#            compressed = f.read()
#            data = zlib.decompress(compressed)
#            self.assertEqual(data.decode("ascii"), m2.msg + newline)
#        self.assertFalse(os.path.exists(namer(self.fn + ".3")))
#        rh.close()
#
#class TimedRotatingFileHandlerTest(BaseFileTest):
#    # other test methods added below
#    def test_rollover(self):
#        fh = logging.handlers.TimedRotatingFileHandler(self.fn, 'S',
#                                                       backupCount=1)
#        fmt = logging.Formatter('%(asctime)s %(message)s')
#        fh.setFormatter(fmt)
#        r1 = logging.makeLogRecord({'msg': 'testing - initial'})
#        fh.emit(r1)
#        self.assertLogFile(self.fn)
#        time.sleep(1.1)    # a little over a second ...
#        r2 = logging.makeLogRecord({'msg': 'testing - after delay'})
#        fh.emit(r2)
#        fh.close()
#        # At this point, we should have a recent rotated file which we
#        # can test for the existence of. However, in practice, on some
#        # machines which run really slowly, we don't know how far back
#        # in time to go to look for the log file. So, we go back a fair
#        # bit, and stop as soon as we see a rotated file. In theory this
#        # could of course still fail, but the chances are lower.
#        found = False
#        now = datetime.datetime.now()
#        GO_BACK = 5 * 60 # seconds
#        for secs in range(GO_BACK):
#            prev = now - datetime.timedelta(seconds=secs)
#            fn = self.fn + prev.strftime(".%Y-%m-%d_%H-%M-%S")
#            found = os.path.exists(fn)
#            if found:
#                self.rmfiles.append(fn)
#                break
#        msg = 'No rotated files found, went back %d seconds' % GO_BACK
#        if not found:
#            #print additional diagnostics
#            dn, fn = os.path.split(self.fn)
#            files = [f for f in os.listdir(dn) if f.startswith(fn)]
#            print('Test time: %s' % now.strftime("%Y-%m-%d %H-%M-%S"), file=sys.stderr)
#            print('The only matching files are: %s' % files, file=sys.stderr)
#            for f in files:
#                print('Contents of %s:' % f)
#                path = os.path.join(dn, f)
#                with open(path, 'r') as tf:
#                    print(tf.read())
#        self.assertTrue(found, msg=msg)
#
#    def test_invalid(self):
#        assertRaises = self.assertRaises
#        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
#                     self.fn, 'X', delay=True)
#        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
#                     self.fn, 'W', delay=True)
#        assertRaises(ValueError, logging.handlers.TimedRotatingFileHandler,
#                     self.fn, 'W7', delay=True)
#
#    def test_compute_rollover_daily_attime(self):
#        currentTime = 0
#        atTime = datetime.time(12, 0, 0)
#        rh = logging.handlers.TimedRotatingFileHandler(
#            self.fn, when='MIDNIGHT', interval=1, backupCount=0, utc=True,
#            atTime=atTime)
#        try:
#            actual = rh.computeRollover(currentTime)
#            self.assertEqual(actual, currentTime + 12 * 60 * 60)
#
#            actual = rh.computeRollover(currentTime + 13 * 60 * 60)
#            self.assertEqual(actual, currentTime + 36 * 60 * 60)
#        finally:
#            rh.close()
#
#    #@unittest.skipIf(True, 'Temporarily skipped while failures investigated.')
#    def test_compute_rollover_weekly_attime(self):
#        currentTime = int(time.time())
#        today = currentTime - currentTime % 86400
#
#        atTime = datetime.time(12, 0, 0)
#
#        wday = time.gmtime(today).tm_wday
#        for day in range(7):
#            rh = logging.handlers.TimedRotatingFileHandler(
#                self.fn, when='W%d' % day, interval=1, backupCount=0, utc=True,
#                atTime=atTime)
#            try:
#                if wday > day:
#                    # The rollover day has already passed this week, so we
#                    # go over into next week
#                    expected = (7 - wday + day)
#                else:
#                    expected = (day - wday)
#                # At this point expected is in days from now, convert to seconds
#                expected *= 24 * 60 * 60
#                # Add in the rollover time
#                expected += 12 * 60 * 60
#                # Add in adjustment for today
#                expected += today
#                actual = rh.computeRollover(today)
#                if actual != expected:
#                    print('failed in timezone: %d' % time.timezone)
#                    print('local vars: %s' % locals())
#                self.assertEqual(actual, expected)
#                if day == wday:
#                    # goes into following week
#                    expected += 7 * 24 * 60 * 60
#                actual = rh.computeRollover(today + 13 * 60 * 60)
#                if actual != expected:
#                    print('failed in timezone: %d' % time.timezone)
#                    print('local vars: %s' % locals())
#                self.assertEqual(actual, expected)
#            finally:
#                rh.close()
#
#
#def secs(**kw):
#    return datetime.timedelta(**kw) // datetime.timedelta(seconds=1)
#
#for when, exp in (('S', 1),
#                  ('M', 60),
#                  ('H', 60 * 60),
#                  ('D', 60 * 60 * 24),
#                  ('MIDNIGHT', 60 * 60 * 24),
#                  # current time (epoch start) is a Thursday, W0 means Monday
#                  ('W0', secs(days=4, hours=24)),
#                 ):
#    def test_compute_rollover(self, when=when, exp=exp):
#        rh = logging.handlers.TimedRotatingFileHandler(
#            self.fn, when=when, interval=1, backupCount=0, utc=True)
#        currentTime = 0.0
#        actual = rh.computeRollover(currentTime)
#        if exp != actual:
#            # Failures occur on some systems for MIDNIGHT and W0.
#            # Print detailed calculation for MIDNIGHT so we can try to see
#            # what's going on
#            if when == 'MIDNIGHT':
#                try:
#                    if rh.utc:
#                        t = time.gmtime(currentTime)
#                    else:
#                        t = time.localtime(currentTime)
#                    currentHour = t[3]
#                    currentMinute = t[4]
#                    currentSecond = t[5]
#                    # r is the number of seconds left between now and midnight
#                    r = logging.handlers._MIDNIGHT - ((currentHour * 60 +
#                                                       currentMinute) * 60 +
#                            currentSecond)
#                    result = currentTime + r
#                    print('t: %s (%s)' % (t, rh.utc), file=sys.stderr)
#                    print('currentHour: %s' % currentHour, file=sys.stderr)
#                    print('currentMinute: %s' % currentMinute, file=sys.stderr)
#                    print('currentSecond: %s' % currentSecond, file=sys.stderr)
#                    print('r: %s' % r, file=sys.stderr)
#                    print('result: %s' % result, file=sys.stderr)
#                except Exception:
#                    print('exception in diagnostic code: %s' % sys.exc_info()[1], file=sys.stderr)
#        self.assertEqual(exp, actual)
#        rh.close()
#    setattr(TimedRotatingFileHandlerTest, "test_compute_rollover_%s" % when, test_compute_rollover)
#
#
#@unittest.skipUnless(win32evtlog, 'win32evtlog/win32evtlogutil/pywintypes required for this test.')
#class NTEventLogHandlerTest(BaseTest):
#    def test_basic(self):
#        logtype = 'Application'
#        elh = win32evtlog.OpenEventLog(None, logtype)
#        num_recs = win32evtlog.GetNumberOfEventLogRecords(elh)
#
#        try:
#            h = logging.handlers.NTEventLogHandler('test_logging')
#        except pywintypes.error as e:
#            if e.winerror == 5:  # access denied
#                raise unittest.SkipTest('Insufficient privileges to run test')
#            raise
#
#        r = logging.makeLogRecord({'msg': 'Test Log Message'})
#        h.handle(r)
#        h.close()
#        # Now see if the event is recorded
#        self.assertLess(num_recs, win32evtlog.GetNumberOfEventLogRecords(elh))
#        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | \
#                win32evtlog.EVENTLOG_SEQUENTIAL_READ
#        found = False
#        GO_BACK = 100
#        events = win32evtlog.ReadEventLog(elh, flags, GO_BACK)
#        for e in events:
#            if e.SourceName != 'test_logging':
#                continue
#            msg = win32evtlogutil.SafeFormatMessage(e, logtype)
#            if msg != 'Test Log Message\r\n':
#                continue
#            found = True
#            break
#        msg = 'Record not found in event log, went back %d records' % GO_BACK
#        self.assertTrue(found, msg=msg)
# ----------------------------------------------------------------------------------------------------------------------

def load_tests(*args):                                                          ###
    tests =      (                                                              ###
                 BasicConfigTest, LoggerAdapterTest, LoggerTest,
#                 SMTPHandlerTest, FileHandlerTest, RotatingFileHandlerTest,
                 FileHandlerTest, RotatingFileHandlerTest,                      ###
#                 LastResortTest, LogRecordTest, ExceptionTest,
                 LogRecordTest, #ExceptionTest,                                 ###
                )


#    tests = (LoggerAdapterTest,)

    suite = unittest.TestSuite([unittest.makeSuite(test) for test in tests])    ###
    return suite                                                                ###
