########################
[baseline] Release Notes
########################

Versions increment per `semver <http://semver.org/>`_.

  .. Note::

    Changes to experimental features only result in a bump of
    the subminor (patch) version, including those introducing
    backwards incompatibility.


*****************
1.2.0 2020-DEC-22
*****************

+ Add ``--force`` command line option to suppress acknowledgement
  prompt.

+ Add Python 3.9 support advertisement. (Regression testing
  added to release process.)

+ Remove Python 3.4 and 3.5 support advertisement. (Regression testing
  removed from release process.) Nothing blocks installation, but no
  promise exists that the package works with those interpreter versions.


*****************
1.1.2 2020-MAY-02
*****************

+ Maintain file permissions and owner (both when generating update
  file and when applying update file to original script). Previously,
  file owner and permissions were set based on permission levels of
  execution context which caused issues when executing under elevated
  permission levels (e.g. sudo).


*****************
1.1.1 2020-MAY-02
*****************

+ Improve experimental feature to support specifying an alternative
  location. Add ``BASELINE_MOVE_UPDATES`` environment variable that
  when set to ``YES``, enables specifying an alternative location to
  write update files. This master switch facilitates allowing CI/CD
  systems to enable the feature while leaving the feature off in
  local development while still using CI/CD resources (e.g. tox).


*****************
1.1.0 2020-MAY-01
*****************

+ Add ``--clean`` (`-c`) option to baseline command line tool to
  remove update files.

+ Add ``--diff`` (`-d`) option to baseline command line tool that
  shows difference and queries for overwrite permission for each
  updated file.

+ Change update file extension to ``.py.update`` so that testing
  frameworks such as ``unittest`` or ``pytest`` ignore them.

+ Add experimental feature to support specifying an alternative
  location to write update files with the ``BASELINE_UPDATES_PATH``
  environment variable. (Note, ``BASELINE_RELPATH_BASE`` must be
  set when using this feature.)

+ Add experimental feature to print contextual differences whenever
  a baseline mis-compare occurs. The feature may be turned on by
  setting the environment variable (``BASELINE_PRINT_DIFFS="YES"``)
  or overriding the class attribute (``Baseline.PRINT_DIFFS = True``).


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
