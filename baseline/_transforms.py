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

import sys

if sys.version_info.major >= 3:
    INSIDE_STRING_DELIMETER_SLICE = slice(1, -1)
else:
    INSIDE_STRING_DELIMETER_SLICE = slice(2, -1)


def ascii_repr(text):
    r"""Create representation with escaped non-printable characters.

    For example, transform the null character (ASCII code 0) into \x00.
    Transform the tab character into \t. But leave newline characters
    as is.

    :param text: string
    :type text: str or unicode
    :returns: representation
    :rtype: str or unicode

    """
    return _ascii_repr(text)


def _ascii_repr(text, special_chars=('\n', '"', '\\')):
    """ascii_repr() recursive helper.

    Use repr() method to escape non-printable characters. Avoid escaping
    newline, double quotes, and back slashes by removing them first then
    restoring after.

    :param text: string
    :type text: str or unicode
    :param iterable special_chars: characters to remove/restore
    :returns: representation
    :rtype: str

    """
    try:
        char = special_chars[0]
    except IndexError:
        text = repr(text)[INSIDE_STRING_DELIMETER_SLICE]
    else:
        text = char.join(
            _ascii_repr(s, special_chars[1:]) for s in text.split(char))

    return text


def rstrip(text):
    """Strip trailing whitespace from end of each line.

    :param text: string
    :type text: str or unicode
    :returns: transformed string
    :rtype: str

    """
    return '\n'.join(line.rstrip() for line in text.split('\n'))
