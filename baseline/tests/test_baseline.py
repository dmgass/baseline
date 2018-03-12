# -*- coding: utf-8 -*-
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

from __future__ import absolute_import, division, print_function, unicode_literals

import atexit
import difflib
import importlib
import io
import os
import sys
from unittest import TestCase, main

import baseline

from baseline import Baseline, ascii_repr

if sys.version_info.major >= 3:
    from unittest.mock import Mock
else:
    from mock import Mock

SEP = '\n' + getattr(baseline, '_baseline').SEPARATOR + '\n'
Script = getattr(baseline, '_script').Script


# suppress file writes
Script.TEST_MODE = True

endswith = importlib.import_module('endswith')
indents = importlib.import_module('indents')
raw = importlib.import_module('raw')
simple = importlib.import_module('simple')
special = importlib.import_module('special')
whitespace = importlib.import_module('whitespace')


class BaseTestCase(TestCase):

    def setUp(self):
        self.atexit_mock = Mock()
        atexit.register = self.atexit_mock

    def tearDown(self):
        Baseline._baselines_to_update = set()
        for baseline_instance in Baseline._all_instances.values():
            baseline_instance._updates = set()

    def check_updated_files(self, module_ops=None):

        if module_ops is None:
            module_ops = {}
            self.atexit_mock.assert_not_called()
        else:
            self.atexit_mock.assert_called_once_with(Baseline._atexit_callback)

        updated_scripts = Baseline._atexit_callback()

        path_to_module = {}
        for module, ops in module_ops.items():
            path = os.path.abspath(module.__file__).replace('.pyc', '.py')
            path_to_module[path] = module

        self.assertEqual(sorted(updated_scripts), sorted(path_to_module))

        for path, module in path_to_module.items():
            actual = '\n'.join(updated_scripts[path].lines)
            with io.open(path, 'r', encoding='utf-8') as handle:
                expect = handle.read()

            for pattern, replacement in module_ops[module]:
                expect = expect.replace(pattern, replacement)

            if actual != expect:
                title_len = 120
                print(' ACTUAL ({}) '.format(path).center(title_len, '*'))
                print(actual)
                print(' EXPECT ({}) '.format(path).center(title_len, '*'))
                print(expect)
                print(' DIFFS ({}) '.format(path).center(title_len, '*'))
                print(''.join(difflib.ndiff(
                    expect.splitlines(True),
                    actual.splitlines(True))))
                print('*' * title_len)

            self.assertTrue(actual == expect)


class NormalUse(BaseTestCase):

    def test_all_equal(self):
        self.assertEqual(simple.single, 'SINGLE')
        self.assertEqual(simple.multiple, 'LINE 1\nLINE 2\n    LINE 3')

        self.check_updated_files()

    def test_some_equal(self):
        self.assertNotEqual(simple.single, 'SINGLE+')
        self.assertEqual(simple.multiple, 'LINE 1\nLINE 2\n    LINE 3')
        # self.assertNotEqual(
        #     multiline.global_baseline, 'Global+ 1\nGlobal+ 2\n    Global+ 2a')
        # self.assertEqual(multiline.Class.baseline, 'Class 1\n    Class 1a\nClass 2')

        expected_updates = {
            simple:  [
                ('SINGLE', 'SINGLE+')],
            # multi_key: multiline.FILE_TEXT.replace('Global', 'Global+'),
        }

        self.check_updated_files(expected_updates)


class MultipleCompares(BaseTestCase):

    def test_two_dissimiliar(self):
        single_updates = ['SINGLE', 'SINGLE+']

        self.assertEqual(simple.single, single_updates[0])
        self.assertNotEqual(simple.single, single_updates[1])

        expected_updates = {
            simple:  [('SINGLE', '"""\nr"""'.join(single_updates))],
        }

        self.check_updated_files(expected_updates)

    def test_two_same(self):
        self.assertEqual(simple.single, 'SINGLE')
        self.assertEqual(simple.single, 'SINGLE')

        self.check_updated_files()

class BaselineSingleton(BaseTestCase):

    def test_same_value(self):

        sample_text = "Hello world!"
        baseline1, baseline2 = Baseline(sample_text), Baseline(sample_text)

        self.assertEqual(baseline1, sample_text)
        self.assertEqual(baseline2, sample_text)
        self.assertIs(baseline1, baseline2)

        self.check_updated_files()

    def test_diff_value(self):

        with self.assertRaises(RuntimeError):
            Baseline('junk1'), Baseline('junk2')

        self.check_updated_files()


# TODO - test AsciiBaseline
# TODO - test StrippedBaseline
# TODO - add test case to go from multi-line with indent to single line

class IllegalBaselines(BaseTestCase):

    def test_nonblank_first_line(self):

        with self.assertRaises(ValueError):
            Baseline("""not blank!
                normal
                """)

        self.check_updated_files()

    def test_nonblank_last_line(self):

        with self.assertRaises(ValueError):
            Baseline("""
                normal
                not blank!""")

        self.check_updated_files()

    def test_too_little_indent(self):

        with self.assertRaises(ValueError):
            Baseline("""
                not indented enough
                    """)

        self.check_updated_files()


