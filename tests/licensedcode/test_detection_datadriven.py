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

from collections import defaultdict
from collections import OrderedDict
import io
import os
from os.path import abspath
from os.path import join
import pprint
import traceback
import unittest

import attr
from license_expression import Licensing

from commoncode import fileutils
from commoncode import saneyaml
from commoncode import text
from itertools import chain

# Python 2 and 3 support
try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str  # NOQA

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/licenses')

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

    licensing = Licensing()

    def __attrs_post_init__(self, *args, **kwargs):
        if self.test_file:
            _, _, self.test_file_name = self.test_file.partition(
                os.path.join('licensedcode', 'data') + os.sep)

        data = {}
        if self.data_file:
            with io.open(self.data_file, encoding='utf-8') as df:
                data = saneyaml.load(df.read()) or {}

        self.license_expressions = data.pop('license_expressions', [])

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
                        +repr(exp) + ' for: file://' + self.data_file +
                        '\n' + traceback.format_exc()
                )
                if expression is None:
                    raise Exception(
                        'Unable to parse License rule expression: '
                        +repr(exp) + ' for:' + repr(self.data_file))

                new_exp = expression.render()
                self.license_expressions[i] = new_exp

        else:
            if not self.notes:
                raise Exception(
                    'A license test with expected license_expressions should '
                    'have explanatory notes:  for: file://' + self.data_file)

    def to_dict(self):
        dct = OrderedDict()
        if self.license_expressions:
            dct['license_expressions'] = self.license_expressions
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
        with io.open(self.data_file, 'wb') as df:
            df.write(as_yaml)

    def get_test_method_name(self, prefix='test_detection_'):
        test_file_name = self.test_file_name
        test_name = '{prefix}{test_file_name}'.format(**locals())
        return text.python_safe_name(test_name)


def load_license_tests(test_dir=TEST_DATA_DIR):
    """
    Yield an iterable of LicenseTest loaded from test data files in test_dir.
    """
    # first collect files with .yml extension and files with other extensions
    # in two  maps keyed by file base_name
    data_files = {}
    test_files = {}
    paths_ignoring_case = defaultdict(list)

    for top, _, files in os.walk(test_dir):
        for yfile in files:
            if yfile. endswith('~'):
                continue
            base_name = fileutils.file_base_name(yfile)
            file_path = abspath(join(top, yfile))
            file_base_path = abspath(join(top, base_name))
            paths_ignoring_case[file_path.lower()].append(file_path)
            if yfile.endswith('.yml'):
                assert file_base_path not in data_files
                data_files[file_base_path] = file_path
            else:
                assert file_base_path not in test_files
                test_files[file_base_path] = file_path

    # ensure that test file paths are unique when you ignore case
    # we use the file names as test method names (and we have Windows that's
    # case insensitive
    dupes = list(chain.from_iterable(
        paths for paths in paths_ignoring_case.values() if len(paths) != 1))
    if dupes:
        msg = 'Non unique License test file(s) found when ignoring case!'
        print(msg)
        for item in dupes:
            print(repr(item))
        raise Exception(msg + '\n' + pprint.pformat(dupes))

    # ensure that each data file has a corresponding test file
    diff = set(data_files.keys()).symmetric_difference(set(test_files.keys()))
    if diff:
        msg = (
            'Orphaned license test file(s) found: '
            'test file without its YAML test descriptor '
            'or YAML test descriptor without its test file.')
        print(msg)
        for item in diff:
            print(repr(item))
        raise Exception(msg + '\n' + pprint.pformat(diff))

    for base_name, data_file in data_files.items():
        test_file = test_files[base_name]
        yield LicenseTest(data_file, test_file)


def build_tests(license_tests, clazz, regen=False):
    """
    Dynamically build license_test methods from a sequence of LicenseTest and
    attach these method to the clazz license test class.
    """
    # TODO: check that we do not have duplicated tests with same data and text

    for license_test in license_tests:
        test_name = license_test.get_test_method_name()
        test_file = license_test.test_file

        # closure on the license_test params
        test_method = make_test(license_test, regen=regen)

        # avoid duplicated test method
        if hasattr(clazz, test_name):
            msg = ('Duplicated test method name: {test_name}: file://{test_file}'
            ).format(**locals())
            raise Exception(msg)

        # attach that method to our license_test class
        setattr(clazz, test_name, test_method)


def make_test(license_test, regen=False):
    """
    Build and return a test function closing on tests arguments for a
    license_test LicenseTest object.
    """
    test_name = license_test.get_test_method_name()
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    from licensedcode import cache
    from licensedcode.tracing import get_texts

    expected_expressions = license_test.license_expressions or []

    test_file = license_test.test_file
    test_data_file = license_test.data_file
    expected_failure = license_test.expected_failure

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(location=test_file, min_score=0)
        if not matches:
            matches = []

        detected_expressions = [match.rule.license_expression for match in matches]

        # use detection as expected and dump test back
        if regen:
            license_test.license_expressions = detected_expressions
            license_test.dump()
            return

        try:
            assert expected_expressions == detected_expressions
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            failure_trace = detected_expressions[:]
            failure_trace .extend([test_name, 'test file: file://' + test_file])

            for match in matches:
                qtext, itext = get_texts(match, location=test_file, idx=idx)
                rule_text_file = match.rule.text_file
                rule_data_file = match.rule.data_file
                failure_trace.extend(['', '',
                    '======= MATCH ====', match,
                    '======= Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    failure_trace.append('file://{test_data_file}'.format(**locals()))

                failure_trace.append(qtext.splitlines())
                failure_trace.extend(['',
                    '======= Matched Rule Text for:'
                    'file://{rule_text_file}'.format(**locals()),
                    'file://{rule_data_file}'.format(**locals()),
                    itext.splitlines(),
                ])
            # this assert will always fail and provide a detailed failure trace
            assert expected_expressions == failure_trace

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


class TestLicenseToolsDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


# this is for license-related npm tools with a lot of license references in code, tests and data
TEST_DATA_DIR4 = os.path.join(os.path.dirname(__file__), 'data/license_tools')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR4),
            clazz=TestLicenseToolsDataDriven, regen=False)
