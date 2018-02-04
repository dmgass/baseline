from baseline import Baseline

global_baseline = Baseline(r"""
    Global 1
    Global 2
        Global 2a
    """)


class Class(object):

    baseline = Baseline(
        r"""
        Class 1
            Class 1a
        Class 2
        """)


with open(__file__.replace('.pyc', '.py')) as thisfile:
    FILE_TEXT = thisfile.read()
