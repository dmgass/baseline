###############################
[baseline] Easy String Baseline
###############################

.. image:: https://readthedocs.org/projects/baseline/badge/?version=latest
   :target: https://baseline.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/dmgass/baseline.svg?branch=master
   :target: https://travis-ci.org/dmgass/baseline

This tool streamlines creation and maintenance of tests which compare string
output against a baseline. It offers a mechanism to compare a string against
a baselined copy and update the baselined copy to match the new value when a
mismatch occurs. The update process includes a manual step to facilitate a
review of the change before acceptance. The tool uses multi-line string format
for string baselines to improve readability for human review.


***********
Quick Start
***********

Create an empty baseline with a triple quoted multi-line string. Place
the ending triple quote on a separate line and indent it to the level
you wish the string baseline update to be indented to. Add a compare of
the string being tested to the baseline string. Then save the file as
``fox.py``:

.. code-block:: python

    from baseline import Baseline

    expected = Baseline("""
        """)

    test_string = "THE QUICK BROWN FOX\n    JUMPS\nOVER THE LAZY DOG."

    assert test_string == expected


Run ``fox.py`` and observe that the ``assert`` raises an exception since
the strings are not equal.  Because the comparison failed, the tool located
the triple quoted baseline string in the source file and updated it with the
miscompared value. When the interpretter exited, the tool saved the updated
source file but changed the file name to ``fox.update.py``:

.. code-block:: python

    from baseline import Baseline

    expected = Baseline("""
        THE QUICK BROWN FOX
            JUMPS
        OVER THE LAZY DOG.
        """)

    test_string = "THE QUICK BROWN FOX\n    JUMPS\nOVER THE LAZY DOG."

    assert test_string == expected


After reviewing the change with your favorite file differencing tool,
accept the change by either manually overwriting the original file or use
the ``baseline`` command line tool to scan the directory for updated
scripts and accept them:

.. code-block:: shell

    $ python -m baseline *
    Found updates for:
      fox.py

    Hit [ENTER] to update, [Ctrl-C] to cancel

    fox.update.py -> fox.py


Run ``fox.py`` again and observe the ``assert`` does not raise an exception
nor is a source file update generated. If in the future the test value
changes, the ``assert`` will raise an exception and cause a new source file
update to be generated. Simply repeat the review and acceptance step and you
are back in business!
