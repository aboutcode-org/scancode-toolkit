#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path
import json
import shutil

from commoncode import testcase


class PackageTester(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_package(self, package, expected_loc, regen=False):
        """
        Helper to test a package object against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc)

        package.license_expression = package.compute_normalized_license()
        results = package.to_dict()

        if regen:
            regened_exp_loc = self.get_temp_file()
            with open(regened_exp_loc, 'w') as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc) as ex:
            expected = json.load(ex)

        try:
            assert results == expected
        except AssertionError:
            assert json.dumps(results, indent=2) == json.dumps(expected, indent=2)

    def check_packages(self, packages, expected_loc, regen=False):
        """
        Helper to test multiple package objects against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc)

        results = []
        for package in packages:
            package.license_expression = package.compute_normalized_license()
            results.append(package.to_dict())

        if regen:
            regened_exp_loc = self.get_temp_file()
            with open(regened_exp_loc, 'w') as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc, 'rb') as ex:
            expected_packages = json.load(ex, encoding='utf-8')

        for expected_package, result in zip(expected_packages, results):
            assert result == expected_package


def check_result_equals_expected_json(result, expected, regen=False):
    """
    Check equality between a result collection and an expected JSON file.
    Regen the expected file if regen is True.
    """
    if regen:
        with open(expected, 'w') as ex:
            ex.write(json.dumps(result, indent=2))

    with open(expected) as ex:
        expected = json.loads(ex.read())

    assert result == expected
