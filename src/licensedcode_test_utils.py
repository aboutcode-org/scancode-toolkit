#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os
import traceback
from time import time

import attr
import pytest
import saneyaml
from license_expression import Licensing

from commoncode import text
from commoncode.testcase import get_test_file_pairs

from scancode_config import REGEN_TEST_FIXTURES

"""
Data-driven tests using expectations stored in YAML files.
"""


@attr.attrs(slots=True)
class LicenseTest(object):
    """
    A license detection test is used to verify that license detection works
    correctly

    It consists of two files with the same base name: a .yml file with test data
    and a test file with any other extension that needs to be tested for
    detection

    The following data are loaded from the .yml file:
     - a test file to scan for licenses,
     - a list of expected licenses expressions to detect
     - optional notes.
     - a boolean flag expected_failure set to True if a test is expected to fail
       for now.

    If the list of license expressions is empty, then this test should not
    detect any license in the test file.
    """
    data_file = attr.attrib(default=None)
    test_file = attr.attrib(default=None)
    test_file_name = attr.attrib(default=None)
    license_expressions = attr.attrib(default=attr.Factory(list))
    notes = attr.attrib(default=None)
    expected_failure = attr.attrib(default=False)
    language = attr.attrib(default='en')

    licensing = Licensing()

    def __attrs_post_init__(self, *args, **kwargs):
        if self.test_file:
            _, _, self.test_file_name = self.test_file.partition(
                os.path.join('licensedcode', 'data') + os.sep)

        data = {}
        if self.data_file:
            try:
                with io.open(self.data_file, encoding='utf-8') as df:
                    data = saneyaml.load(df.read()) or {}
            except Exception as e:
                raise Exception(f'Failed to read: file://{self.data_file}', e)

            self.license_expressions = data.pop('license_expressions', [])
            self.language = data.pop('language', 'en')
            self.notes = data.pop('notes', None)
            # True if the test is expected to fail
            self.expected_failure = data.pop('expected_failure', False)

        if data:
            raise Exception(
                'Unknown data elements: ' + repr(data) +
                ' for: file://' + self.data_file)

        if self.license_expressions:
            for i, exp in enumerate(self.license_expressions[:]):
                try:
                    expression = self.licensing.parse(exp)
                except:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        f'{exp!r} for: file://{self.data_file}\n' +
                        traceback.format_exc()
                    )
                if expression is None:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        f'{exp!r} for: file://{self.data_file}'
                    )
                new_exp = expression.render()
                self.license_expressions[i] = new_exp

        else:
            if not self.notes:
                raise Exception(
                    'A license test without expected license_expressions should '
                    f'have explanatory notes:  for: file://{self.data_file}'
                )

    def to_dict(self):
        dct = {}
        if self.license_expressions:
            dct['license_expressions'] = self.license_expressions
        if self.language and self.language != 'en':
            dct['language'] = self.language
        if self.expected_failure:
            dct['expected_failure'] = self.expected_failure
        if self.notes:
            dct['notes'] = self.notes
        return dct

    def dump(self):
        """
        Dump a representation of self to its YAML data file
        """
        as_yaml = saneyaml.dump(self.to_dict())
        with io.open(self.data_file, 'w', encoding='utf-8') as df:
            df.write(as_yaml)

    def get_content(self):
        """
        Return a byte strings of the test file content.
        """
        with open(self.test_file, 'rb') as df:
            d = df.read()
        return d

    def get_test_method_name(self, prefix='test_detection_'):
        test_file_name = self.test_file_name
        test_name = '{prefix}{test_file_name}'.format(**locals())
        test_name = text.python_safe_name(test_name)
        if not isinstance(test_name, str):
            test_name = test_name.decode('utf-8')
        return test_name

    @staticmethod
    def load_from(test_dir):
        """
        Return an iterable of LicenseTest objects loaded from `test_dir`
        """
        return [
            LicenseTest(data_file, test_file)
            for data_file, test_file
            in get_test_file_pairs(test_dir)
        ]


def build_tests(test_dir, clazz, unknown_detection=False, regen=REGEN_TEST_FIXTURES):
    """
    Dynamically build license_test methods from a sequence of LicenseTest and
    attach these method to the clazz license test class.
    """

    license_tests = LicenseTest.load_from(test_dir)

    # TODO: check that we do not have duplicated tests with same data and text

    for license_test in license_tests:
        test_name = license_test.get_test_method_name()
        test_file = license_test.test_file

        # closure on the license_test params
        test_method = make_test(
            license_test,
            unknown_detection=unknown_detection,
            regen=regen,
        )

        # avoid duplicated test method
        if hasattr(clazz, test_name):
            msg = (
                f'Duplicated test method name: {test_name}: file://{test_file}'
            )
            raise Exception(msg)

        # attach that method to our license_test class
        setattr(clazz, test_name, test_method)


