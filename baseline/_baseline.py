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

    Support the comparison of a string against a baselined representation of the
    string. When the comparision results in a mismatch, update the baselined
    representation in a copy of the Python script containing the baseline.

    """

    # set of instances of this class where a string comparison against the baselined
    # representation was a mismatch
    _baselines_to_update = set()

    # dictionary of every unique source code location of Baseline instantiation
    # key: source code location of Baseline instantiation (abs path, linenum)
    # value: Baseline instance for a particular location
    _all_instances = {}

    @staticmethod
    def _dedent(text):
        lines = text.split('\n')

        if len(lines) == 1:
            indent = 0

        elif lines[0].strip():
            raise RuntimeError('first line must be blank')

        elif lines[-1].strip():
            raise RuntimeError('last line must only contain indent whitespace')

        else:
            indent = len(lines[-1])

            if any(line[:indent].strip() for line in lines):
                raise RuntimeError('indents must equal or exceed indent in last line')

            lines = [line[indent:] for line in lines][1:-1]

        return indent, '\n'.join(lines)

    def __new__(cls, text):

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
            instance.z__path = path
            instance.z__linenum = linenum
            instance._indent = indent
            instance._updates = set()
            cls._all_instances[key] = instance
        else:
            if baseclass.__ne__(instance, text):
                raise RuntimeError('varying baseline text not allowed')

        return instance

    @classmethod
    def _psuedo_repr(cls, text, special_chars=('\n', '"', '\\')):
        # convert baseline text string into a representation but since the
        # representation will be encapsulated in a "raw" triple quoted string,
        # leave newlines, quotes, and backslashes as is.
        try:
            char = special_chars[0]
        except IndexError:
            text = repr(text)[INSIDE_STRING_DELIMETER_SLICE]
        else:
            text = char.join(
                cls._psuedo_repr(chunk, special_chars[1:]) for chunk in text.split(char))
        return text

    def __eq__(self, text):

        # don't baseline trailing whitespace to avoid pylint complaints
        # text = '\n'.join(line.rstrip(' ') for line in text.split('\n'))

        # baselines are special "psuedo" representations, convert to compare
        text = self._psuedo_repr(text)

        # use triple double quote normally, except use triple single quote when
        # triple double quote is present to avoid syntax errors
        quotes = '"""'
        if quotes in text:
            quotes = "'''"
            # handle case where both triple double and triple single quotes are present
            text = text.replace(quotes, r"\'\'\'")

        if ('\n' in text) or text.endswith('\\') or text.endswith(quotes[0]):
            update = 'r' + quotes + '\n' + text + '\n' + quotes
        else:
            update = 'r' + quotes + text + quotes

        self._updates.add(update)

        is_equal = super(Baseline, self).__eq__(text)

        if not is_equal:
            if not self._baselines_to_update:
                atexit.register(Baseline._atexit_callback)

            self._baselines_to_update.add(self)

        return is_equal

    def __hash__(self):
        # provide unique ID to allow Baseline instances to be a part of a set or be used
        # as dictionary keys (otherwise the __eq__ method would be invoked as part of
        # normal set/dict operations and would result in problematic comparisions of
        # unrelated Baseline instances)
        return id(self)

    if sys.version_info.major < 3:
        def __ne__(self, text):
            # for use with assertNotEqual( ) for internal regression test purposes
            return not (self == text)

    @property
    def z__update(self):
        # sort updates so Python hash seed has no impact on internal regression test
        update = '\n'.join(sorted(self._updates))
        indent = ' ' * self._indent
        lines = [(indent + line).rstrip() for line in update.split('\n')]
        if len(lines) > 1:
            lines = [''] + lines
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
