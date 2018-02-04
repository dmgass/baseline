# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2018 Daniel Mark Gass
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import difflib
import importlib
import os
from unittest import TestCase, main

import baseline
from baseline import Baseline

SEPARATOR = getattr(baseline, '_baseline').SEPARATOR
Script = getattr(baseline, '_script').Script

# this test calls callback directly to evaluate correct behavior of baseline facility,
# don't let test cases cause callback call at this script's exit
Baseline.z__registered_atexit = True

# suppress file writes
Script.TEST_MODE = True

singleline = importlib.import_module('singleline')
multiline = importlib.import_module('multiline')

single_key = os.path.abspath(singleline.__file__).replace('.pyc', '.py')
multi_key = os.path.abspath(multiline.__file__).replace('.pyc', '.py')


class Test1(TestCase):

    def tearDown(self):
        Baseline.z__updated_scripts = {}
        Baseline.z__unequal_baselines = set()
        for baseline_instance in Baseline._all_instances.itervalues():
            baseline_instance._updates = set()

    def check_updated_files(self, expected):
        Baseline.z__atexit_callback()

        updated_scripts = Baseline.z__updated_scripts

        updated_script_paths = sorted(updated_scripts.keys())
        self.assertEqual(updated_script_paths, sorted(expected))

        for path, expect_content in expected.iteritems():

            actual_content = '\n'.join(updated_scripts[path].lines)

            if actual_content != expect_content:
                print ' ACTUAL ({}) '.format(path).center(120, '*')
                print actual_content
                print ' EXPECT ({}) '.format(path).center(120, '*')
                print expect_content
                print ' DIFFS ({}) '.format(path).center(120, '*')
                print ''.join(difflib.ndiff(
                    expect_content.splitlines(True),
                    actual_content.splitlines(True)))
                print '*' * 120

            self.assertTrue(actual_content == expect_content)

    def test_some_compares(self):
        self.assertEqual(singleline.global_baseline, 'Global')
        self.assertEqual(multiline.Class.baseline, 'Class 1\n    Class 1a\nClass 2')

        self.check_updated_files({})

    def test_all_equal(self):
        self.assertEqual(singleline.global_baseline, 'Global')
        self.assertEqual(singleline.Class.baseline, 'Class')
        self.assertEqual(multiline.global_baseline, 'Global 1\nGlobal 2\n    Global 2a')
        self.assertEqual(multiline.Class.baseline, 'Class 1\n    Class 1a\nClass 2')

        self.check_updated_files({})

    def test_some_equal(self):
        self.assertNotEqual(singleline.global_baseline, 'Global+')
        self.assertEqual(singleline.Class.baseline, 'Class')
        self.assertNotEqual(
            multiline.global_baseline, 'Global+ 1\nGlobal+ 2\n    Global+ 2a')
        self.assertEqual(multiline.Class.baseline, 'Class 1\n    Class 1a\nClass 2')

        expected_updates = {
            single_key: singleline.FILE_TEXT.replace('"""Global"""', 'r"""Global+"""'),
            multi_key: multiline.FILE_TEXT.replace('Global', 'Global+'),
        }

        self.check_updated_files(expected_updates)

    def test_varying_compares(self):
        self.assertNotEqual(singleline.global_baseline, 'Global+')
        self.assertNotEqual(singleline.global_baseline, 'Global++')
        new_str = '\n'.join([
            'r"""',
            'Global+',
            SEPARATOR.strip(),
            'Global++',
            '"""',
        ])

        expected_updates = {
            single_key: singleline.FILE_TEXT.replace('"""Global"""', new_str),
        }
        self.check_updated_files(expected_updates)


if __name__ == '__main__':
    main()
