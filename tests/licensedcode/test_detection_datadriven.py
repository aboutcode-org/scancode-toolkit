#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import os
from os.path import abspath
from os.path import join
import traceback
import unittest

from license_expression import Licensing

from commoncode import fileutils
from commoncode import functional
from commoncode import text
from commoncode import saneyaml

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/licenses')

"""
Data-driven tests using expectations stored in YAML files.
"""


class LicenseTest(object):
    """
    A license detection test is used to verify that license detection works
    correctly

    It consists of two files with the same base name: a .yml file with test data
    and a test file with any other extension that needs to be tested for
    detection

    The following data are loaded from the .yml file:
     - a test file to scan for licenses,
     - a list of expected licenses to detect
     - optional notes.
     - a list of license expressions (not used yet)
     - a boolean flag expected_failure set to True if a test is expected to fail
       for now.

    If the list of licenses is empty, then this test should not detect any
    license in the test file.
    """
    __slots__ = (
        'data_file', 'test_file', 'test_file_name',
        'licenses', 'license_choice',
        'license_expressions',
        'notes',
        'expected_failure',
        'licensing',
    )

    licensing = Licensing()

    def __init__(self, data_file=None, test_file=None):
        self.data_file = data_file
        self.test_file = test_file
        if self.test_file:
            self.test_file_name = fileutils.file_name(test_file)

        data = {}
        if self.data_file:
            with codecs.open(data_file, mode='rb', encoding='utf-8') as df:
                data = saneyaml.load(df.read()) or {}

        self.licenses = data.get('licenses', [])

        self.license_choice = data.get('license_choice')

        self.license_expressions = data.get('license_expressions', [])

        self.notes = data.get('notes')

        # True if the test is expected to fail
        self.expected_failure = data.get('expected_failure', False)

        # build expression from available data if not present
        if not self.license_expressions:
            kw = self.license_choice and ' or ' or ' and '
            exp = kw.join(self.licenses).strip()
            if exp:
                self.license_expressions = [exp]

        if self.license_expressions:
            for i, exp in enumerate(self.license_expressions[:]):
                try:
                    expression = self.licensing.parse(exp)
                except:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        + repr(exp) + ' for: file://' + self.data_file +
                        '\n' + traceback.format_exc()
                )
            if expression is None:
                raise Exception(
                    'Unable to parse License rule expression: '
                    + repr(exp) + ' for:' + repr(self.data_file))

            exp = expression.render()
            # this is a grossly incorrect approximation that will fail alright when
            # running the tests
            self.license_expressions[i] = exp

    def to_dict(self):
        dct = OrderedDict()
        if self.licenses:
            dct['licenses'] = self.licenses
        if self.license_choice:
            dct['license_choice'] = self.license_choice
        if self.license_expressions:
            dct['license_expressions'] = self.license_expressions
        if self.expected_failure:
            dct['expected_failure'] = self.expected_failure
        if self.notes:
            dct['notes'] = self.notes
        return dct

    def dump(self):
        """
        Dump a representation of self to tgt_dir using two files:
         - a .yml for the rule data in YAML block format
         - a .RULE: the rule text as a UTF-8 file
        """
        as_yaml = saneyaml.dump(self.to_dict())
        with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
            df.write(as_yaml)


def load_license_tests(test_dir=TEST_DATA_DIR):
    """
    Yield an iterable of LicenseTest loaded from test data files in test_dir.
    """
    # first collect files with .yml extension and files with other extensions
    # in two  maps keyed by file base_name
    data_files = {}
    test_files = {}
    for top, _, files in os.walk(test_dir):
        for yfile in files:
            if yfile. endswith('~'):
                continue
            base_name = fileutils.file_base_name(yfile)
            file_path = abspath(join(top, yfile))
            if yfile.endswith('.yml'):
                assert base_name not in data_files
                data_files[base_name] = file_path
            else:
                assert base_name not in test_files
                test_files[base_name] = file_path

    # ensure that each data file has a corresponding test file
    diff = set(data_files.keys()).symmetric_difference(set(test_files.keys()))
    assert not diff, ('Orphaned license test file(s) found: '
                      'test file without its YAML test descriptor '
                      'or YAML test descriptor without its test file.')

    # second, create pairs of corresponding (data_file, test file) for files
    # that have the same base_name
    for base_name, data_file in data_files.items():
        test_file = test_files[base_name]
        yield LicenseTest(data_file, test_file)


