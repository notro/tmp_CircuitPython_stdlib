# Due to memory reason test_logging.py had to be split up

import logging
import logging.handlers
#import datetime
import io
#import gc
import os
import re
import sys
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


# This line delimiter and the next one marks the code that was cut out from test_logging.py
# ----------------------------------------------------------------------------------------------------------------------
class FormatterTest(unittest.TestCase):
    def setUp(self):
        self.common = {
            'name': 'formatter.test',
            'level': logging.DEBUG,
            'pathname': os.path.join('path', 'to', 'dummy.ext'),
            'lineno': 42,
            'exc_info': None,
            'func': None,
            'msg': 'Message with %d %s',
            'args': (2, 'placeholders'),
        }
        self.variants = {
        }

    def get_record(self, name=None):
        result = dict(self.common)
        if name is not None:
            result.update(self.variants[name])
        return logging.makeLogRecord(result)

    def test_percent(self):
        # Test %-formatting
        r = self.get_record()
        f = logging.Formatter('${%(message)s}')
        self.assertEqual(f.format(r), '${Message with 2 placeholders}')
        f = logging.Formatter('%(random)s')
        self.assertRaises(KeyError, f.format, r)
        self.assertFalse(f.usesTime())
        f = logging.Formatter('%(asctime)s')
        self.assertTrue(f.usesTime())
        f = logging.Formatter('%(asctime)-15s')
        self.assertTrue(f.usesTime())
        f = logging.Formatter('asctime')
        self.assertFalse(f.usesTime())

    def test_braces(self):
        # Test {}-formatting
        r = self.get_record()
        f = logging.Formatter('$%{message}%$', style='{')
        self.assertEqual(f.format(r), '$%Message with 2 placeholders%$')
        f = logging.Formatter('{random}', style='{')
        self.assertRaises(KeyError, f.format, r)
        self.assertFalse(f.usesTime())
        f = logging.Formatter('{asctime}', style='{')
        self.assertTrue(f.usesTime())
        f = logging.Formatter('{asctime!s:15}', style='{')
        self.assertTrue(f.usesTime())
        f = logging.Formatter('{asctime:15}', style='{')
        self.assertTrue(f.usesTime())
        f = logging.Formatter('asctime', style='{')
        self.assertFalse(f.usesTime())

#    def test_dollars(self):
#        # Test $-formatting
#        r = self.get_record()
#        f = logging.Formatter('$message', style='$')
#        self.assertEqual(f.format(r), 'Message with 2 placeholders')
#        f = logging.Formatter('$$%${message}%$$', style='$')
#        self.assertEqual(f.format(r), '$%Message with 2 placeholders%$')
#        f = logging.Formatter('${random}', style='$')
#        self.assertRaises(KeyError, f.format, r)
#        self.assertFalse(f.usesTime())
#        f = logging.Formatter('${asctime}', style='$')
#        self.assertTrue(f.usesTime())
#        f = logging.Formatter('${asctime', style='$')
#        self.assertFalse(f.usesTime())
#        f = logging.Formatter('$asctime', style='$')
#        self.assertTrue(f.usesTime())
#        f = logging.Formatter('asctime', style='$')
#        self.assertFalse(f.usesTime())
#
    def test_invalid_style(self):
        self.assertRaises(ValueError, logging.Formatter, None, None, 'x')

#    def test_time(self):
#        r = self.get_record()
#        dt = datetime.datetime(1993, 4, 21, 8, 3, 0, 0, utc)
#        # We use None to indicate we want the local timezone
#        # We're essentially converting a UTC time to local time
#        r.created = time.mktime(dt.astimezone(None).timetuple())
#        r.msecs = 123
#        f = logging.Formatter('%(asctime)s %(message)s')
#        f.converter = time.gmtime
#        self.assertEqual(f.formatTime(r), '1993-04-21 08:03:00,123')
#        self.assertEqual(f.formatTime(r, '%Y:%d'), '1993:21')
#        f.format(r)
#        self.assertEqual(r.asctime, '1993-04-21 08:03:00,123')
#
class TestBufferingFormatter(logging.BufferingFormatter):
    def formatHeader(self, records):
        return '[(%d)' % len(records)

    def formatFooter(self, records):
        return '(%d)]' % len(records)

class BufferingFormatterTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            logging.makeLogRecord({'msg': 'one'}),
            logging.makeLogRecord({'msg': 'two'}),
        ]

    def test_default(self):
        f = logging.BufferingFormatter()
        self.assertEqual('', f.format([]))
        self.assertEqual('onetwo', f.format(self.records))

    def test_custom(self):
        f = TestBufferingFormatter()
        self.assertEqual('[(2)onetwo(2)]', f.format(self.records))
        lf = logging.Formatter('<%(message)s>')
        f = TestBufferingFormatter(lf)
        self.assertEqual('[(2)<one><two>(2)]', f.format(self.records))

