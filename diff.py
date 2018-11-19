import argparse
import difflib
import os
import sys


class File:
    def __init__(self, path, fork_dir, original_dir):
        self.path = path
        self.rel = os.path.relpath(path, fork_dir)
        self.original = os.path.join(original_dir, self.rel)
        self.missing = False

        if not os.path.exists(self.original):
            self.original = None

    def __str__(self):
        return 'File({!r}): path={!r}, original={!r}'.format(self.rel, self.path, self.original)

    def parse(self):
        if self.original is None:
            self.lines = open(self.path).readlines()
        else:
            self.lines = []
            with open(self.path) as f1:
                with open(self.original) as f2:
                    l1 = True
                    l2 = f2.readline()
                    count = 0
                    while l1:
                        l1 = f1.readline()
                        count += 1
                        #print('l1 {!r}'.format(l1))
                        #print('   {!r}'.format(l2))
                        #print()
                        if l1 == l2:
                            self.lines.append(l1)
                            l2 = f2.readline()
                        elif l1 == '#' + l2:
                            l2 = f2.readline()
                        else:
                            if ' ###' not in l1:
                                sys.stderr.write('{!r}: ({}) missing ### in {!r}\n'.format(self.path, count, l1))
                                self.missing = True
                            if l1.endswith(' ###'):
                                l1 = l1[:-4].rstrip()
                            self.lines.append(l1)

        self.stripped = ''.join(self.lines)

    def write_stripped(self, path):
        fname = os.path.join(path, self.rel)
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        open(fname, 'w').write(self.stripped)

    def diff(self):
        if self.original:
            org = open(self.original).readlines()
            fromfile = '<CPython-3.4.9>/{}'.format(self.rel)
        else:
            org = []
            fromfile = '/dev/null'
        diff = difflib.unified_diff(org, self.lines, fromfile=fromfile, tofile=os.path.join('lib', self.rel))
        return ''.join(diff)

    def write_diff(self, path):
        fname = os.path.join(path, self.rel)
        fname = os.path.splitext(fname)[0] + '.diff'
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        diff = self.diff()
        open(fname, 'w').write(diff)


def find_files(fork, src, args):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(fork):
        for filename in filenames:
#            if any(ext for ext in ['.mpy', '.zip', '.tar'] if os.path.splitext(filename)[1] == ext):
#                continue
            if os.path.splitext(filename)[1] != '.py':
                if args.verbose > 1 and os.path.splitext(filename)[1] != '.mpy':
                    sys.stdout.write('SKIP support file: {}\n'.format(filename))
                continue

            if filename[-4].isdigit() or os.path.exists(os.path.join(dirpath, filename[:-3] + '2.py')):
                if args.verbose > 1:
                    sys.stdout.write('SKIP split file: {}\n'.format(filename))
                continue

            if args.filter and args.filter not in filename:
                if args.verbose > 1:
                    sys.stdout.write('Filtered: {}\n'.format(filename))
                continue

            if args.verbose == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            else:
                sys.stdout.write('{}\n'.format(filename))

            f = File(os.path.join(dirpath, filename), fork, src)
            files.append(f)

    sys.stdout.write('\n')
    sys.stdout.flush()
    return files


parser = argparse.ArgumentParser(description='diff strip tool')
parser.add_argument('src', help='Original CPyton stdlib 3.4.9 folder')
parser.add_argument('-f', '--filter', help="Files filter")
parser.add_argument('--verbose', '-v', action='count', default=0, help='be verbose')
args = parser.parse_args()

root = os.path.dirname(os.path.realpath(__file__))
fork = os.path.join(root, 'lib')

files = find_files(fork, args.src, args)

for f in files:
    f.parse()

missing = any([f.missing for f in files])
if missing:
    sys.stderr.write('\n\nERROR:\nMissing ### at the end of added line\n')
    sys.exit(1)


for f in files:
    f.write_stripped(os.path.join(root, 'stripped'))
    f.write_diff(os.path.join(root, 'diff'))
