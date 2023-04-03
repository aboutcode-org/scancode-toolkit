#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os import path

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestConsolidate(FileDrivenTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_consolidate_package(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/package-fileset-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_package_files_should_not_be_considered_in_license_holder_consolidated_component(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders')
        result_file = self.get_temp_file('json')
        # There should not be a consolidated component for license-holder, even
        # though every single file in this directory contains the same license
        # expression and holder
        expected_file = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_component_package_from_json_can_run_twice(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package')
        scan_file = self.get_temp_file('json')
        run_scan_click(['-clip', scan_loc, '--json', scan_file])
        expected_file = self.get_test_loc('plugin_consolidate/component-package-expected.json')
        result_file = self.get_temp_file('json')
        run_scan_click(['--from-json', scan_file, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)
 
        # rerun with result_file from last run
        result_file2 = self.get_temp_file('json')
        run_scan_click(['--from-json', result_file, '--consolidate', '--json', result_file2])
        check_json_scan(expected_file, result_file2, remove_uuid=True, regen=False, remove_file_date=True)

    def test_consolidate_component_package_from_live_scan(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_package_always_include_own_manifest_file(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package-manifest')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/package-manifest-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_multiple_same_holder_and_license(self):
        scan_loc = self.get_test_loc('plugin_consolidate/multiple-same-holder-and-license')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/multiple-same-holder-and-license-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_origin_summary_license_holder_rollup(self):
        scan_loc = self.get_test_loc('plugin_consolidate/license-holder-rollup')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/license-holder-rollup-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        # There should be two consolidated components for things under
        # no-majority and one consolidated component for clear-majority
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_return_nested_local_majority(self):
        scan_loc = self.get_test_loc('plugin_consolidate/return-nested-local-majority')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/return-nested-local-majority-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        # The nested majority is just 1 file, but has a different origin than the rest of the files above it
        # and should be reported as a separate consolidated component
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_component_package_build_from_live_scan(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package-build')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-build-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_report_minority_origin_directory(self):
        scan_loc = self.get_test_loc('plugin_consolidate/report-subdirectory-with-minority-origin')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/report-subdirectory-with-minority-origin-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_zlib(self):
        # Input for scan: https://github.com/madler/zlib/archive/refs/tags/v1.2.11.tar.gz
        # Run a -clipeu scan to regenerate plugin_consolidate/zlib.json
        scan_loc = self.get_test_loc('plugin_consolidate/zlib.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/zlib-expected.json')
        run_scan_click(['--from-json', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_consolidate_e2fsprogs(self):
        # Input for the scan: https://github.com/tytso/e2fsprogs/archive/refs/tags/v1.45.4.zip
        # Run a -clipeu scan to regenerate plugin_consolidate/e2fsprogs.json
        scan_loc = self.get_test_loc('plugin_consolidate/e2fsprogs.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/e2fsprogs-expected.json')
        run_scan_click(['--from-json', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)
