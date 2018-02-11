from baseline import Baseline


unprintable = Baseline(r"""\x00hello\x01""")

both_quotes = Baseline(r"""'hello' "world\"""")



with open(__file__.replace('.pyc', '.py')) as thisfile:
    FILE_TEXT = thisfile.read()
