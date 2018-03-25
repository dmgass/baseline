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

import io
import os
import re
from enum import Enum


class Mode(Enum):

    """Mode of operation."""

    COPY = 0
    """Create copy with updates."""

    OVERWRITE = 1
    """Overwrite script with updates."""


DELIMITER_EXPRESSION = '"""' + '|' "'''"


class Script(object):

    """Python script updater."""

    # for regression test purposes (suppresses console output and file writes)
    TEST_MODE = False

    def __init__(self, path):
        self.path = path
        self._lines = None
        self.updates = {}

    @staticmethod
    def showpath(path):
        """Return path in form most convenient for user to read.

        Return relative path when input path is within the current working
        directory, otherwise return same (absolute) path passed in.

        :param path: file system path
        :type path: str or unicode
        :returns: file system path
        :rtype: str

        """
        try:
            retval = os.path.relpath(path, os.getcwd())
        except ValueError:
            retval = path
        else:
            if retval.startswith('..'):
                retval = path
        return retval

    def add_update(self, linenum, update):
        """Register baseline representation replacement text.

        :param int linenum: location of baseline representation
        :param str update: replacement representation (including delimeters)

        """
        self.updates[linenum] = update

    @property
    def lines(self):
        """List of file lines."""
        if self._lines is None:
            with io.open(self.path, 'r', encoding='utf-8') as fh:
                self._lines = fh.read().split('\n')

        return self._lines
    
    # used to replace baseline string representation
    REGEX = re.compile(
        '(?P<prefix>.*?)'  # stuff to retain before string representation
        '[rR]?(?P<delim>{})'  # multi-line string beginning delimeter
        '(?P<docstr>.*?)'  # current representation
        '(?P=delim)'  # multi-line string ending delimeter
        '(?P<suffix>.*)'.format(DELIMITER_EXPRESSION),  # stuff to retain after
        re.DOTALL)

    def replace_baseline_repr(self, linenum, update):
        """Replace individual baseline representation.

        :param int linenum: location of baseline representation
        :param str update: new baseline representation text (with delimiters)

        """
        # use property to access lines to read them from file if necessary
        lines = self.lines

        count = 0
        delimiter = None
        for index in range(linenum - 1, -1, -1):
            line = lines[index]
            if delimiter is None:
                single_quote_index = line.rfind("'''")
                double_quote_index = line.rfind('"""')
                if double_quote_index >= 0:
                    if double_quote_index > single_quote_index:
                        delimiter = '"""'
                    else:
                        delimiter = "'''"
                elif single_quote_index >= 0:
                    delimiter = "'''"
                else:
                    continue
            count += lines[index].count(delimiter)
            if count >= 2:
                linenum = index
                break
        else:
            docstr_not_found = (
                '{}:{}: could not find baseline docstring'
                ''.format(self.showpath(self.path), linenum))
            raise RuntimeError(docstr_not_found)

        old_content = '\n'.join(lines[linenum:])

        match = self.REGEX.match(old_content)

        if match is None:
            docstr_not_found = (
                '{}:{}: could not find docstring'.format(self.path, linenum))
            raise RuntimeError(docstr_not_found)

        new_content = match.group('prefix') + update + match.group('suffix')

        lines[linenum:] = new_content.split('\n')

    def update(self):
        """Replace baseline representations previously registered for update."""
        for linenum in reversed(sorted(self.updates)):
            self.replace_baseline_repr(linenum, self.updates[linenum])

        if not self.TEST_MODE:
            path = '{}.update{}'.format(*os.path.splitext(self.path))
            with io.open(path, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(self.lines))
            print('UPDATE: {}'.format(self.showpath(path)))