def make_test(license_test, unknown_detection=False, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments for a
    license_test LicenseTest object.
    """
    test_name = license_test.get_test_method_name()

    from licensedcode import cache
    from licensedcode.tracing import get_texts

    expected_expressions = license_test.license_expressions or []

    test_file = license_test.test_file
    test_data_file = license_test.data_file
    expected_failure = license_test.expected_failure

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(
            location=test_file,
            min_score=0,
            unknown_licenses=unknown_detection,
        )
        if not matches:
            matches = []

        detected_expressions = [match.rule.license_expression for match in matches]

        # use detection as expected and dump test back
        if regen:
            if not expected_failure:
                license_test.license_expressions = detected_expressions
            license_test.dump()
            return

        if detected_expressions != expected_expressions:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            expected = expected_expressions + ['======================', '']
            results_failure_trace = (
                detected_expressions[:]
                +['======================', '']
            )

            for match in matches:
                qtext, itext = get_texts(match)
                rule_file = match.rule.rule_file()
                results_failure_trace.extend(['',
                    '======= MATCH ====', repr(match),
                    '======= Matched Query Text for:',
                    f'file://{test_file}'
                ])
                if test_data_file:
                    results_failure_trace.append(f'file://{test_data_file}')

                results_failure_trace.append('')
                results_failure_trace.append(qtext)
                results_failure_trace.extend(['',
                    '======= Matched Rule Text for:',
                    f'file://{rule_file}',
                    '',
                    itext,
                ])
            if not matches:
                results_failure_trace.extend(['',
                    '======= NO MATCH ====',
                    '======= Not Matched Query Text for:',
                    f'file://{test_file}'
                ])
                if test_data_file:
                    results_failure_trace.append(f'file://{test_data_file}')

            # this assert will always fail and provide a detailed failure trace
            assert '\n'.join(results_failure_trace) == '\n'.join(expected)

    closure_test_function.__name__ = test_name

    if expected_failure:
        closure_test_function = pytest.mark.xfail(closure_test_function)  # NOQA

    return closure_test_function

# A small legalese to use in tests. This must be a sorted mapping of common
# license-specific words aka. legalese as {token: id}
# see legalese.py on how to re-create and update this mapping


mini_legalese = {
    'accordance': 0,
    'according': 1,
    'accused': 2,
    'acknowledgement': 3,
    'admission': 4,
    'admitted': 5,
    'agreement': 6,
    'alleged': 7,
    'allowance': 8,
    'alternatively': 9,
    'assessment': 10,
    'assessments': 11,
    'choices': 12,
    'complementary': 13,
    'complications': 14,
    'covered': 15,
    'damages': 16,
    'determines': 17,
    'distribute': 18,
    'distribution': 19,
    'enforcement': 20,
    'exceeding': 21,
    'exceeds': 22,
    'existed': 23,
    'fragments': 24,
    'general': 25,
    'gnu': 26,
    'ignored': 27,
    'liability': 28,
    'license': 29,
    'licensed': 30,
    'literal': 31,
    'means': 32,
    'observed': 33,
    'plaintiff': 34,
    'responded': 35,
    'ultimately': 36,
    'volunteer': 37,
    'warranties': 38,
    'warranty': 39
}


def query_run_tokens_with_unknowns(query_run):
    """
    Yield the original token ids stream with unknown tokens represented
    by None.
    """
    unknowns = query_run.query.unknowns_by_pos
    # yield anything at the start only if this is the first query run
    if query_run.start == 0:
        for _ in range(unknowns.get(-1, 0)):
            yield None

    for pos, tid in query_run.tokens_with_pos():
        yield tid
        if pos == query_run.end:
            break
        for _ in range(unknowns.get(pos, 0)):
            yield None


def query_tokens_with_unknowns(qry):
    """
    Yield the original tokens stream of a Query `qry` with unknown tokens
    represented by None.
    """
    unknowns = qry.unknowns_by_pos
    # yield anything at the start
    for _ in range(unknowns.get(-1, 0)):
        yield None

    for pos, token in enumerate(qry.tokens):
        yield token
        for _ in range(unknowns.get(pos, 0)):
            yield None


def create_rule_from_text_file_and_expression(
    text_file,
    license_expression=None,
    identifier=None,
    **kwargs
):
    """
    Return a new Rule object from a ``text_file`` and a ``license_expression``.
    """
    license_expression = license_expression or 'mit'
    if os.path.exists(text_file):
        from licensedcode.models import get_rule_text
        text = get_rule_text(location=text_file)
    else:
        text = ''

    return create_rule_from_text_and_expression(
        text=text,
        license_expression=license_expression,
        identifier=identifier,
        **kwargs,
    )


def create_rule_from_text_and_expression(
    text=None,
    license_expression=None,
    identifier=None,
    **kwargs,
):
    """
    Return a new Rule object from a ``text``, a ``license_expression`` and a
    rule ``identifier``.
    """
    from licensedcode.models import Rule
    license_expression = license_expression or 'mit'
    text = text or ''
    identifier = identifier or f'_tst_{time()}_{len(text)}_{license_expression}'
    rule = Rule(
        license_expression=license_expression,
        text=text,
        is_synthetic=True,
        identifier=identifier,
        **kwargs,
    )
    rule.setup()
    return rule

