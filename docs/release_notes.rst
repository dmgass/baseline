########################
[baseline] Release Notes
########################

Versions are incremented according to `semver <http://semver.org/>`_.

***
0.1
***

+ 0.1.0 (2018-03-25)
    - Initial "beta" release.

+ 0.1.1 (2018-03-25)
    - Change author to match PyPi user name.

+ 0.1.2 (2018-03-27)
    - Add Travis C/I support.
    - Change author name to commonly used form.
    - Use Python 3.5 in tox for basic tasks.
    - Remove "beta" label.

+ 0.1.3 (2018-03-29)
    - Show command line help dump in API reference documentation.
    - Fix development status classifier in setup configuration
      (to make PyPi listing accurate).

+ 0.1.4 (2018-04-01)
    - Fix anomaly where spaces at the end of a line were removed when
      when updating a string baseline. The incorrect removal of the
      spaces caused comparisons of the string with end of line spaces
      against the baseline to fail. Now the tool retains the spaces
      when updating baseline strings so that comparisons of the string
      with end of line spaces against the baseline pass.