class ExceptionTest(BaseTest):
    def test_formatting(self):
        r = self.root_logger
        h = RecordingHandler()
        r.addHandler(h)
        try:
            raise RuntimeError('deliberate mistake')
        except:
            logging.exception('failed', stack_info=True)
        r.removeHandler(h)
        h.close()
        r = h.records[0]
        self.assertTrue(r.exc_text.startswith('Traceback (most recent '
                                              'call last):\n'))
        self.assertTrue(r.exc_text.endswith('\nRuntimeError: '
                                            'deliberate mistake'))
#        self.assertTrue(r.stack_info.startswith('Stack (most recent '
#                                              'call last):\n'))
#        self.assertTrue(r.stack_info.endswith('logging.exception(\'failed\', '
#                                            'stack_info=True)'))


#class LastResortTest(BaseTest):
#    def test_last_resort(self):
#        # Test the last resort handler
#        root = self.root_logger
#        root.removeHandler(self.root_hdlr)
#        old_stderr = sys.stderr
#        old_lastresort = logging.lastResort
#        old_raise_exceptions = logging.raiseExceptions
#        try:
#            sys.stderr = sio = io.StringIO()
#            root.debug('This should not appear')
#            self.assertEqual(sio.getvalue(), '')
#            root.warning('This is your final chance!')
#            self.assertEqual(sio.getvalue(), 'This is your final chance!\n')
#            #No handlers and no last resort, so 'No handlers' message
#            logging.lastResort = None
#            sys.stderr = sio = io.StringIO()
#            root.warning('This is your final chance!')
#            self.assertEqual(sio.getvalue(), 'No handlers could be found for logger "root"\n')
#            # 'No handlers' message only printed once
#            sys.stderr = sio = io.StringIO()
#            root.warning('This is your final chance!')
#            self.assertEqual(sio.getvalue(), '')
#            root.manager.emittedNoHandlerWarning = False
#            #If raiseExceptions is False, no message is printed
#            logging.raiseExceptions = False
#            sys.stderr = sio = io.StringIO()
#            root.warning('This is your final chance!')
#            self.assertEqual(sio.getvalue(), '')
#        finally:
#            sys.stderr = old_stderr
#            root.addHandler(self.root_hdlr)
#            logging.lastResort = old_lastresort
#            logging.raiseExceptions = old_raise_exceptions
#
#
class FakeHandler:

    def __init__(self, identifier, called):
        for method in ('acquire', 'flush', 'close', 'release'):
            setattr(self, method, self.record_call(identifier, method, called))

    def record_call(self, identifier, method_name, called):
        def inner():
            called.append('{} - {}'.format(identifier, method_name))
        return inner


class RecordingHandler(logging.NullHandler):

    def __init__(self, *args, **kwargs):
        super(RecordingHandler, self).__init__(*args, **kwargs)
        self.records = []

    def handle(self, record):
        """Keep track of all the emitted records."""
        self.records.append(record)


