from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

indent0 = Baseline("""
line=1
    line=2

line=4
""")

indent4 = Baseline("""
    line=1
        line=2

    line=4
    """)
