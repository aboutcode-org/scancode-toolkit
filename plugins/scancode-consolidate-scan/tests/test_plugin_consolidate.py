#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

from collections import OrderedDict
from os.path import dirname
from os.path import join
import json

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from plugin_consolidate import is_majority


class TestConsolidate(FileDrivenTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_is_majority_above_threshold(self):
        files_count = 10
        src_count = 8
        assert is_majority(src_count, files_count)

    def test_is_majority_below_threshold(self):
        files_count = 10
        src_count = 7
        assert not is_majority(src_count, files_count)

    def test_consolidate_clear_summary(self):
        # 75% of the files have the same license expression and holder, so we should have one fileset
        scan_loc = self.get_test_loc('plugin_consolidate/clear-summary')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/clear-summary-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_no_summary(self):
        # 50% of the files have the same license expression and holder, so no fileset should be created
        scan_loc = self.get_test_loc('plugin_consolidate/no-summary')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/no-summary-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_package_fileset(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/package-fileset-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_package_files_should_not_be_considered_in_license_holder_filesets(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders')
        result_file = self.get_temp_file('json')
        # There should not be a fileset for license-holder, even though every single file in this directory contains the
        # same license expression and holder
        expected_file = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_clear_summary_from_json(self):
        # 75% of the files have the same license expression and holder, so we should have one fileset
        scan_loc = self.get_test_loc('plugin_consolidate/clear-summary.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/clear-summary-expected.json')
        run_scan_click(['--from-json', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_component_package_from_json_can_run_twice(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-expected.json')
        run_scan_click(['--from-json', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

        result_file2 = self.get_temp_file('json')
        run_scan_click(['--from-json', result_file, '--consolidate', '--json', result_file2])
        check_json_scan(expected_file, result_file2, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_component_package_from_live_scan(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_package_always_include_own_manifest_file(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package-manifest')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/package-manifest-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_get_package_resources_on_nested_packages_should_include_manifest(self):
        from packagedcode import get_package_instance
        from scancode.resource import VirtualCodebase
        scan_loc = self.get_test_loc('plugin_consolidate/nested-npm-packages.json')
        codebase = VirtualCodebase(scan_loc)
        for resource in codebase.walk():
            for package_data in resource.packages:
                package = get_package_instance(package_data)
                package_resources = list(package.get_package_resources(resource, codebase))
                assert any(r.name == 'package.json' for r in package_resources), resource.path

    def test_consolidate_multiple_same_holder_and_license(self):
        scan_loc = self.get_test_loc('plugin_consolidate/multiple-same-holder-and-license')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/multiple-same-holder-and-license-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_origin_summary_license_holder_rollup(self):
        scan_loc = self.get_test_loc('plugin_consolidate/license-holder-rollup')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/license-holder-rollup-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        # There should be two consolidated components for things under
        # no-majority and one consolidated component for clear-majority
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    # TODO: test that test data is basd off of samples from the outside world and not something
    # that only exists in scancode tests
