import subprocess
import sys

from pathlib import Path

mpy_cross = '/home/pi/circuitpython/workdirs/test/circuitpython/mpy-cross/mpy-cross'

src = Path('lib')

for py in src.glob('**/*.py'):
    mpy = py.with_suffix('.mpy')
    if mpy.exists() and mpy.stat().st_mtime > py.stat().st_mtime:
        #print('skip:', mpy)
        continue

    print('compile:', mpy)
    subprocess.run([mpy_cross, '-o', str(mpy), str(py)])

