# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

double_quote = Baseline("""SPECIAL ["]""")

backslash = Baseline("""SPECIAL [\\]""")

tab = Baseline("""SPECIAL [\t]""")

triple_double = Baseline('''SPECIAL ["""]''')

triple_single = Baseline("""SPECIAL [''']""")

unprintable = Baseline("""SPECIAL [\x00]""")

polish_hello_world = Baseline("""SPECIAL [Witaj świecie!]""")
