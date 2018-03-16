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
from unittest import TestCase
from unittest.mock import Mock

import baseline
from baseline import Baseline, rstrip

from . import endswith
from . import indents
from . import raw
from . import simple
from . import special
from . import whitespace

SEP = '\n' + baseline._baseline.SEPARATOR + '\n'
Script = baseline._script.Script


# suppress file writes
Script.TEST_MODE = True


class BaseTestCase(TestCase):

    """Base class for all test cases."""

    def setUp(self):
        """Do preparations for a test case.

         This runs before each test*() method call.

         """
        atexit.register = Mock()

        # save and use our own reference to avoid pylint complaint
        self.atexit_mock = atexit.register

    def tearDown(self):
        """Do clean up after a test case.

         This runs after each test*() method call.

         """
        # clear out record of which baseline instances had a mis-compare
        Baseline._baselines_to_update = set()

        # for each baseline instance, clear out cache of previous comparisons
        for baseline_instance in Baseline._all_instances.values():
            baseline_instance._updates = set()

    def check_updated_files(self, module_ops=None):
        """Check pending file edits match expectations.

        If no module edit operations specified, check that baseline
        utility never registered to execute when the Python interpreter
        exits.  Otherwise check that the registration occurred and execute
        the same logic that was registered. Then check that the registered
        logic performed the expected module edit operations.

        Express the expected module operations expectations as a dictionary.
        Where the key is the module object containing the baseline
        instantiations that are expected to be edited. The dictionary
        value is a list of simple text (search, replace) patterns to apply
        to the original file content to formulate the expected edit.

        :param dict module_ops:
            expected edits in the form: {module: [(search, replace), ...]}

        :raises AssertionError:
            if actual edits do not match expected edits

        """
        if module_ops is None:
            module_ops = {}
            self.atexit_mock.assert_not_called()
        else:
            self.atexit_mock.assert_called_once_with(Baseline._atexit_callback)

        # create lookup dict: absolute path -> module object
        path_to_module = {}
        for module, ops in module_ops.items():
            path = os.path.abspath(module.__file__).replace('.pyc', '.py')
            path_to_module[path] = module

        # execute logic that would have executed at Python interpreter exit
        # (except baseline utility was configured to stops short of actual
        # file write and is designed to return a dictionary of records that
        # contain what would have been written)
        #   key -> script absolute path
        #   value -> Script( ) instance
        updated_scripts = Baseline._atexit_callback()

        # check file list of what baseline utility would have updated
        # meets expectations
        self.assertEqual(sorted(updated_scripts), sorted(path_to_module))

        # for each file expected to change, check that file content baseline
        # utility would have wrote matches expectations
        for path, module in path_to_module.items():

            # get file content baseline utility would have wrote
            actual = '\n'.join(updated_scripts[path].lines)

            # generate expected content from search/replace patterns
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

    """Test "normal" single and multi-line baselines.

    Test baseline object supports equality checks. Test that miscompares
    result in proper edits to the script containing the baseline instance
    that had the miscompare.

    """

    def test_all_equal(self):
        """Test all baseline comparisons are a match.

        Check baseline comparisons return True when compared to a string
        that matches the baselined string. Check that no "atexit" activity
        was registered and no files were updated.

        """
        self.assertEqual(simple.single, 'SINGLE')
        self.assertEqual(simple.multiple, 'LINE 1\nLINE 2\n    LINE 3')
        self.check_updated_files()

    def test_some_equal(self):
        """Test some baseline comparisons are a match and some are not.

        Check baseline comparisons return True when compared to a string
        that matches the baselined string (and returns False when it
        doesn't). Check that the "atexit" registration occurred and that
        the logic normally executed "atexit" results in the expected file
        edits.

        """
        self.assertNotEqual(simple.single, 'SINGLE+')
        self.assertEqual(simple.multiple, 'LINE 1\nLINE 2\n    LINE 3')

        expected_updates = {simple: [('SINGLE', 'SINGLE+')]}

        self.check_updated_files(expected_updates)


class MultipleCompares(BaseTestCase):

    """Test behavior of baseline when it is used more than once."""

    def test_two_dissimiliar(self):
        """Test same baseline compared against two different values.

         Check comparisons meet expectations and that "atexit" registration
         occurred. Check update to baseline includes both versions of
         string.

         """
        single_updates = ['SINGLE', 'SINGLE+']

        self.assertEqual(simple.single, single_updates[0])
        self.assertNotEqual(simple.single, single_updates[1])

        expected_updates = {
            simple:  [('SINGLE', '"""\n"""'.join(single_updates))],
        }

        self.check_updated_files(expected_updates)

    def test_two_same(self):
        """Test same baseline compared against same value twice.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

         """
        self.assertEqual(simple.single, 'SINGLE')
        self.assertEqual(simple.single, 'SINGLE')

        self.check_updated_files()


