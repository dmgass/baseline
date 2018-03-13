# -*- coding: utf-8 -*-

# avoid use of "from __future__ import unicode_literals" when using ASCII,
# otherwise even with r"..." designation the \u0000 is encoded into a character
from __future__ import absolute_import, division, print_function

from baseline import AsciiBaseline

double_quote = AsciiBaseline(r"""SPECIAL ["]""")

backslash = AsciiBaseline(r"""SPECIAL [\]""")

tab = AsciiBaseline(r"""SPECIAL [\t]""")

unprintable = AsciiBaseline(r"""SPECIAL [\x00]""")

polish_hello_world = AsciiBaseline(r"""SPECIAL [Witaj \u015bwiecie!]""")
