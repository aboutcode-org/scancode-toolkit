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

from collections import OrderedDict
import io
from itertools import chain
from os import path

import attr
import pytest

import cluecode.copyrights
from commoncode import compat
from commoncode import saneyaml
from commoncode.system import py2
from commoncode.testcase import FileDrivenTesting
from commoncode.testcase import get_test_file_pairs
from commoncode.text import python_safe_name


"""
Data-driven Copyright test utilities.
"""

test_env = FileDrivenTesting()
test_env.test_data_dir = path.join(path.dirname(__file__), 'data')


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
     - what to test
     - a list of expected copyrights, authors or holders to detect,
     - optional notes.
     - a list of expected_failures

    If a list of expected data is not provided or empty, then this test should
    not detect any such data in the test file.
    """
    data_file = attr.ib(default=None)
    test_file = attr.ib(default=None)
    # one of holders, copyrights, authors
    what = attr.ib(default=attr.Factory(list))
    copyrights = attr.ib(default=attr.Factory(list))
    holders = attr.ib(default=attr.Factory(list))
    authors = attr.ib(default=attr.Factory(list))

    holders_summary = attr.ib(default=attr.Factory(list))
    copyrights_summary = attr.ib(default=attr.Factory(list))
    authors_summary = attr.ib(default=attr.Factory(list))

    expected_failures = attr.ib(default=attr.Factory(list))
    notes = attr.ib(default=None)

    def __attrs_post_init__(self, *args, **kwargs):
        if self.data_file:
            try:
                with io.open(self.data_file, encoding='utf-8') as df:
                    for key, value in saneyaml.load(df.read()).items():
                        if value:
                            setattr(self, key, value)
            except:
                import traceback
                msg = 'file://' + self.data_file + '\n' + repr(self) + '\n' + traceback.format_exc()
                raise Exception(msg)

        # fix counts to be ints: saneyaml loads everything as string
        for holders_sum in self.holders_summary:
            holders_sum['count'] = int(holders_sum['count'])

        for copyrs_sum in self.copyrights_summary:
            copyrs_sum['count'] = int(copyrs_sum['count'])

        for auths_sum in self.authors_summary:
            auths_sum['count'] = int(auths_sum['count'])

    def to_dict(self):
        """
        Serialize self to an ordered mapping.
        """
        filtered = [field for field in attr.fields(CopyrightTest)
                    if '_file' in field.name]
        fields_filter = attr.filters.exclude(*filtered)
        data = attr.asdict(self, filter=fields_filter, dict_factory=OrderedDict)
        return OrderedDict([
            (key, value) for key, value in data.items()
            # do not dump false and empties
            if value])

    def dumps(self):
        """
        Return a string representation of self in YAML block format.
        """
        return saneyaml.dump(self.to_dict())

    def dump(self, check_exists=False):
        """
        Dump a representation of self to a .yml data_file in YAML block format.
        """
        if check_exists and path.exists(self.data_file):
            raise Exception(self.data_file)
        with io.open(self.data_file, 'w', encoding='utf-8') as df:
            df.write(self.dumps())


def load_copyright_tests(test_dir=test_env.test_data_dir):
    """
    Yield an iterable of CopyrightTest loaded from test data files in `test_dir`.
    """
    test_dirs = (path.join(test_dir, td) for td in
        ('copyrights', 'ics', 'holders', 'authors', 'years', 'generated'))

    all_test_files = chain.from_iterable(
        get_test_file_pairs(td) for td in test_dirs)

    for data_file, test_file in all_test_files:
        yield CopyrightTest(data_file, test_file)


def copyright_detector(location):
    """
    Return lists of detected copyrights, authors and holders
    in file at location.
    """
    copyrights = []
    copyrights_append = copyrights.append
    holders = []
    holders_append = holders.append
    authors = []
    authors_append = authors.append

    for dtype, value, _start, _end in cluecode.copyrights.detect_copyrights(location):
        if dtype == 'copyrights':
            copyrights_append(value)
        elif dtype == 'holders':
            holders_append(value)
        elif dtype == 'authors':
            authors_append(value)

    return copyrights, holders, authors


def as_sorted_mapping(counter):
    """
    Return a list of ordered mapping of {value:val, count:cnt} built from a
    `counter` mapping of {value: count} and sortedd by decreasing count then by
    value.
    """

    def by_count_value(value_count):
        value, count = value_count
        return -count, value

    summarized = [OrderedDict([('value', value), ('count', count)])
                  for value, count in sorted(counter.items(), key=by_count_value)]
    return summarized


def make_copyright_test_functions(test, index, test_data_dir=test_env.test_data_dir, regen=False):
    """
    Build and return a test function closing on tests arguments and the function
    name. Create only a single function for multiple tests (e.g. copyrights and
    holders together).
    """
    from summarycode.copyright_summary import summarize_copyrights
    from summarycode.copyright_summary import summarize_holders
    from summarycode.copyright_summary import Text

    def closure_test_function(*args, **kwargs):
        copyrights, holders, authors = copyright_detector(test_file)

        holders_summary = []
        if 'holders_summary' in test.what:
            holders_summary = as_sorted_mapping(summarize_holders(holders))

        copyrights_summary = []
        if 'copyrights_summary' in test.what:
            copyrights_summary = as_sorted_mapping(summarize_copyrights(copyrights))

        authors_summary = []
        if 'authors_summary' in test.what:
            authors_summary = as_sorted_mapping(summarize_holders(authors))

        results = dict(
            copyrights=copyrights,
            authors=authors,
            holders=holders,
            holders_summary=holders_summary,
            copyrights_summary=copyrights_summary,
            authors_summary=authors_summary,
        )

        expected_yaml = test.dumps()

        for wht in test.what:
            setattr(test, wht, results.get(wht))
        results_yaml = test.dumps()

        if regen:
            test.dump()
        if expected_yaml != results_yaml:
            expected_yaml = (
                'data file: file://' + data_file +
                '\ntest file: file://' + test_file + '\n'
            ) + expected_yaml

            assert expected_yaml == results_yaml

    data_file = test.data_file
    test_file = test.test_file
    what = test.what

    tfn = test_file.replace(test_data_dir, '').strip('\\/\\')
    whats = '_'.join(what)
    test_name = 'test_%(tfn)s_%(index)s' % locals()
    test_name = python_safe_name(test_name)

    # onPython2 we need a plain non-unicode string
    if py2 and isinstance(test_name, compat.unicode):
        test_name = test_name.encode('utf-8')

    closure_test_function.__name__ = test_name

    if test.expected_failures:
        closure_test_function = pytest.mark.xfail(closure_test_function)

    return closure_test_function, test_name


def build_tests(copyright_tests, clazz, test_data_dir=test_env.test_data_dir, regen=False):
    """
    Dynamically build test methods from a sequence of CopyrightTest and attach
    these method to the clazz test class.
    """
    for i, test in enumerate(sorted(copyright_tests, key=lambda x:x.test_file)):
        # closure on the test params
        if test.expected_failures:
            actual_regen = False
        else:
            actual_regen = regen
        method, name = make_copyright_test_functions(test, i, test_data_dir, actual_regen)
        # attach that method to our test class
        setattr(clazz, name, method)
