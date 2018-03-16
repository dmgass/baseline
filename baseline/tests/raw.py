from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import RawBaseline

lower = RawBaseline(r"""LOWER""")  # lower case "r" present

upper = RawBaseline(R"""UPPER""")  # upper case "R" present

missing = RawBaseline("""MISSING""")  # no "raw" designator present
