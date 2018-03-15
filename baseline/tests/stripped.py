from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import StrippedBaseline

single = StrippedBaseline("""SINGLE""")

multiple = StrippedBaseline("""
    LINE 1
    LINE 2
        LINE 3
    """)
