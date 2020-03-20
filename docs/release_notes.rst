########################
[baseline] Release Notes
########################

Versions increment per `semver <http://semver.org/>`_.


*****************
1.0.0 2020-MAR-19
*****************

+ Improve baseline update when multiple values compared against the
  same baseline. Generate a single multi-line baseline with headers
  between the various alternative values. This facilitates updating
  the baseline again.

+ Support Python 3.8. Previously, when run using 3.8, the baseline
  update tool misplaced baseline updates in the first triple quoted
  string found above the baseline. (Python 3.8 stack frames now
  report the line number of the first line in a statement rather
  than the last.)

+ Change behavior of ``Baseline`` to use raw strings when updating
  baselines when possible and improves readability.

+ Deprecate ``RawBaseline`` since ``Baseline`` now incorporates
  its behavior.


*************
Beta Releases
*************

+ 0.2.1 (2018-05-19)
    - Fix command line tool to not raise UnboundedLocalError exception.
      Previously when tool was invoked with a wild card that yielded
      no baseline updates to move, an exception was unexpectedly raised.

+ 0.2.0 (2018-05-18)
    - Add ``--movepath`` command line option to move updated scripts to
      a new location instead of overwriting the original script (for
      use in continuous integration systems performing regression tests).

+ 0.1.3 (2018-03-29)
    - Show command line help dump in API reference documentation.
    - Fix development status classifier in setup configuration
      (to make PyPi listing accurate).

+ 0.1.2 (2018-03-27)
    - Add Travis C/I support.
    - Change author name to commonly used form.
    - Use Python 3.5 in tox for basic tasks.
    - Remove "beta" label.

+ 0.1.1 (2018-03-25)
    - Change author to match PyPi user name.

+ 0.1.0 (2018-03-25)
    - Initial "beta" release.
