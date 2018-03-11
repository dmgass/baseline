from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

double_quote = Baseline(r"""SPECIAL ["]""")

backslash = Baseline(r"""SPECIAL [\]""")

tab = Baseline(r"""SPECIAL [\t]""")

triple_both = Baseline(r'''SPECIAL [\'\'\'],["""]''')

triple_double = Baseline(r'''SPECIAL ["""]''')

triple_single = Baseline(r"""SPECIAL [''']""")

unprintable = Baseline(r"""SPECIAL [\x00]""")

