from __future__ import absolute_import, division, print_function, unicode_literals

from baseline import Baseline

capital = Baseline(R"""CAPITAL""") # capital "R" replaced with lower

single = Baseline("""SINGLE""") # left off "r" to test it is inserted

multiple = Baseline(
    '''
    MULTIPLE
    """"""""
    ''')  # left off "r" to test it is inserted
