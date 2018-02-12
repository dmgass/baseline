from baseline import Baseline


backslash = Baseline(r"""SPECIAL [\]""")

tab = Baseline(r"""SPECIAL [\t]""")

triple_both = Baseline(r'''SPECIAL [\'\'\'],["""]''')

triple_double = Baseline(r'''SPECIAL ["""]''')

triple_single = Baseline(r"""SPECIAL [''']""")

unprintable = Baseline(r"""SPECIAL [\x00]""")

