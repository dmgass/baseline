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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# standard library
import os
import re
import subprocess
from enum import Enum


def showpath(path):
    # TODO make method
    retval = os.path.relpath(path, os.getcwd())
    if path.startswith('..'):
        retval = path
    return retval


class Mode(Enum):

    """Mode of operation."""

    COPY = 0
    """Create copy with updates."""

    OVERWRITE = 1
    """Overwrite script with updates."""


class Script(object):

    REGEX = re.compile(
        r'(?P<prefix>.*?)"""(?P<docstr>.*?""")(?P<suffix>.*)', re.DOTALL)

    instances = {}

    def __init__(self, path):
        self.path = path
        self.original_lines_list = None
        self.mismatches = {}

    @classmethod
    def add_instance(cls, path):
        cls.instances[path] = cls(path)

    def add_mismatch(self, baseline):
        self.mismatches[baseline.z__linenum] = baseline.z__update

    @property
    def original_lines(self):
        if self.original_lines_list is None:
            with open(self.path, 'r') as fh:
                self.original_lines_list = fh.read().split('\n')

        return self.original_lines_list
    
    def replace_lines(self, linenum, update):
        lines = self.original_lines

        count = 0
        for index in xrange(linenum - 1, -1, -1):
            count += lines[index].count('"""')
            if count >= 2:
                linenum = index
                break
        else:
            docstr_not_found = (
                '{}:{}: could not find baseline docstring'
                ''.format(show_path(self.path), linenum))
            raise RuntimeError(docstr_not_found)

        old_content = '\n'.join(lines[linenum:])

        match = self.REGEX.match(old_content)

        if match is None:
            docstr_not_found = (
                '{}:{}: could not find docstring'.format(self.path, linenum))
            raise RuntimeError(docstr_not_found)

        new_content = '{}r"""{}"""{}'.format(
            match.group('prefix'), update, match.group('suffix'))

        lines[linenum:] = new_content.split('\n')

    def update(self):
        for linenum in reversed(sorted(self.mismatches)):
            self.replace_lines(linenum, self.mismatches[linenum])
        print "UPDATED:", showpath(self.path)
        path = self.path.replace('.py', '.update.py')
        with open(path, 'w') as fh:
            fh.write('\n'.join(self.original_lines))
