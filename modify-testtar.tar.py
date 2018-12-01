import argparse
import os
import sys
import tarfile

# Create a small file that can be used

parser = argparse.ArgumentParser(description='diff strip tool')
parser.add_argument('src', help='Original CPyton stdlib test/testtar.tar')
parser.add_argument('--verbose', '-v', action='count', default=0, help='be verbose')
args = parser.parse_args()

root = os.path.dirname(os.path.realpath(__file__))
args.dst = os.path.join(root, 'lib', 'test/testtar.tar')

i = 0
with tarfile.open(args.src) as src:
    with tarfile.open(args.dst, 'w') as dst:

        for tarinfo in src:
            i += 1
            name = tarinfo.name.encode('utf-8', errors='replace').decode()
            print(name, "is", tarinfo.size, "bytes in size and is ", end="")
            if tarinfo.isreg():
                print("a regular file.")
            elif tarinfo.isdir():
                print("a directory.")
            else:
                print("something else.")

            if tarinfo.size < 10 *1024 and name.startswith('ustar') and 'umlaut' not in name:
                if tarinfo.isreg():
                    if tarinfo.size > 128:
                        tarinfo.size = 128
                    print('  ADD:', name)
                    dst.addfile(tarinfo, fileobj=src.extractfile(tarinfo))
                else:
                    print('  ADD:', name)
                    dst.addfile(tarinfo)


print('\n\n\n\n\n\n')

with tarfile.open(args.dst) as tar:
    for tarinfo in tar:
        name = tarinfo.name.encode('utf-8', errors='replace').decode()
        print(name, "is", tarinfo.size, "bytes in size")

