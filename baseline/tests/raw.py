from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

lower = Baseline(r"""LOWER""")  # lower case "r" present

upper = Baseline(R"""UPPER""")  # upper case "R" present

missing = Baseline("""MISSING""")  # no "raw" designator present