def build_tests(license_tests, clazz, regen=False):
    """
    Dynamically build license_test methods from a sequence of LicenseTest and attach
    these method to the clazz license_test class.
    """
    # TODO: check that we do not have duplicated tests with same data and text

    for license_test in license_tests:
        # uncomment to regen/redump
        # license_test.dump()
        tfn = license_test.test_file_name
        test_name = 'test_detection_%(tfn)s' % locals()
        test_name = text.python_safe_name(test_name)

        # closure on the license_test params
        test_method = make_license_test_function(
            license_test,
            test_name=test_name,
            regen=regen
        )

        # attach that method to our license_test class
        setattr(clazz, test_name, test_method)


def make_license_test_function(license_test, test_name, regen=False):
    """
    Build and return a test function closing on tests arguments for a
    license_test LicenseTest object.
    """
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    from licensedcode import cache
    from licensedcode.tracing import get_texts

    expected_licenses = license_test.licenses or []
    expected_expressions = license_test.license_expressions or []

    test_file = license_test.test_file
    test_data_file = license_test.data_file
    expected_failure = license_test.expected_failure

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(location=test_file, min_score=0)
        if not matches:
            matches = []

        detected_license_keys = functional.flatten(map(unicode, match.rule.licenses) for match in matches)
        detected_license_expressions = [match.rule.license_expression for match in matches]

        # use detection as expected and dump test back
        if regen:
            license_test.licenses = detected_license_keys
            license_test.license_expressions = detected_license_expressions
            license_test.dump()
            return

        # test license keys
        try:
            assert expected_licenses == detected_license_keys
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            match_failure_trace = []

            for match in matches:
                qtext, itext = get_texts(match, location=test_file, idx=idx)
                rule_text_file = match.rule.text_file
                rule_data_file = match.rule.data_file
                match_failure_trace.extend(['', '',
                    '======= MATCH ====', match,
                    '======= Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    match_failure_trace.append('file://{test_data_file}'.format(**locals()))
                match_failure_trace.append(qtext.splitlines())
                match_failure_trace.extend(['',
                    '======= Matched Rule Text for:'
                    'file://{rule_text_file}'.format(**locals()),
                    'file://{rule_data_file}'.format(**locals()),
                    itext.splitlines(),
                ])
            # this assert will always fail and provide a detailed failure trace
            assert expected_licenses == detected_license_keys + [test_name, 'test file: file://' + test_file] + match_failure_trace

        # test expressions
        try:
            assert expected_expressions == detected_license_expressions
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            match_failure_trace = []

            for match in matches:
                qtext, itext = get_texts(match, location=test_file, idx=idx)
                rule_text_file = match.rule.text_file
                rule_data_file = match.rule.data_file
                match_failure_trace.extend(['', '',
                    '=== INCORRECT EXPRESSION ===',
                    '======= MATCH ====', match,
                    '======= Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    match_failure_trace.append('file://{test_data_file}'.format(**locals()))
                match_failure_trace.append(qtext.splitlines())
                match_failure_trace.extend(['',
                    '======= Matched Rule Text for:'
                    'file://{rule_text_file}'.format(**locals()),
                    'file://{rule_data_file}'.format(**locals()),
                    itext.splitlines(),
                ])
            # this assert will always fail and provide a detailed failure trace
            assert expected_expressions == detected_license_expressions + [test_name, 'test file: file://' + test_file] + match_failure_trace

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    if expected_failure:
        closure_test_function = unittest.expectedFailure(closure_test_function)

    return closure_test_function


class TestLicenseDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


build_tests(license_tests=load_license_tests(),
            clazz=TestLicenseDataDriven, regen=False)


class TestLicenseRetrographyDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


TEST_DATA_DIR2 = os.path.join(os.path.dirname(__file__), 'data/retro_licenses/OS-Licenses-master')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR2),
            clazz=TestLicenseRetrographyDataDriven, regen=False)


class TestLicenseSpdxDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


TEST_DATA_DIR3 = os.path.join(os.path.dirname(__file__), 'data/spdx/licenses')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR3),
            clazz=TestLicenseSpdxDataDriven, regen=False)
