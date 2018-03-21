########
baseline
########

Ease maintenance of baselined strings.

This subpackage offers a mechanism to compare a string against a
baselined copy and update the baseline to match the new value when
a mismatch occurs. The update process includes a separate manual
step to facilitate a review of the change before acceptance.

This facility enables significant streamlining of the creation and
maintenance of tests which compare string output against a baselined
copy. The tool uses multiline string format for baselined strings to
improve readabilty for human review and acceptance of baseline updates.


*****
Usage
*****

To create a baseline string that contains the special update mechanism,
use triple quotes around the string and instantiate :class:`Baseline`
with it. The resulting object is a Python string which naturally supports
equality comparisons. The example below shows a simple use and results
in an :exc:`AssertionError` since the strings to not match.

.. code-block:: python
    :caption: foo.py

    from baseline import Baseline

    expected = Baseline("""The quick brown fox jumps over the lazy dog.""")

    assert expected == "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG."

The baseline string includes a mechanism to locate the triple quoted string
in the source code file. When a comparison against the baseline string fails,
the tool updates the baseline string in the source file and saves a copy of
the source file with the same name (except the file extension is changed to
``.update.py``) when the Python interpretter exits:

.. code-block:: python
    :caption: foo.update.py

    from baseline import Baseline

    expected = Baseline("""THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG.""")

    assert expected == "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG."

After reviewing the change with your favorite file differencing tool,
accept the change by either manually overwritting the original file or use
the |baseline| command line interface to scan the directory for updated
scripts and accept them with your permission:

.. code-block:: shell

    $ python -m baseline *
    Found updates for:
      foo.py

    Hit [ENTER] to update, [Ctrl-C] to cancel

    foo.update.py -> foo.py


The triple quote usage in the :class:`Baseline` instantiation provides a
consistent search and replace mechanism that supports embedding quotation
marks and/or newlines within a baselined string. In the case of newlines,
the triple quotes facilitate the use of multiline string syntax which
typically makes the string more human readable and shortens line lengths.

For multiline baselined string format, start the string on the line
following the opening triple quote delimiter. Insert a line after the
baselined string content to hold the closing triple quote delimiter.
Indent the closing triple quote delimiter to the indentation level of
the baselined string:

.. code-block:: python
    :caption: bar.py

    from baseline import Baseline

    expected = Baseline("""
        THE QUICK BROWN FOX
        JUMPS OVER THE LAZY DOG.
        """)

    assert expected == "THE QUICK BROWN FOX\nJUMPS OVER THE LAZY DOG."

The example above executes without an assertion because the tool strips
the leading indentation of every line in the baselined string based on
the indentation of the closing triple quote.

To avoid carefully anticipating and coding the exact content of the
baselined string, specify an empty baseline in multiline format and
set the indentation level with the closing triple quote. Then let
the tool do the work filling in the baseline:

.. code-block:: python
    :caption: bar.py

    from baseline import Baseline

    expected = Baseline("""
        """)

    assert expected == "THE QUICK BROWN FOX\nJUMPS OVER THE LAZY DOG."


***************
Tips and Tricks
***************

- RawBaseline
- Triple quotes within baseline
- transforms


.. toctree::

    :maxdepth: 2
    :hidden:

    about.rst
    changelog.rst
    install.rst
    reference.rst
