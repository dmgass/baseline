from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

single = Baseline("""SINGLE""")

multiple = Baseline("""
    LINE 1
    LINE 2
        LINE 3
    """)
