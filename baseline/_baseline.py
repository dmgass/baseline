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

from __future__ import absolute_import, division, print_function, unicode_literals

import atexit
import inspect
import os
import sys

from ._script import Script


SEPARATOR = '\n' + '*' * 40 + '\n'

if sys.version_info.major >= 3:
    INSIDE_STRING_DELIMETER_SLICE = slice(1, -1)
    baseclass = str
else:
    INSIDE_STRING_DELIMETER_SLICE = slice(2, -1)
    baseclass = unicode


class Baseline(baseclass):

    """Baselined string representation manager.

    Support comparison of a string against a baselined representation of the
    string. When the comparison results in a mismatch, update the baselined
    representation in a copy of the Python script containing the baseline.

    """
    STRIP_TRAILING_WHITESPACE = False

    # set of instances of this class where a string comparison against the
    # baselined representation was a mismatch
    _baselines_to_update = set()

    # dictionary of every unique source code location of Baseline instantiation
    # key: source code location of Baseline instantiation (abs path, linenum)
    # value: Baseline instance for a particular location
    _all_instances = {}

    # set of string representations of strings compared against this baseline
    # (its an instance attribute, but for documentation and pylint purposes)
    _updates = None

    @staticmethod
    def _dedent(text):
        """Remove common indentation from each line in a text block.

        When text block is a single line, return text block. Otherwise determine
        common indentation from last line, strip common indentation from each
        line, and return text block consisting of inner lines (don't include
        first and last lines since they either empty or contain whitespace and
        are present in baselined representations to make them pretty and
        delineate the common indentation).

        :param str text: text block
        :returns: text block with common indentation removed
        :rtype: str
        :raises ValueError: when text block violates whitespace rules

        """
        lines = text.split('\n')

        if len(lines) == 1:
            indent = 0

        elif lines[0].strip():
            raise ValueError('when multiple lines, first line must be blank')

        elif lines[-1].strip():
            raise ValueError('last line must only contain indent whitespace')

        else:
            indent = len(lines[-1])

            if any(line[:indent].strip() for line in lines):
                raise ValueError(
                    'indents must equal or exceed indent in last line')

            lines = [line[indent:] for line in lines][1:-1]

        return indent, '\n'.join(lines)

    def __new__(cls, text):
        """Construct and initialize Baseline instance.

        Determine source code location (path/line) for every instance
        constructed and return same instance for every unique location.
        Remove whitespace used to make the representation look pretty in
        the source file (i.e. when multi-line, remove common indentation
        as well as the first and last lines).

        :param str text: baselined string representation
        :returns: normalized string representation
        :raises RuntimeError: when text differs for a specific location

        """
        frame = inspect.getouterframes(inspect.currentframe())[1]
        path = os.path.abspath(frame[1])
        linenum = frame[2]

        assert path.lower().endswith('.py')

        key = (path, linenum)

        try:
            instance = cls._all_instances[key]
        except KeyError:
            indent, dedented_text = cls._dedent(text)
            instance = baseclass.__new__(cls, dedented_text)
            cls._all_instances[key] = instance

            # initialize instance here instead of __init__ to avoid:
            #   (1) reinitializing when returning a pre-existing instance
            #   (2) recomputing path and linenum (or corrupting class signature
            #       by passing them to __init__)
            instance.z__path = path
            instance.z__linenum = linenum
            instance._indent = indent
            instance._updates = set()

        else:
            if baseclass.__ne__(instance, text):
                raise RuntimeError('varying baseline text not allowed')

        return instance

    @classmethod
    def _repr(cls, text, special_chars=('\n', '"', '\\')):
        # convert text string into a baseline representation but since the
        # representation will be encapsulated in a "raw" triple quoted string,
        # leave newlines, quotes, and backslashes as is.
        try:
            char = special_chars[0]
        except IndexError:
            text = repr(text)[INSIDE_STRING_DELIMETER_SLICE]
        else:
            text = char.join(
                cls._repr(s, special_chars[1:]) for s in text.split(char))

        return text

    def __eq__(self, text):
        """Make representation and compare it against baselined representation.

        Save a copy of the representation in order to later update the
        representation in the source code file in the event any comparison
        against this baseline fails.

        :param str text: string to compare against baselined representation
        :returns: indication if string representation matches baseline
        :rtype: bool

        """
        if self.STRIP_TRAILING_WHITESPACE:
            # don't baseline trailing whitespace to avoid pylint complaints
            text = '\n'.join(line.rstrip(' ') for line in text.split('\n'))

        # convert to a representation to compare against baseline
        text = self._repr(text)

        # use triple double quote, except use triple single quote when
        # triple double quote is present to avoid syntax errors
        quotes = '"""'
        if quotes in text:
            quotes = "'''"
            # handle when both triple double and triple single quotes present
            text = text.replace(quotes, r"\'\'\'")

        # Save a copy of the representation in order to later update the
        # representation in the source code file in the event any comparison
        # against this baseline fails. Wrap with blank lines when multi-line
        # or when text ends with characters that would otherwise result in a
        # syntax error in the formatted representation.
        multiline = self._indent or ('\n' in text)
        if multiline or text.endswith('\\') or text.endswith(quotes[0]):
            self._updates.add('r' + quotes + '\n' + text + '\n' + quotes)
        else:
            self._updates.add('r' + quotes + text + quotes)

        is_equal = super(Baseline, self).__eq__(text)

        if not is_equal:
            if not self._baselines_to_update:
                atexit.register(Baseline._atexit_callback)

            self._baselines_to_update.add(self)

        return is_equal

    def __ne__(self, text):
        # not necessary for Python 3 or greater, but override for Python 2
        # for use with assertNotEqual( ) for internal regression test purposes
        return not (self == text)

    def __hash__(self):
        # provide unique ID to allow Baseline instances to be a part of a set
        # or be used as dictionary keys (otherwise the __eq__ method would be
        # invoked as part of normal set/dict operations and would result in
        # problematic comparisions of unrelated Baseline instances)
        return id(self)

    @property
    def z__update(self):
        """Triple quoted baseline representation.

        Return string with multiple triple quoted baseline representations when
        baseline had been compared multiple times against varying string
        representations.

        :returns: source file baseline replacement text
        :rtype: str

        """
        # sort updates so Python hash seed has no impact on regression test
        update = '\n'.join(sorted(self._updates))

        indent = ' ' * self._indent

        lines = [(indent + line).rstrip() for line in update.split('\n')]

        return '\n'.join(lines).lstrip()

    @classmethod
    def _atexit_callback(cls):
        updated_scripts = {}

        for baseline in cls._baselines_to_update:
            try:
                script = updated_scripts[baseline.z__path]
            except KeyError:
                script = Script(baseline.z__path)
                updated_scripts[baseline.z__path] = script

            script.add_update(baseline.z__linenum, baseline.z__update)

        for key in sorted(updated_scripts):
            script = updated_scripts[key]
            script.update()

        return updated_scripts
