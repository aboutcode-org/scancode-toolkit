#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
from itertools import chain
from os import path

import attr
import pytest
import saneyaml

from commoncode.testcase import FileDrivenTesting
from commoncode.testcase import get_test_file_pairs
from commoncode.text import python_safe_name

from cluecode.copyrights import detect_copyrights
from cluecode.copyrights import Detection
from scancode_config import REGEN_TEST_FIXTURES


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
                msg = (
                    f'file://{self.data_file}\n'
                    f'{self!r}\n' + traceback.format_exc()
                )
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
        filtered = [
            field for field in attr.fields(CopyrightTest)
            if '_file' in field.name
        ]

        fields_filter = attr.filters.exclude(*filtered)
        data = attr.asdict(self, filter=fields_filter, dict_factory=dict)

        return dict([
            (key, value) for key, value in data.items()
            # do not dump false and empties
            if value
        ])

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


def as_sorted_mapping(counter):
    """
    Return a list of ordered mapping of {value:val, count:cnt} built from a
    `counter` mapping of {value: count} and sortedd by decreasing count then by
    value.
    """

    def by_count_value(value_count):
        value, count = value_count
        return -count, value

    summarized = [
        dict([('value', value), ('count', count)])
        for value, count in sorted(counter.items(), key=by_count_value)
    ]

    return summarized


def get_detections(test_file):
    detections = detect_copyrights(test_file)
    return Detection.split_values(detections)


def make_copyright_test_functions(
    test,
    index,
    test_data_dir=test_env.test_data_dir,
    regen=REGEN_TEST_FIXTURES,
):
    """
    Build and return a test function closing on tests arguments and the function
    name. Create only a single function for multiple tests (e.g. copyrights and
    holders together).
    """
    from summarycode.copyright_tallies import tally_copyrights
    from summarycode.copyright_tallies import tally_persons

    def closure_test_function(*args, **kwargs):
        detections = detect_copyrights(test_file)
        copyrights, holders, authors = Detection.split_values(detections)

        holders_summary = []
        if 'holders_summary' in test.what:
            holders_summary = as_sorted_mapping(tally_persons(holders))

        copyrights_summary = []
        if 'copyrights_summary' in test.what:
            copyrights_summary = as_sorted_mapping(tally_copyrights(copyrights))

        authors_summary = []
        if 'authors_summary' in test.what:
            authors_summary = as_sorted_mapping(tally_persons(authors))

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

            assert results_yaml == expected_yaml

    data_file = test.data_file
    test_file = test.test_file

    tfn = test_file.replace(test_data_dir, '').strip('\\/\\')
    test_name = python_safe_name(f'test_{tfn}_{index}')
    closure_test_function.__name__ = test_name

    if test.expected_failures:
        closure_test_function = pytest.mark.xfail(closure_test_function)

    return closure_test_function, test_name


def build_tests(
    copyright_tests,
    clazz,
    test_data_dir=test_env.test_data_dir,
    regen=REGEN_TEST_FIXTURES,
):
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

        method, name = make_copyright_test_functions(
            test=test,
            index=i,
            test_data_dir=test_data_dir,
            regen=actual_regen,
        )

        # attach that method to our test class
        setattr(clazz, name, method)
