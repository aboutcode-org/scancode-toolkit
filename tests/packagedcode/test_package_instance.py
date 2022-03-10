#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from packagedcode.pypi import PythonPackage
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestPackageAndDependency(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_package_instance_scan_python(self):
        test_dir = self.get_test_loc('instance/pypi')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('instance/python-package-instance-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_instance_uuid=True)

    # Note that this will fail even at regen True.
    # Will pass on the next regen False run.
    # ToDo: Use moking instead
    def test_package_instance_scan_python_with_uuid(self):
        test_dir = self.get_test_loc('instance/pypi')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('instance/python-package-instance-expected-with-uuid.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, ignore_instance_uuid=True)

    def test_package_instance_scan_python_with_test_manifests(self):
        test_dir = self.get_test_loc('instance/pypi-with-test-manifests')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('instance/python-package-instance-expected-with-test-manifests.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_instance_uuid=True)

    def test_package_data_merge_generic(self, regen=REGEN_TEST_FIXTURES):
        input_file = self.get_test_loc('instance/python-manifests-click-scanned.json')
        expected_file = self.get_test_loc('instance/python-manifests-click-scanned-result.json')

        with io.open(input_file, encoding='utf-8') as res:
            manifests = json.load(res)

        pk_instance = PythonPackage()
        for manifest in manifests:
            pk_instance.update(manifest)

        self.check_package(pk_instance, expected_file, regen)

    def test_package_data_merge_with_dependencies(self, regen=REGEN_TEST_FIXTURES):
        input_file = self.get_test_loc('instance/python-manifests-atomicwrites-scanned.json')
        expected_file = self.get_test_loc('instance/python-manifests-atomicwrites-scanned-result.json')

        with io.open(input_file, encoding='utf-8') as res:
            manifests = json.load(res)

        pk_instance = PythonPackage()
        for manifest in manifests:
            pk_instance.update(manifest)

        self.check_package(pk_instance, expected_file, regen)
