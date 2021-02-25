#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
from os import path
from os import walk

from commoncode.testcase import FileBasedTesting
from commoncode import text
import saneyaml

from packagedcode import debian_copyright


def check_expected_parse_copyright_file(
    test_loc,
    expected_loc,
    regen=False,
    with_details=False,
):
    """
    Check copyright parsing of `test_loc` location against an expected JSON file
    at `expected_loc` location. Regen the expected file if `regen` is True.
    """
    if with_details:
        skip_debian_packaging = True
        simplify_licenses = True
        unique = True
    else:
        skip_debian_packaging = False
        simplify_licenses = False
        unique = False

    parsed = debian_copyright.parse_copyright_file(
        copyright_file=test_loc,
        skip_debian_packaging=skip_debian_packaging,
        simplify_licenses=simplify_licenses,
        unique=unique,
    )
    result = saneyaml.dump(list(parsed))
    if regen:
        with io.open(expected_loc, 'w', encoding='utf-8') as reg:
            reg.write(result)

    with io.open(expected_loc, encoding='utf-8') as ex:
        expected = ex.read()

    if result != expected:

        expected = '\n'.join([
            'file://' + test_loc,
            'file://' + expected_loc,
            expected
        ])

        assert result == expected


def relative_walk(dir_path):
    """
    Walk path and yield files paths relative to dir_path.
    """
    for base_dir, _dirs, files in walk(dir_path):
        for file_name in files:
            if file_name.endswith('.yml'):
                continue
            file_path = path.join(base_dir, file_name)
            file_path = file_path.replace(dir_path, '', 1)
            file_path = file_path.strip(path.sep)
            yield file_path


def create_test_function(
    test_loc,
    expected_loc,
    test_name,
    with_details=False,
    regen=False,
):
    """
    Return a test function closed on test arguments.
    """

    # closure on the test params
    def test_func(self):
        check_expected_parse_copyright_file(
            test_loc, expected_loc, with_details=with_details, regen=regen)

    # set a proper function name to display in reports and use in discovery
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    test_func.__name__ = test_name
    return test_func


def build_tests(test_dir, clazz, prefix='test_', regen=False):
    """
    Dynamically build test methods for each copyright file in `test_dir` and
    attach the test method to the `clazz` class.
    """
    test_data_dir = path.join(path.dirname(__file__), 'data')
    test_dir_loc = path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir_loc):
        test_name = prefix + text.python_safe_name(test_file)
        test_loc = path.join(test_dir_loc, test_file)

        # create two test methods: one with and one without details
        test_method = create_test_function(
            test_loc=test_loc,
            expected_loc=test_loc + '.expected.yml',
            test_name=test_name,
            regen=regen,
            with_details=False,
        )
        # attach that method to the class
        setattr(clazz, test_name, test_method)

        test_method = create_test_function(
            test_loc=test_loc,
            expected_loc=test_loc + '-detailed.expected.yml',
            test_name=test_name,
            regen=regen,
            with_details=True,
        )
        # attach that method to the class
        setattr(clazz, test_name, test_method)


class TestDebianCopyrightLicenseDetection(FileBasedTesting):
    # pytestmark = pytest.mark.scanslow
    test_data_dir = path.join(path.dirname(__file__), 'data')


build_tests(
    test_dir='debian/copyright/debian-2019-11-15',
    prefix='test_debian_parse_copyright_file_',
    clazz=TestDebianCopyrightLicenseDetection,
    regen=False,
)
