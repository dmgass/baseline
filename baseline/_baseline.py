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

import atexit
import inspect
import os
import sys

from ._script import Script

PY2 = sys.version_info.major < 3
if PY2:  # pragma: no cover
    ascii = repr


SEPARATOR = '\n' + '*' * 40 + '\n'

baseclass = type(u"")

RAW_MULTILINE_CHARS = ('\n', '"', '\\')


def multiline_repr(text, special_chars=('\n', '"')):
    """Get string representation for triple quoted context.

    Make string representation as normal except do not transform
    "special characters" into an escaped representation to support
    use of the representation in a triple quoted multi-line string
    context (to avoid escaping newlines and double quotes).

     Pass ``RAW_MULTILINE_CHARS`` as the ``special_chars`` when use
     context is a "raw" triple quoted string (to also avoid excaping
     backslashes).

    :param text: string
    :type text: str or unicode
    :param iterable special_chars: characters to remove/restore
    :returns: representation
    :rtype: str

    """
    try:
        char = special_chars[0]
    except IndexError:
        text = ascii(text)[2 if PY2 else 1:-1]
    else:
        text = char.join(
            multiline_repr(s, special_chars[1:]) for s in text.split(char))

    return text


class Baseline(baseclass):

    """Baselined string.

    Support comparison of a string against this baseline. When the comparison
    results in a mismatch, make a copy of the Python script containing the
    baseline and modify the baseline to match the new value.

    """
    TRANSFORMS = []

    _AVOID_RAW_FORM = True

    # set of instances of this class where a string comparison against the
    # baseline was a mismatch
    _baselines_to_update = set()

    # dictionary of every unique source code location of Baseline instantiation
    # key: source code location of Baseline instantiation (abs path, linenum)
    # value: Baseline instance for a particular location
    _all_instances = {}

    # set of strings compared against this baseline (all Baseline instances
    # override this attribute with a set() specific to it, it is present as
    # a class attribute for documentation and pylint warning suppression)
    _updates = None

    @staticmethod
    def _dedent(text):
        """Remove common indentation from each line in a text block.

        When text block is a single line, return text block. Otherwise
        determine common indentation from last line, strip common
        indentation from each line, and return text block consisting of
        inner lines (don't include first and last lines since they either
        empty or contain whitespace and are present in baselined
        string to make them pretty and delineate the common indentation).

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
        Remove whitespace used to make the string look pretty in the
        source file (i.e. when multi-line, remove common indentation
        as well as the first and last lines).

        :param text: baselined string representation
        :type text: str or unicode
        :returns: normalized string representation
        :raises RuntimeError: when text differs for a specific location

        """
        frame = inspect.getouterframes(inspect.currentframe())[1]
        path = os.path.abspath(frame[1])
        linenum = frame[2]

        key = (path, linenum)

        try:
            self = cls._all_instances[key]
        except KeyError:
            indent, dedented_text = cls._dedent(text)
            self = super(Baseline, cls).__new__(cls, dedented_text)
            cls._all_instances[key] = self

            # initialize instance here instead of __init__ to avoid:
            #   (1) reinitializing when returning a pre-existing instance
            #   (2) recomputing path and linenum (or corrupting class signature
            #       by passing them to __init__)
            self.z__path = path
            self.z__linenum = linenum
            self._indent = indent
            self._updates = set()

        else:
            if baseclass.__ne__(self, text):
                raise RuntimeError('varying baseline text not allowed')

        return self

    def __eq__(self, text):
        """Compare string against baseline.

        Save a copy of the string in order to later update the string
        in the source code file in the event any comparison against
        this baseline fails.

        :param str text: string to compare against baseline
        :returns: indication if string matches baseline
        :rtype: bool

        """
        for transform in self.TRANSFORMS:
            text = transform(text)

        # use triple double quote, except use triple single quote when
        # triple double quote is present to avoid syntax errors
        if '"""' in text and "'''" in text:
            raise ValueError(
                'Both triple quote styles exist in string, '
                'replace either """ or {} before baselining'.format("'''"))

        # Save a copy of the string in order to later update the string
        # in the source code file in the event any comparison against
        # this baseline fails.
        self._updates.add(text)

        is_equal = super(Baseline, self).__eq__(text)

        if not is_equal:
            if not self._baselines_to_update:
                atexit.register(Baseline._atexit_callback)

            self._baselines_to_update.add(self)

        return is_equal

    def __ne__(self, other):
        # not necessary for Python 3 or greater, but override for Python 2
        # for use in regression test where assertNotEqual() is used
        eq = self.__eq__(other)
        return NotImplemented if eq is NotImplemented else not eq

    def __hash__(self):
        # provide unique ID to allow Baseline instances to be a part of a set
        # or be used as dictionary keys (otherwise the __eq__ method would be
        # invoked as part of normal set/dict operations and would result in
        # problematic comparisions of unrelated Baseline instances)
        return id(self)

    @property
    def z__update(self):
        """Triple quoted baseline representation.

        Return string with multiple triple quoted baseline strings when
        baseline had been compared multiple times against varying strings.

        :returns: source file baseline replacement text
        :rtype: str

        """
        updates = []

        for text in self._updates:

            if self._AVOID_RAW_FORM:
                text_repr = multiline_repr(text)
                raw_char = ''
            else:
                text_repr = multiline_repr(text, RAW_MULTILINE_CHARS)

                if len(text_repr) == len(text):
                    raw_char = 'r' if '\\' in text_repr else ''
                else:
                    # must have special characters that required added backslash
                    # escaping, use normal representation to get backslashes right
                    text_repr = multiline_repr(text)
                    raw_char = ''

            # use triple double quote, except use triple single quote when
            # triple double quote is present to avoid syntax errors
            quotes = '"""'
            if quotes in text:
                quotes = "'''"

            # Wrap with blank lines when multi-line or when text ends with
            # characters that would otherwise result in a syntax error in
            # the formatted representation.
            multiline = self._indent or ('\n' in text)
            if multiline or text.endswith('\\') or text.endswith(quotes[0]):
                update = raw_char + quotes + '\n' + text_repr + '\n' + quotes
            else:
                update = raw_char + quotes + text_repr + quotes

            updates.append(update)

        # sort updates so Python hash seed has no impact on regression test
        update = '\n'.join(sorted(updates))

        indent = ' ' * self._indent

        lines = ((indent + line).rstrip() for line in update.split('\n'))

        return '\n'.join(lines).lstrip()

    @classmethod
    def _atexit_callback(cls):
        """Create Python script copies with updated baselines.

        For any baseline that had a miscompare, make a copy of the
        source file which contained the baseline and update the
        baseline with the new string value.

        :returns:
            record of every Python file update (key=path,
            value=script instance)
        :rtype: dict

        """
        updated_scripts = {}

        for baseline in cls._baselines_to_update:

            if baseline.z__path.endswith('<stdin>'):
                continue

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
