#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os

import saneyaml

from commoncode import testcase
from commoncode import text
from scancode.cli_test_utils import purl_with_fake_uuid

from scancode_config import REGEN_TEST_FIXTURES


class PackageTester(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_package_data(
        self,
        package_data,
        expected_loc,
        regen=REGEN_TEST_FIXTURES,
    ):
        """
        Helper to test a package object against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc, must_exist=False)

        populate_license_fields(package_data)
        results = package_data.to_dict()

        check_result_equals_expected_json(
            result=results,
            expected_loc=expected_loc,
            regen=regen,
        )

    def check_packages_data(
        self,
        packages_data,
        expected_loc,
        must_exist=True,
        remove_uuid=True,
        regen=REGEN_TEST_FIXTURES,
    ):
        """
        Helper to test a list of package_data objects against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc, must_exist=must_exist)

        results = []
        for package_data in packages_data:
            if remove_uuid and hasattr(package_data, 'package_uid'):
                package_data.package_uid = purl_with_fake_uuid(package_data.package_uid)
            if remove_uuid and hasattr(package_data, 'resources'):
                for resource in package_data.resources:
                    normalized_package_uids = [
                        purl_with_fake_uuid(package_uid)
                        for package_uid in resource.for_packages
                    ]
                    resource.for_packages = normalized_package_uids
            populate_license_fields(package_data)
            results.append(package_data.to_dict())

        check_result_equals_expected_json(
            result=results,
            expected_loc=expected_loc,
            regen=regen,
        )


def populate_license_fields(package_data):
    if package_data.extracted_license_statement and not package_data.declared_license_expression:
        from packagedcode import HANDLER_BY_DATASOURCE_ID
        handler = HANDLER_BY_DATASOURCE_ID[package_data.datasource_id]
        handler.populate_license_fields(package_data)


def check_result_equals_expected_json(result, expected_loc, regen=REGEN_TEST_FIXTURES):
    """
    Check equality between a result collection and the data in an expected_loc
    JSON file. Regen the expected file if regen is True.
    """
    if regen:
        expected = result

        expected_dir = os.path.dirname(expected_loc)
        if not os.path.exists(expected_dir):
            os.makedirs(expected_dir)

        with open(expected_loc, 'w') as ex:
            json.dump(expected, ex, indent=2, separators=(',', ': '))
    else:
        with open(expected_loc) as ex:
            expected = json.load(ex)

    if result != expected:
        assert saneyaml.dump(result) == saneyaml.dump(expected)


def get_test_files(location, test_file_suffix):
    """
    Walk directory at ``location`` and yield location-relative paths to test
    files matching ``test_file_suffix``).
    """
    assert os.path.exists(location), f'Missing location: {location!r}'

    # NOTE we do not use commoncode here as we want NO files spkipped for testing
    for base_dir, _dirs, files in os.walk(location):
        for file_name in files:
            if not file_name.endswith(test_file_suffix):
                continue

            file_path = os.path.join(base_dir, file_name)
            file_path = file_path.replace(location, '', 1)
            file_path = file_path.strip(os.path.sep)
            yield file_path


def create_test_function(
    test_file_loc,
    tested_function,
    test_name,
    regen=REGEN_TEST_FIXTURES,
):
    """
    Return a test function closed on test arguments to run
    `tested_function(test_file_loc)`.
    """

    def test_proper(self):
        test_loc = self.get_test_loc(test_file_loc, must_exist=True)
        result = tested_function(test_loc)
        check_result_equals_expected_json(
            result=result,
            expected_loc=test_loc + '-expected.json',
            regen=regen,
        )

    test_proper.__name__ = test_name
    return test_proper


def build_tests(
    test_dir,
    test_file_suffix,
    clazz,
    tested_function,
    test_method_prefix,
    regen=REGEN_TEST_FIXTURES,
):
    """
    Dynamically build test methods from files in ``test_dir`` ending with
    ``test_file_suffix`` and attach a test method to the ``clazz`` test class.

    For each method:
    - run ``tested_function`` with a test file with``test_file_suffix``
      ``tested_function`` should return a JSON-serializable object.
    - set the name prefixed with ``test_method_prefix``.
    - check that a test expected file named <test_file_name>-expected.json`
      has content matching the results of the ``tested_function`` returned value.
    """
    assert issubclass(clazz, PackageTester)

    # loop through all items and attach a test method to our test class
    for test_file_path in get_test_files(test_dir, test_file_suffix):
        test_name = test_method_prefix + text.python_safe_name(test_file_path)
        test_file_loc = os.path.join(test_dir, test_file_path)

        test_method = create_test_function(
            test_file_loc=test_file_loc,
            tested_function=tested_function,
            test_name=test_name,
            regen=regen,
        )
        setattr(clazz, test_name, test_method)


def compare_package_results(expected, result):
    result_packages = [r.to_dict() for r in result]
    expected_packages = [e.to_dict() for e in expected]
    assert result_packages == expected_packages
