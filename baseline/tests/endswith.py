from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

quote = Baseline("""
    ENDSWITH "
    """)

backslash = Baseline(r"""
    ENDSWITH \
    """)