#class ShutdownTest(BaseTest):
#
#    """Test suite for the shutdown method."""
#
#    def setUp(self):
#        super(ShutdownTest, self).setUp()
#        self.called = []
#
#        raise_exceptions = logging.raiseExceptions
#        self.addCleanup(setattr, logging, 'raiseExceptions', raise_exceptions)
#
#    def raise_error(self, error):
#        def inner():
#            raise error()
#        return inner
#
#    def test_no_failure(self):
#        # create some fake handlers
#        handler0 = FakeHandler(0, self.called)
#        handler1 = FakeHandler(1, self.called)
#        handler2 = FakeHandler(2, self.called)
#
#        # create live weakref to those handlers
#        handlers = map(logging.weakref.ref, [handler0, handler1, handler2])
#
#        logging.shutdown(handlerList=list(handlers))
#
#        expected = ['2 - acquire', '2 - flush', '2 - close', '2 - release',
#                    '1 - acquire', '1 - flush', '1 - close', '1 - release',
#                    '0 - acquire', '0 - flush', '0 - close', '0 - release']
#        self.assertEqual(expected, self.called)
#
#    def _test_with_failure_in_method(self, method, error):
#        handler = FakeHandler(0, self.called)
#        setattr(handler, method, self.raise_error(error))
#        handlers = [logging.weakref.ref(handler)]
#
#        logging.shutdown(handlerList=list(handlers))
#
#        self.assertEqual('0 - release', self.called[-1])
#
#    def test_with_ioerror_in_acquire(self):
#        self._test_with_failure_in_method('acquire', OSError)
#
#    def test_with_ioerror_in_flush(self):
#        self._test_with_failure_in_method('flush', OSError)
#
#    def test_with_ioerror_in_close(self):
#        self._test_with_failure_in_method('close', OSError)
#
#    def test_with_valueerror_in_acquire(self):
#        self._test_with_failure_in_method('acquire', ValueError)
#
#    def test_with_valueerror_in_flush(self):
#        self._test_with_failure_in_method('flush', ValueError)
#
#    def test_with_valueerror_in_close(self):
#        self._test_with_failure_in_method('close', ValueError)
#
#    def test_with_other_error_in_acquire_without_raise(self):
#        logging.raiseExceptions = False
#        self._test_with_failure_in_method('acquire', IndexError)
#
#    def test_with_other_error_in_flush_without_raise(self):
#        logging.raiseExceptions = False
#        self._test_with_failure_in_method('flush', IndexError)
#
#    def test_with_other_error_in_close_without_raise(self):
#        logging.raiseExceptions = False
#        self._test_with_failure_in_method('close', IndexError)
#
#    def test_with_other_error_in_acquire_with_raise(self):
#        logging.raiseExceptions = True
#        self.assertRaises(IndexError, self._test_with_failure_in_method,
#                          'acquire', IndexError)
#
#    def test_with_other_error_in_flush_with_raise(self):
#        logging.raiseExceptions = True
#        self.assertRaises(IndexError, self._test_with_failure_in_method,
#                          'flush', IndexError)
#
#    def test_with_other_error_in_close_with_raise(self):
#        logging.raiseExceptions = True
#        self.assertRaises(IndexError, self._test_with_failure_in_method,
#                          'close', IndexError)
#
#
class ModuleLevelMiscTest(BaseTest):

    """Test suite for some module level methods."""

    def test_disable(self):
        old_disable = logging.root.manager.disable
        # confirm our assumptions are correct
        self.assertEqual(old_disable, 0)
        self.addCleanup(logging.disable, old_disable)

        logging.disable(83)
        self.assertEqual(logging.root.manager.disable, 83)

    def _test_log(self, method, level=None):
        called = []
        patch(self, logging, 'basicConfig',
              lambda *a, **kw: called.append((a, kw)))

        recording = RecordingHandler()
        logging.root.addHandler(recording)

        log_method = getattr(logging, method)
        if level is not None:
            log_method(level, "test me: %r", recording)
        else:
            log_method("test me: %r", recording)

        self.assertEqual(len(recording.records), 1)
        record = recording.records[0]
        self.assertEqual(record.getMessage(), "test me: %r" % recording)

        expected_level = level if level is not None else getattr(logging, method.upper())
        self.assertEqual(record.levelno, expected_level)

        # basicConfig was not called!
        self.assertEqual(called, [])

    def test_log(self):
        self._test_log('log', logging.ERROR)

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

    def test_set_logger_class(self):
        self.assertRaises(TypeError, logging.setLoggerClass, object)

        class MyLogger(logging.Logger):
            pass

        logging.setLoggerClass(MyLogger)
        self.assertEqual(logging.getLoggerClass(), MyLogger)

        logging.setLoggerClass(logging.Logger)
        self.assertEqual(logging.getLoggerClass(), logging.Logger)

#    def test_logging_at_shutdown(self):
#        # Issue #20037
#        code = """if 1:
#            import logging
#
#            class A:
#                def __del__(self):
#                    try:
#                        raise ValueError("some error")
#                    except Exception:
#                        logging.exception("exception in __del__")
#
#            a = A()"""
#        rc, out, err = assert_python_ok("-c", code)
#        err = err.decode()
#        self.assertIn("exception in __del__", err)
#        self.assertIn("ValueError: some error", err)
#

# ----------------------------------------------------------------------------------------------------------------------

def load_tests(*args):                                                          ###
    tests =      (                                                              ###
#                 ManagerTest, FormatterTest, BufferingFormatterTest,
                 FormatterTest, BufferingFormatterTest,                         ###
#                 QueueHandlerTest, ShutdownTest, ModuleLevelMiscTest,
                 ModuleLevelMiscTest,                                           ###
#                 LastResortTest, LogRecordTest, ExceptionTest,
                 ExceptionTest,                                                 ###
                )

#    tests = (ExceptionTest,)

    suite = unittest.TestSuite([unittest.makeSuite(test) for test in tests])    ###
    return suite                                                                ###
