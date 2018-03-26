# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2018 Daniel Mark Gass
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
from argparse import ArgumentParser
from glob import glob

PY2 = sys.version_info.major < 3
if PY2:  # pragma: no cover
    input = raw_input

UPDATE_EXT = '.update.py'

DESCRIPTION = """
Locate scripts with baseline updates within the paths specified and modify 
the scripts with the updates found. (The scripts to be modified will be 
summarized and you will be offered a chance to cancel before files are
changed.)
""".strip()

def main(args=None):
    """Command line interface.

    :param list args: command line options (defaults to sys.argv)
    :returns: exit code
    :rtype: int

    """
    parser = ArgumentParser(
        prog='baseline',
        description=DESCRIPTION)

    parser.add_argument(
        'path', nargs='*',
        help='module or directory path')

    parser.add_argument(
        '-w', '--walk', action='store_true',
        help='recursively walk directories')

    args = parser.parse_args(args)

    paths = args.path or ['.']

    paths = [path for pattern in paths for path in glob(pattern)]

    if args.walk:
        for dirpath in (p for p in paths if os.path.isdir(p)):
            for root, _dirs, files in os.walk(dirpath):
                paths += (os.path.join(root, filename) for filename in files)
    else:
        for dirpath in (p for p in paths if os.path.isdir(p)):
            paths += (os.path.join(dirpath, pth) for pth in os.listdir(dirpath))

    update_paths = [
        os.path.abspath(p) for p in paths if p.lower().endswith(UPDATE_EXT)]

    if update_paths:
        script_paths = [pth[:-len(UPDATE_EXT)] + '.py' for pth in update_paths]

        print('Found updates for:')
        for path in script_paths:
            print('  ' + os.path.relpath(path))
        print()

        try:
            input('Hit [ENTER] to update, [Ctrl-C] to cancel ')
        except KeyboardInterrupt:
            print()
            print('Update canceled.')
        else:
            print()
            for script_path, update_path in zip(script_paths, update_paths):
                with open(update_path) as update:
                    new_content = update.read()
                with open(script_path, 'w') as script:
                    script.write(new_content)
                os.remove(update_path)
                print(
                    os.path.relpath(update_path) +
                    ' -> ' +
                    os.path.relpath(script_path))

    return 0


if __name__ == '__main__':

    sys.exit(main())
