This is an experiment to see what it would take to port the [CPython standard library](https://github.com/python/cpython/tree/v3.4.9/Lib) to CircuitPython on an [Adafruit Metro M4](https://www.adafruit.com/product/3382) which has 192kB of RAM.

The diff from CPython is retained in the source files in the following way:
- No lines are removed
- Lines that are not needed/supported or is failing on CircuitPython are commented out with a single ```#``` at the beginning of the line
- Changes are inserted only as new lines with a trailing ```###``` as an added sign

It doesn't matter that the source files are large, because the resulting ```.mpy``` files are stripped of the comments.

Special cases:
- Added ```unittest/mp_function_attributes.py``` to handle properties on functions
- ```test/support/__init__.py``` is converted to ```test/support.py``` so it can be cross compiled
- ```itertools.py``` was copied from MicroPython [itertools.py](https://github.com/micropython/micropython-lib/blob/master/itertools/itertools.py) (CPython: [itertoolsmodule.c](https://github.com/python/cpython/blob/master/Modules/itertoolsmodule.c))
- ```time.py``` was hacked from scratch (CPython: [timemodule.c](https://github.com/python/cpython/blob/master/Modules/timemodule.c))

Caveats so far:
- skip on Test classes are not working (can probably be fixed like for functions)
- fnmatch: translate(): ```\Z(?ms)``` is dropped from the regex since it's not supported by the ```ure``` module


The scope of this experiment was to convert ```os```, ```time```, ```unittest``` and be able to run the ```os``` and ```time``` tests.
Some dependency modules had to be added to support that.

The file ```added.diff``` shows the lines that have been added (not the ones 'removed').

Test script:
```python
verbosity=2

import supervisor
supervisor.set_next_stack_limit(8 * 1024)

import gc
print('mem_free:', gc.mem_free())

print('import unittest')
import unittest

print('mem_free:', gc.mem_free())

import _os
import _sys

from unittest import loader, runner

start = '/lib/test'

# Test files have to be collected one by one for memory reasons
for d in _os.listdir(start):
    if not d.startswith('test_') and d.endswith('.mpy'):
        continue
    print('\n' + start + '/' + d)
    print('------------------------------')
    tests = loader.defaultTestLoader.discover(start, d)
    testrunner = runner.TextTestRunner(verbosity=verbosity)

    print()
    testrunner.run(tests)

    print('\nmem_free:', gc.mem_free())
    tests = None
    testrunner = None
    gc.collect()
    print('\\n')

```

Output:
```
mem_free: 172624
import unittest
mem_free: 80128

/lib/test/test_os.mpy
------------------------------

test_stat_attributes (test_os.StatAttributeTests) ... ok
test_statvfs_attributes (test_os.StatAttributeTests) ... ok
test_walk_bottom_up (test_os.WalkTests) ... ok
test_walk_prune (test_os.WalkTests) ... ok
test_walk_topdown (test_os.WalkTests) ... ok
test_exist_ok_existing_directory (test_os.MakedirTests) ... ok
test_exist_ok_existing_regular_file (test_os.MakedirTests) ... ok
test_makedir (test_os.MakedirTests) ... ok
test_remove_all (test_os.RemoveDirsTests) ... ok
test_remove_nothing (test_os.RemoveDirsTests) ... ok
test_remove_partial (test_os.RemoveDirsTests) ... ok
test_urandom_length (test_os.URandomTests) ... ok
test_urandom_value (test_os.URandomTests) ... ok

----------------------------------------------------------------------
Ran 13 tests in 17.000s

OK

mem_free: 66384



/lib/test/test_time.mpy
------------------------------

test_asctime (test_time.TimeTestCase) ... ok
test_asctime_bounding_check (test_time.TimeTestCase) ... ok
test_clock (test_time.TimeTestCase) ... skipped 'need time.clock()'
test_clock_getres (test_time.TimeTestCase) ... skipped 'need time.clock_getres()'
test_clock_monotonic (test_time.TimeTestCase) ... skipped 'need time.clock_gettime()'
test_clock_realtime (test_time.TimeTestCase) ... skipped 'need time.clock_gettime()'
test_clock_settime (test_time.TimeTestCase) ... skipped 'need time.clock_settime()'
test_conversions (test_time.TimeTestCase) ... ok
test_ctime (test_time.TimeTestCase) ... ok
test_ctime_without_arg (test_time.TimeTestCase) ... ok
test_data_attributes (test_time.TimeTestCase) ... ok
test_default_values_for_zero (test_time.TimeTestCase) ... ok
test_gmtime_without_arg (test_time.TimeTestCase) ... ok
test_insane_timestamps (test_time.TimeTestCase) ... skipped 'Crashes'
test_localtime_failure (test_time.TimeTestCase) ... skipped 'need 64-bit time_t'
test_localtime_without_arg (test_time.TimeTestCase) ... ok
test_mktime (test_time.TimeTestCase) ... ok
test_mktime_error (test_time.TimeTestCase) ... ok
test_monotonic (test_time.TimeTestCase) ... ok
test_sleep (test_time.TimeTestCase) ... ok
test_strftime (test_time.TimeTestCase) ... ok
test_strftime_bounding_check (test_time.TimeTestCase) ... ok
test_strptime (test_time.TimeTestCase) ... skipped 'need time.strptime()'
test_strptime_bytes (test_time.TimeTestCase) ... skipped 'need time.strptime()'
test_strptime_exception_context (test_time.TimeTestCase) ... skipped 'need time.strptime()'
test_time (test_time.TimeTestCase) ... ok
test_tzset (test_time.TimeTestCase) ... skipped 'time module has no attribute tzset'
test_large_year (test_time.TestAsctime4dyear) ... ok
test_negative (test_time.TestAsctime4dyear) ... ok
test_year (test_time.TestAsctime4dyear) ... ok

----------------------------------------------------------------------
Ran 30 tests in 3.000s

OK (skipped=11)

mem_free: 17856

```
