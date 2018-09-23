This is an experiment to see what it takes to port the [CPython standard library](https://github.com/python/cpython/tree/v3.4.9/Lib) to CircuitPython on an [Adafruit Metro M4](https://www.adafruit.com/product/3382) which has 192kB of RAM.

The diff from CPython is retained in the source files in the following way:
- No lines are removed
- Lines that are not needed/supported or is failing on CircuitPython are commented out with a single ```#``` at the beginning of the line
- Changes are inserted only as new lines with a trailing ```###``` as an added sign

It doesn't matter that the source files are large, because the resulting ```.mpy``` files are stripped of the comments.

Special cases:
- ```itertools.py``` was created from the equivalent functions in the docs
- ```posix.py``` was hacked from scratch (C module in CPython)
- ```time.py``` was hacked from scratch (CPython: [timemodule.c](https://github.com/python/cpython/blob/master/Modules/timemodule.c))
- ```unittest/mp_function_attributes.py``` added to handle properties on functions
- ```test/support/__init__.py``` is converted to ```test/support.py``` so it can be cross compiled

Caveats so far:
- skip on Test classes are not working (can probably be fixed like for functions)
- fnmatch: translate(): ```\Z(?ms)``` is dropped from the regex since it's not supported by the ```ure``` module
- many more...


Test script to run on the board:
```python
verbosity=2

import supervisor
supervisor.set_next_stack_limit(12 * 1024)

import gc
print('mem_free:', gc.mem_free())  # prints: mem_free: 171104

print('import unittest')
import unittest

print('mem_free:', gc.mem_free())  # prints: mem_free: 78112


# separate means that the test files are run one by one to avoid running out of memory

unittest.main(module=None, verbosity=verbosity, start='/lib/test', separate=True)
# Ran 324 tests in 161.975s
# FAILED (failures=1) (skipped=13) (expected failures=2)

unittest.main(module=None, verbosity=verbosity, start='/lib/unittest/test', separate=True)
# Ran 256 tests in 24.438s
# FAILED (failures=2) (errors=3) (skipped=1)

# Test only one module
unittest.main(module='test.test_os', verbosity=verbosity)


```