class BaselineSingleton(BaseTestCase):

    """Test two baseline instantiations at same line result in same instance."""

    def test_same_value(self):
        """Test same baselined text for every call.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        sample_text = "Hello world!"

        baseline1, baseline2 = [Baseline(sample_text) for _ in range(2)]

        self.assertEqual(baseline1, sample_text)
        self.assertEqual(baseline2, sample_text)
        self.assertIs(baseline1, baseline2)

        baseline1, baseline2 = Baseline(sample_text), Baseline(sample_text)

        self.assertEqual(baseline1, sample_text)
        self.assertEqual(baseline2, sample_text)
        self.assertIs(baseline1, baseline2)

        self.check_updated_files()

    def test_differing_value(self):
        """Test differing baselined text for every call.

         Check that exception is raised, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        with self.assertRaises(RuntimeError):
            Baseline('junk1'), Baseline('junk2')

        with self.assertRaises(RuntimeError):
            for text in ['junk1', 'junk2']:
                Baseline(text)

        self.check_updated_files()


class IllegalBaselines(BaseTestCase):

    """Test illegal baseline value formats."""

    def test_both_quote_styles_present(self):
        """Verify exception when both triple quote styles present.

         Check that exception is raised, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        both_styles = Baseline('')
        with self.assertRaises(ValueError):
            self.assertNotEqual(both_styles, '"""' + "'''")

        self.check_updated_files()

    def test_nonblank_first_line(self):
        """Verify exception when first line of baseline value is not blank.

         Check that exception is raised, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        with self.assertRaises(ValueError):
            Baseline("""not blank!
                normal
                """)

        self.check_updated_files()

    def test_nonblank_last_line(self):
        """Verify exception when last line of baseline value is not blank.

         Check that exception is raised, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        with self.assertRaises(ValueError):
            Baseline("""
                normal
                not blank!""")

        self.check_updated_files()

    def test_too_little_indent(self):
        """Verify exception when middle line has less indent than last line.

         Check that exception is raised, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        with self.assertRaises(ValueError):
            Baseline("""
                not indented enough
                    """)

        self.check_updated_files()


class RawStringDesignator(BaseTestCase):

    """Test "r" raw string designator added/removed during an update."""

    def test_adding(self):
        """Test "r" raw string designator added as needed during an update."""
        self.assertNotEqual(raw.lower, r'\ LOWER')
        self.assertNotEqual(raw.upper, r'\ UPPER')
        self.assertNotEqual(raw.missing, r'\ MISSING')

        expected_updates = {
            raw:  [
                ('(r"""LOWER', r'(r"""\ LOWER'),
                ('(R"""UPPER', r'(r"""\ UPPER'),
                ('("""MISSING', r'(r"""\ MISSING'),
            ]}

        self.check_updated_files(expected_updates)

    def test_removal_when_u_escape(self):
        """Test raw string designator removed when backlash "u" present."""
        self.assertNotEqual(raw.lower, 'LOWER\\u')
        self.assertNotEqual(raw.upper, 'UPPER\\U')

        expected_updates = {
            raw:  [
                ('(r"""LOWER', '("""LOWER\\\\u'),
                ('(R"""UPPER', '("""UPPER\\\\U'),
            ]}

        self.check_updated_files(expected_updates)

    def test_removal_when_escaping(self):
        """Test raw string designator removed when escaping needed."""
        self.assertNotEqual(raw.lower, 'LOWER' + chr(0))
        self.assertNotEqual(raw.upper, 'UPPER' + chr(1))
        self.assertNotEqual(raw.missing, 'MISSING' + chr(2))

        expected_updates = {
            raw:  [
                ('(r"""LOWER', r'("""LOWER\x00'),
                ('(R"""UPPER', r'("""UPPER\x01'),
                ('("""MISSING', r'("""MISSING\x02'),
            ]}

        self.check_updated_files(expected_updates)

    def test_removal_when_normal_text(self):
        """Test raw string designator removed when just normal text."""
        self.assertNotEqual(raw.lower, 'LOWER+')
        self.assertNotEqual(raw.upper, 'UPPER+')
        self.assertNotEqual(raw.missing, 'MISSING+')

        expected_updates = {
            raw:  [
                ('(r"""LOWER', '("""LOWER+'),
                ('(R"""UPPER', '("""UPPER+'),
                ('("""MISSING', '("""MISSING+'),
            ]}

        self.check_updated_files(expected_updates)


class EndswithQuoteBackslash(BaseTestCase):

    """Test multi-line format used when necessary to avoid syntax errors.

    When text has no newlines and has a quote or a backslash as the last
    character, multi-line format is used prevent syntax errors during
    updates. Check that format operates correctly for comparisons.

    """

    def test_compare(self):
        """Test comparison with potentially problematic ending character.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        self.assertEqual(endswith.quote, 'ENDSWITH "')
        self.assertEqual(endswith.backslash, 'ENDSWITH \\')
        self.check_updated_files()

    def test_update(self):
        """Test baseline update results in multi-line format to avoid error.

         Check comparisons meet expectations, that "atexit" registration
         occurred, and that file update was in multi-line format to
         avoid a syntax error.

        """
        self.assertNotEqual(endswith.quote, 'ENDSWITH+ "')
        self.assertNotEqual(endswith.backslash, 'ENDSWITH+ \\')
        self.check_updated_files({endswith: [('ENDSWITH', 'ENDSWITH+')]})


class Indents(BaseTestCase):

    """Test indented lines in baselined text compare and updated correctly."""

    sample = '\n'.join([
        'line=1',
        '    line=2',
        '',
        'line=4',
    ])

    sample_update = sample.replace('line=', 'line+=')

    def test_compare(self):
        """Test comparison with lines with varying indentation.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        self.assertEqual(indents.indent0, self.sample)
        self.assertEqual(indents.indent4, self.sample)
        self.check_updated_files()

    def test_update(self):
        """Test baseline update results in relative indentation maintained.

         Check comparisons meet expectations, that "atexit" registration
         occurred, and that file update maintained relative line
         indentation in baseline update.

        """
        self.assertNotEqual(indents.indent0, self.sample_update)
        self.assertNotEqual(indents.indent4, self.sample_update)
        self.check_updated_files({indents: [('line=', 'line+=')]})


class FormatSticks(BaseTestCase):

    """Test that once in indented multi-line format, it stays in that format.

    Test that an update to a multi-line indented baseline value keeps the
    baseline in indented, multi-line form.

    """

    def test_update(self):
        """Test once in indented multi-line format, it stays in that format."""
        self.assertNotEqual(simple.multiple, 'single')

        old_multi_line_value = '\n'.join(
            '    ' + line for line in simple.multiple.split('\n')).strip()

        self.check_updated_files({simple: [(old_multi_line_value, 'single')]})


class SpecialCharacters(BaseTestCase):

    """Test certain characters (or combinations of) are accomodated."""

    double_quote = 'SPECIAL ["]'
    backslash = 'SPECIAL [{}]'.format('\\')
    tab = 'SPECIAL [{}]'.format(chr(9))
    triple_both = 'SPECIAL [{}],[{}]'.format("'''", '"""')
    triple_double = 'SPECIAL ["""]'
    triple_single = "SPECIAL [''']"
    unprintable = 'SPECIAL [{}]'.format(chr(0))
    polish_hello_world = 'SPECIAL [Witaj świecie!]'

    def test_compare(self):
        """Test comparisons with special characters function properly.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        self.assertEqual(special.double_quote, self.double_quote)
        self.assertEqual(special.backslash, self.backslash)
        self.assertEqual(special.tab, self.tab)
        self.assertEqual(special.triple_double, self.triple_double)
        self.assertEqual(special.triple_single, self.triple_single)
        self.assertEqual(special.unprintable, self.unprintable)
        self.assertEqual(special.polish_hello_world, self.polish_hello_world)

        self.check_updated_files()

    def test_update(self):
        """Test updates with special characters accommodated with format.

         Check comparisons meet expectations, that "atexit" registration
         occurred, and that file update created baseline updates that
         accommodate the special characters in the string.

        """
        self.assertNotEqual(
            special.double_quote, self.double_quote.replace('S', '+S'))

        self.assertNotEqual(
            special.backslash, self.backslash.replace('S', '+S'))

        self.assertNotEqual(
            special.tab, self.tab.replace('S', '+S'))

        self.assertNotEqual(
            special.triple_double, self.triple_double.replace('S', '+S'))

        self.assertNotEqual(
            special.triple_single, self.triple_single.replace('S', '+S'))

        self.assertNotEqual(
            special.unprintable, self.unprintable.replace('S', '+S'))

        self.assertNotEqual(
            special.polish_hello_world,
            self.polish_hello_world.replace('S', '+S'))

        # TODO - handle py3 and __future__ in py2 for international characters

        self.check_updated_files({
            special: [
                ('SPECIAL', '+SPECIAL'),
                ('świecie', '\\u015bwiecie')
            ]})


class WhiteSpace(BaseTestCase):

    """Test whitespace supported in baselined strings."""

    def test_compare(self):
        """Test comparisons of strings with blank lines function properly.

         Check comparisons meet expectations, that "atexit" registration
         did not occur, and that no files were to be updated.

        """
        self.assertEqual(whitespace.multiple, 'WHITESPACE\n\n')
        self.check_updated_files()

    def test_update(self):
        """Test updates resulting from comparsions of strings with blank lines.

         Check comparisons meet expectations, that "atexit" registration
         occurred, and that file update created a baseline update with
         the blank lines maintained.

        """
        self.assertNotEqual(whitespace.multiple, 'WHITESPACE+\n\n')

        self.check_updated_files({whitespace: [('WHITESPACE', 'WHITESPACE+')]})


class Stripped(BaseTestCase):

    """Test rstrip() transform cleans whitespace at end of lines."""

    def test_transform(self):
        """Test rstrip() transform function.

        Test that lines passed in with whitespace at the end are returned
        without the whitespace.

        """
        stimulus = 'LINE 1 \nLINE 2\t\n    LINE 3 \t'
        expected = 'LINE 1\nLINE 2\n    LINE 3'
        self.assertEqual(rstrip(stimulus), expected)
