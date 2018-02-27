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
from os.path import exists
from os.path import join
from unittest.case import expectedFailure

import attr

import cluecode.copyrights
from commoncode import saneyaml
from commoncode.testcase import FileDrivenTesting
from commoncode.text import python_safe_name

"""
Data-driven Copyright test utilities.
"""

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


@attr.s(slots=True)
class CopyrightTest(object):
    """
    A copyright detection test is used to verify that copyright detection works
    correctly

    It consists of two files with the same file name: a .yml file with test data
    and a test file with any other extension (and the same name whenremoving the
    .yml extension) that needs to be tested for detection.

    The following data are loaded based on or from the .yml file:
     - a test file to scan for copyrights (based on file name convenstions),
     - a list of expected copyrights, authors, holders or years to detect,
     - optional notes.
     - a boolean flag expected_failure set to True if a test is expected to fail
       for now

    If a list of expected data is not provided or empty, then this test should
    not detect any such data in the test file.
    """
    data_file = attr.ib(default=None)
    test_file = attr.ib(default=None)
    # one of holders, copyrights, authors, years
    what = attr.ib(default=attr.Factory(list))
    copyrights = attr.ib(default=attr.Factory(list))
    holders = attr.ib(default=attr.Factory(list))
    years = attr.ib(default=attr.Factory(list))
    authors = attr.ib(default=attr.Factory(list))

    expected_failures = attr.ib(default=attr.Factory(list))
    notes = attr.ib(default=None)

    def __attrs_post_init__(self, *args, **kwargs):
        if self.data_file:
            with codecs.open(self.data_file, mode='rb', encoding='utf-8') as df:
                for key, value in saneyaml.load(df.read()).items():
                    if value:
                        setattr(self, key, value)

    def to_dict(self):
        """
        Serialize self to an ordered mapping.
        """
        filtered = [field for field in attr.fields(CopyrightTest)
                    if b'_file' in field.name]
        fields_filter = attr.filters.exclude(*filtered)
        data = attr.asdict(self, filter=fields_filter, dict_factory=OrderedDict)
        return OrderedDict([(key, value) for key, value in data.items()
                            # do not dump false and empties
                            if value])

    def dump(self, check_exists=False):
        """
        Dump a representation of self to a .yml data_file in YAML block format.
        """
        as_yaml = saneyaml.dump(self.to_dict())
        if check_exists and os.path.exists(self.data_file):
            raise Exception(self.data_file)
        with codecs.open(self.data_file, 'wb', encoding='utf-8') as df:
            df.write(as_yaml)


def load_copyright_tests(test_dir=test_env.test_data_dir):
    """
    Yield an iterable of CopyrightTest loaded from test data files in test_dir.
    """
    # first collect files with .yml extension and files with other no extensions
    # extension in two maps keyed by the test file path
    data_files = {}
    test_files = {}
    dangling = set()

    def collect(subdir):
        for top, _, files in os.walk(join(test_dir, subdir)):
            for yfile in files:
                if yfile. endswith('~'):
                    continue
                file_path = abspath(join(top, yfile))

                if yfile.endswith('.yml'):
                    data_file_path = file_path
                    test_file_path = file_path.replace('.yml', '')
                else:
                    test_file_path = file_path
                    data_file_path = test_file_path + '.yml'

                if not exists(test_file_path):
                    dangling.add(data_file_path)
                if not exists(data_file_path):
                    dangling.add(test_file_path)
                data_files[test_file_path] = data_file_path
                test_files[test_file_path] = test_file_path

    for d in ('copyrights', 'ics', 'holders', 'authors', 'years'):
        collect(d)

    if dangling:
        print('Dangling missingcopyright test files')
        for o in sorted(dangling):
            print(o)
            raise Exception('Dangling/missing copyright test files: ' + repr(o))

    # ensure that each data file has a corresponding test file
    diff = set(data_files.keys()).symmetric_difference(set(test_files.keys()))
    if diff:
        print('orphaned copyright test files')
        for o in sorted(diff):
            print(o)

    assert not diff, ('Orphaned copyright test file(s) found: '
                      'test file without its YAML test descriptor '
                      'or YAML test descriptor without its test file.')

    # second, create pairs of corresponding (data_file, test file) for files
    # that have the same base_name
    for base_name, data_file in data_files.items():
        test_file = test_files[base_name]
        yield CopyrightTest(data_file, test_file)


def make_copyright_test_functions(test, test_data_dir=test_env.test_data_dir, regen=False):
    """
    Build and return a test function closing on tests arguments and the function
    name. Create only a single function for multiple tests (e.g. copyrights and
    holders together).
    """

    def closure_test_function(*args, **kwargs):
        copyrights, authors, years, holders = cluecode.copyrights.detect(test_file)
        results = dict(
            copyrights=copyrights, authors=authors, years=years, holders=holders,)
        if regen:
            for wht in what:
                setattr(test, wht, results.get(wht))
            test.dump()

        failing = []
        all_expected = []
        all_results = []
        for wht in what:
            expected = getattr(test, wht, [])
            result = results[wht]
            try:
                assert expected == result
            except:
                # On failure, we compare against more result data to get additional
                # failure details, including the test_file and full results
                # this assert will always fail and provide a more detailed failure trace
                all_expected.append(expected)
                all_results.append(result)
                failing.append(wht)

        if all_expected:
            all_expected += [
                'failing tests: ' + ', '.join(failing),
                'data file: file://' + data_file,
                'test file: file://' + test_file
            ]

            assert all_expected == all_results

    data_file = test.data_file
    test_file = test.test_file
    what = test.what

    tfn = test_file.replace(test_data_dir, '').strip('\/\\')
    whats = '_'.join(what)
    test_name = 'test_%(whats)s_%(tfn)s' % locals()
    test_name = python_safe_name(test_name)
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    if test.expected_failures:
        closure_test_function = expectedFailure(closure_test_function)

    return closure_test_function, test_name


def build_tests(copyright_tests, clazz, test_data_dir=test_env.test_data_dir, regen=False):
    """
    Dynamically build test methods from a sequence of CopyrightTest and attach
    these method to the clazz test class.
    """
    for test in copyright_tests:
        # closure on the test params
        if test.expected_failures:
            regen = False
        method, name = make_copyright_test_functions(test, test_data_dir, regen)
        # attach that method to our test class
        setattr(clazz, name, method)
