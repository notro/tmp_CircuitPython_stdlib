import timeit
import unittest
import io
import time


# timeit's default number of iterations.
DEFAULT_NUMBER = 1000000

# timeit's default number of repetitions.
DEFAULT_REPEAT = 3

# XXX: some tests are commented out that would improve the coverage but take a
# long time to run because they test the default number of loops, which is
# large.  The tests could be enabled if there was a way to override the default
# number of loops during testing, but this would require changing the signature
# of some functions that use the default as a default argument.

class FakeTimer:
    BASE_TIME = 42.0
    def __init__(self, seconds_per_increment=1.0):
        self.count = 0
        self.setup_calls = 0
        self.seconds_per_increment=seconds_per_increment
        timeit._fake_timer = self

    def __call__(self):
        return self.BASE_TIME + self.count * self.seconds_per_increment

    def inc(self):
        self.count += 1

    def setup(self):
        self.setup_calls += 1

    def wrap_timer(self, timer):
        """Records 'timer' and returns self as callable timer."""
        self.saved_timer = timer
        return self

class TestTimeit(unittest.TestCase):

    def tearDown(self):
        try:
            del timeit._fake_timer
        except (AttributeError, KeyError):                                      ###
            pass

    def test_timer_invalid_stmt(self):
        self.assertRaises(ValueError, timeit.Timer, stmt=None)

    def test_timer_invalid_setup(self):
        self.assertRaises(ValueError, timeit.Timer, setup=None)

    def fake_callable_setup(self):
        self.fake_timer.setup()

    def fake_callable_stmt(self):
        self.fake_timer.inc()

    fake_setup = fake_callable_setup                                            ###
    fake_stmt = fake_callable_stmt                                              ###
                                                                                ###
    def timeit(self, stmt, setup, number=None):
        self.fake_timer = FakeTimer()
        t = timeit.Timer(stmt=stmt, setup=setup, timer=self.fake_timer)
        kwargs = {}
        if number is None:
            number = DEFAULT_NUMBER
        else:
            kwargs['number'] = number
        delta_time = t.timeit(**kwargs)
        self.assertEqual(self.fake_timer.setup_calls, 1)
        self.assertEqual(self.fake_timer.count, number)
        self.assertEqual(delta_time, number)

    # Takes too long to run in debug build.
    #def test_timeit_default_iters(self):
    #    self.timeit(self.fake_stmt, self.fake_setup)

    def test_timeit_zero_iters(self):
        self.timeit(self.fake_stmt, self.fake_setup, number=0)

    def test_timeit_few_iters(self):
        self.timeit(self.fake_stmt, self.fake_setup, number=3)

    def test_timeit_callable_stmt(self):
        self.timeit(self.fake_callable_stmt, self.fake_setup, number=3)

    def test_timeit_callable_setup(self):
        self.timeit(self.fake_stmt, self.fake_callable_setup, number=3)

    def test_timeit_callable_stmt_and_setup(self):
        self.timeit(self.fake_callable_stmt,
                self.fake_callable_setup, number=3)

    # Takes too long to run in debug build.
    #def test_timeit_function(self):
    #    delta_time = timeit.timeit(self.fake_stmt, self.fake_setup,
    #            timer=FakeTimer())
    #    self.assertEqual(delta_time, DEFAULT_NUMBER)

    def test_timeit_function_zero_iters(self):
        self.fake_timer = FakeTimer()                                           ###
        delta_time = timeit.timeit(self.fake_stmt, self.fake_setup, number=0,
                timer=FakeTimer())
        self.assertEqual(delta_time, 0)

    def repeat(self, stmt, setup, repeat=None, number=None):
        self.fake_timer = FakeTimer()
        t = timeit.Timer(stmt=stmt, setup=setup, timer=self.fake_timer)
        kwargs = {}
        if repeat is None:
            repeat = DEFAULT_REPEAT
        else:
            kwargs['repeat'] = repeat
        if number is None:
            number = DEFAULT_NUMBER
        else:
            kwargs['number'] = number
        delta_times = t.repeat(**kwargs)
        self.assertEqual(self.fake_timer.setup_calls, repeat)
        self.assertEqual(self.fake_timer.count, repeat * number)
        self.assertEqual(delta_times, repeat * [float(number)])

    # Takes too long to run in debug build.
    #def test_repeat_default(self):
    #    self.repeat(self.fake_stmt, self.fake_setup)

    def test_repeat_zero_reps(self):
        self.repeat(self.fake_stmt, self.fake_setup, repeat=0)

    def test_repeat_zero_iters(self):
        self.repeat(self.fake_stmt, self.fake_setup, number=0)

    def test_repeat_few_reps_and_iters(self):
        self.repeat(self.fake_stmt, self.fake_setup, repeat=3, number=5)

    def test_repeat_callable_stmt(self):
        self.repeat(self.fake_callable_stmt, self.fake_setup,
                repeat=3, number=5)

    def test_repeat_callable_setup(self):
        self.repeat(self.fake_stmt, self.fake_callable_setup,
                repeat=3, number=5)

    def test_repeat_callable_stmt_and_setup(self):
        self.repeat(self.fake_callable_stmt, self.fake_callable_setup,
                repeat=3, number=5)

    # Takes too long to run in debug build.
    #def test_repeat_function(self):
    #    delta_times = timeit.repeat(self.fake_stmt, self.fake_setup,
    #            timer=FakeTimer())
    #    self.assertEqual(delta_times, DEFAULT_REPEAT * [float(DEFAULT_NUMBER)])

    def test_repeat_function_zero_reps(self):
        delta_times = timeit.repeat(self.fake_stmt, self.fake_setup, repeat=0,
                timer=FakeTimer())
        self.assertEqual(delta_times, [])

    def test_repeat_function_zero_iters(self):
        self.fake_timer = FakeTimer()                                           ###
        delta_times = timeit.repeat(self.fake_stmt, self.fake_setup, number=0,
                timer=FakeTimer())
        self.assertEqual(delta_times, DEFAULT_REPEAT * [0.0])

    def assert_exc_string(self, exc_string, expected_exc_name):
        exc_lines = exc_string.splitlines()
        self.assertGreater(len(exc_lines), 2)
        self.assertTrue(exc_lines[0].startswith('Traceback'))
        self.assertTrue(exc_lines[-1].startswith(expected_exc_name))

    def test_print_exc(self):
        s = io.StringIO()
        def div_by_zero():                                                      ###
            1/0                                                                 ###
        t = timeit.Timer(div_by_zero)                                           ###
        try:
            t.timeit()
        except:
            t.print_exc(s)
        self.assert_exc_string(s.getvalue(), 'ZeroDivisionError')

