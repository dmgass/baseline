from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

single = Baseline(r"""WHITESPACE""")

multiple = Baseline(r"""
    WHITESPACE


    """)
