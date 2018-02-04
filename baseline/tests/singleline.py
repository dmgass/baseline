from baseline import Baseline

global_baseline = Baseline("""Global""")  # left off "r" to test it is inserted


class Class(object):
    baseline = Baseline(
        """Class""")  # left off "r" to test it is inserted


with open(__file__.replace('.pyc', '.py')) as thisfile:
    FILE_TEXT = thisfile.read()