class RawStringDesignator(BaseTestCase):

    def test_update(self):
        """Test "r" raw string designator added during an update."""
        self.assertNotEqual(raw.capital, 'CAPITAL+')
        self.assertNotEqual(raw.single, 'SINGLE+')
        self.assertNotEqual(raw.multiple, 'MULTIPLE+\n""""""""')

        expected_updates = {
            raw:  [
                ('(R"""CAPITAL', '(r"""CAPITAL+'),
                ('("""SINGLE', '(r"""SINGLE+'),
                ("'''\n", "r'''\n"),
                ("MULTIPLE", "MULTIPLE+")
            ]}
        self.check_updated_files(expected_updates)


class EndswithQuoteBackslash(BaseTestCase):

    def test_compare(self):
        """Test quote and backslash at end of single line compares.

        When text has no newlines and has a quote or a backslash as the last
        character, multiline is used prevent syntax errors. Check that format
        operates correctly for comparisons.

        """
        self.assertEqual(endswith.quote, 'ENDSWITH "')
        self.assertEqual(endswith.backslash, 'ENDSWITH \\')

        self.check_updated_files()

    def test_update(self):
        """Test quote and backslash at end of single line text updated as multiline.

        When text has no newlines and has a quote or a backslash as the last
        character, ensure update formatted as multiline to prevent syntax errors

        """
        self.assertNotEqual(endswith.quote, 'ENDSWITH+ "')
        self.assertNotEqual(endswith.backslash, 'ENDSWITH+ \\')

        self.check_updated_files({endswith: [('ENDSWITH', 'ENDSWITH+')]})


class Indents(BaseTestCase):

    sample = '\n'.join([
        'line=1',
        '    line=2',
        '',
        'line=4',
    ])

    sample_update = sample.replace('line=', 'line+=')

    def test_compare(self):
        self.assertEqual(indents.indent0, self.sample)
        self.assertEqual(indents.indent4, self.sample)

        self.check_updated_files()

    def test_update(self):
        self.assertNotEqual(indents.indent0, self.sample_update)
        self.assertNotEqual(indents.indent4, self.sample_update)

        self.check_updated_files({indents: [('line=', 'line+=')]})


class SpecialCharacters(BaseTestCase):

    double_quote = 'SPECIAL ["]'
    backslash = 'SPECIAL [{}]'.format('\\')
    tab = 'SPECIAL [{}]'.format(chr(9))
    triple_both = 'SPECIAL [{}],[{}]'.format("'''", '"""')
    triple_double = 'SPECIAL ["""]'
    triple_single = "SPECIAL [''']"
    unprintable = 'SPECIAL [{}]'.format(chr(0))
    polish_hello_world = 'SPECIAL [Witaj świecie!]'

    def test_compare(self):
        self.assertEqual(special.double_quote, self.double_quote)
        self.assertEqual(special.backslash, self.backslash)
        self.assertEqual(special.tab, ascii_repr(self.tab))
        self.assertEqual(special.triple_both, self.triple_both)
        self.assertEqual(special.triple_double, self.triple_double)
        self.assertEqual(special.triple_single, self.triple_single)
        self.assertEqual(special.unprintable, ascii_repr(self.unprintable))
        self.assertEqual(special.polish_hello_world, self.polish_hello_world)

        self.check_updated_files()

    def test_update(self):
        self.assertNotEqual(special.double_quote, self.double_quote.replace('S', '+S'))
        self.assertNotEqual(special.backslash, self.backslash.replace('S', '+S'))
        self.assertNotEqual(special.tab, ascii_repr(self.tab.replace('S', '+S')))
        self.assertNotEqual(special.triple_both, self.triple_both.replace('S', '+S'))
        self.assertNotEqual(special.triple_double, self.triple_double.replace('S', '+S'))
        self.assertNotEqual(special.triple_single, self.triple_single.replace('S', '+S'))
        self.assertNotEqual(special.unprintable, ascii_repr(self.unprintable.replace('S', '+S')))
        self.assertNotEqual(special.polish_hello_world, self.polish_hello_world.replace('S', '+S'))

        self.check_updated_files({special: [('SPECIAL', '+SPECIAL')]})


class WhiteSpace(BaseTestCase):

    def test_compare(self):
        self.assertEqual(whitespace.single, 'WHITESPACE')
        # self.assertEqual(whitespace.single, 'WHITESPACE ')
        self.assertEqual(whitespace.multiple, 'WHITESPACE\n\n')
        # self.assertEqual(whitespace.multiple, 'WHITESPACE\n  \n  ')

        self.check_updated_files()

    def test_update(self):
        self.assertNotEqual(whitespace.single, 'WHITESPACE+')
        self.assertNotEqual(whitespace.multiple, 'WHITESPACE+\n\n')

        self.check_updated_files({whitespace: [('WHITESPACE', 'WHITESPACE+')]})


if __name__ == '__main__':
    main()
