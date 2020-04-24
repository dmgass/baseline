################
[baseline] Usage
################

.. contents::
    :local:


****************
One line Strings
****************

To create a baseline string that contains a special update mechanism,
use triple quotes around the string and instantiate :class:`Baseline`
with it. The resulting Python string object supports natural equality
comparisons:

.. code-block:: python
    :caption: hello.py

    from baseline import Baseline

    expected = Baseline("""Hello""")

    test_string = "Hello World!"

    assert test_string == expected


Run the script and observe that the ``assert`` raises an exception since
the strings are not equal.  Because the comparison failed, the tool located
the triple quoted baseline string in the source file and updated it with the
miscompared value. When the interpretter exited, the tool saved the updated
source file using the file extension ``.update.py``):

.. code-block:: python
    :caption: hello.update.py

    expected = Baseline("""Hello World!""")

    test_string = "Hello World!"

    assert test_string == expected


After reviewing the change with your favorite file differencing tool,
accept the change by either manually overwriting the original file or use
the ``baseline`` command line interface to scan the directory for baseline
update files:

.. code-block:: shell

    $ python -m baseline *
    Found baseline updates for:
      hello.py

    Hit [ENTER] to update, [Ctrl-C] to cancel


Pressing :guilabel:`Enter` causes the tool to overwrite the scripts with
the new baseline updates and remove the temporary `.update.py` files.


******************
Multi-Line Strings
******************

The triple quote usage in the :class:`Baseline` instantiation provides a
consistent search and replace mechanism that supports embedding quotation
marks and newlines within a baselined string. Embedding newlines improves
the strings human readability which makes reviewing updates easier.

For multiline baselined string format, start the string on the line
following the opening triple quote delimiter. Insert a line after the
baselined string content to hold the closing triple quote delimiter.
Indent the closing triple quote delimiter to the indentation level of
the baselined string:

.. code-block:: python

    from baseline import Baseline

    expected = Baseline("""
        THE QUICK BROWN FOX
            JUMPS
        OVER THE LAZY DOG.
        """)

    test_string = "THE QUICK BROWN FOX\n    JUMPS\nOVER THE LAZY DOG."

    assert test_string == expected


The example above executes without an assertion because the tool strips
the leading indentation of every line in the baselined string based on
the indentation of the closing triple quote.


**********
Transforms
**********

Often strings to test against a baseline contain substrings that may vary
from one execution to the next. Before the comparison, normalize the
string by substituting a representative constant value. For example,
use a regular expression to transform a variable time into a constant
value:

.. code-block:: python

    import re
    import time

    from baseline import Baseline


    expected = Baseline("""The time is HH:MM:SS.""")

    test_string = "The time is {}.".format(time.strftime("%H:%M:%S"))

    assert re.sub(r'\d\d:\d\d:\d\d', 'HH:MM:SS', test_string) == expected


If this is a common operation or there are multiple transformations needed,
override the ``TRANSFORMS`` class attribute and list the operations to
be performed. The tool performs each of the operations on the test string
before every comparison.

.. code-block:: python

    import re
    import time

    from baseline import Baseline


    def normalize_time(s):
        return re.sub(r'\d\d:\d\d:\d\d', 'HH:MM:SS', s)


    class NormalizedBaseline(Baseline):

        """Normalized string baseline."""

        TRANSFORMS = [normalize_time]


    expected = NormalizedBaseline("""The time is HH:MM:SS.""")

    test_string = "The time is {}.".format(time.strftime("%H:%M:%S"))

    assert test_string == expected



***************
Tips and Tricks
***************

Quick Tips
==========

- Take your time and be diligent in your review of baseline updates.
  Similar to Python itself, this tool provides a lot of rope, don't hang
  yourself.

- Put comments above the baseline to provide information to a future
  maintainer of the important aspects of the baseline that are the focus
  of the test.

- Feel free to baseline strings with any style triple quotes embedded.
  The tool adjusts and uses the alternative style. If the test string
  contains both styles, transform one style into something else before
  comparison.

- To archive resulting test script updates from a regression test run
  within a continuous integration system, use the ``--movepath`` command
  line option to move updated scripts to a new location instead of
  overwriting the original script. T


Initial Baseline Value
======================

To avoid the work of anticipating the exact content of the string baseline,
specify an empty baseline in multi-line format and set the indentation level
with the closing triple quote:

.. code-block:: python

    from baseline import Baseline

    expected = Baseline("""
        """)

    test_string = "THE QUICK BROWN FOX\n  JUMPS\nOVER THE LAZY DOG."

    assert test_string == expected


Run the script and let the tool fill in the string baseline. Then carefully
review the baseline update and accept.
