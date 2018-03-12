from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import StrippedBaseline

single = StrippedBaseline(r"""SINGLE""")

multiple = StrippedBaseline(r"""
    LINE 1
    LINE 2
        LINE 3
    """)
