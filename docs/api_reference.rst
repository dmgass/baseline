########################
[baseline] API Reference
########################

.. contents::
    :local:


*******
Classes
*******

.. currentmodule:: baseline

.. autoclass:: Baseline



************
Command Line
************

.. code-block:: shell

    $ python -m baseline --help
    usage: baseline [-h] [-w] [path [path ...]]

    Locate scripts with baseline updates within the paths specified and modify the
    scripts with the updates found. (The scripts to be modified will be summarized
    and you will be offered a chance to cancel before files are changed.)

    positional arguments:
      path        module or directory path

    optional arguments:
      -h, --help  show this help message and exit
      -w, --walk  recursively walk directories
