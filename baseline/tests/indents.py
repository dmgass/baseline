from baseline import Baseline

indent0 = Baseline(r"""
line=1
    line=2

line=4
""")

indent4 = Baseline(r"""
    line=1
        line=2

    line=4
    """)
