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
from os import path

import attr

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode.plugin_consolidate import Consolidator
from scancode.plugin_consolidate import is_majority
from scancode.resource import VirtualCodebase


class TestConsolidate(FileDrivenTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def get_scan(self, test_loc, cli_options='-clip'):
        scan_loc = self.get_test_loc(test_loc)
        scan_file = self.get_temp_file('json')
        run_scan_click(['-clip', scan_loc, '--json', scan_file])
        return scan_file

    def test_is_majority_above_threshold(self):
        files_count = 10
        src_count = 8
        assert is_majority(src_count, files_count)

    def test_is_majority_below_threshold(self):
        files_count = 10
        src_count = 7
        assert not is_majority(src_count, files_count)

    def test_consolidate_clear_summary(self):
        # 75% of the files have the same license expression and holder, so we should have one consolidated component
        scan_loc = self.get_test_loc('plugin_consolidate/clear-summary')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/clear-summary-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_no_summary(self):
        # 50% of the files have the same license expression and holder, so no consolidated component should be created
        scan_loc = self.get_test_loc('plugin_consolidate/no-summary')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/no-summary-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_package(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/package-fileset-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_package_files_should_not_be_considered_in_license_holder_consolidated_component(self):
        scan_loc = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders')
        result_file = self.get_temp_file('json')
        # There should not be a consolidated component for license-holder, even
        # though every single file in this directory contains the same license
        # expression and holder
        expected_file = self.get_test_loc('plugin_consolidate/package-files-not-counted-in-license-holders-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_clear_summary_from_json(self):
        # 75% of the files have the same license expression and holder, so we should have one consolidated component
        scan_file = self.get_scan('plugin_consolidate/clear-summary', cli_options='-clip')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/clear-summary-expected.json')
        run_scan_click(['--from-json', scan_file, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_component_package_from_json_can_run_twice(self):
        scan_file = self.get_scan('plugin_consolidate/component-package', cli_options='-clip')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-expected.json')

        result_file = self.get_temp_file('json')
        run_scan_click(['--from-json', scan_file, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

        # rerun with result_file from last run
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
        scan_file = self.get_scan('plugin_consolidate/nested-packages', cli_options='-p')
        codebase = VirtualCodebase(scan_file)
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

    def test_consolidate_return_nested_local_majority(self):
        scan_loc = self.get_test_loc('plugin_consolidate/return-nested-local-majority')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/return-nested-local-majority-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        # The nested majority is just 1 file, but has a different origin than the rest of the files above it
        # and should be reported as a separate consolidated component
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True)

    def test_consolidate_component_package_build_from_live_scan(self):
        scan_loc = self.get_test_loc('plugin_consolidate/component-package-build')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/component-package-build-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_report_minority_origin_directory(self):
        scan_loc = self.get_test_loc('plugin_consolidate/report-subdirectory-with-minority-origin')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_consolidate/report-subdirectory-with-minority-origin-expected.json')
        run_scan_click(['-clip', scan_loc, '--consolidate', '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False, remove_file_date=True, ignore_headers=True)

    def test_consolidate_check_for_package_root_and_majority(self):
        scan_loc = self.get_test_loc('plugin_consolidate/majority_and_package_root.json')
        resource_attributes = dict(
            consolidated_to=attr.ib(default=attr.Factory(list))
        )
        codebase_attributes = OrderedDict(
            consolidated_components=attr.ib(default=attr.Factory(list)),
            consolidated_packages=attr.ib(default=attr.Factory(list))
        )
        vc = VirtualCodebase(scan_loc, resource_attributes=resource_attributes, codebase_attributes=codebase_attributes)
        Consolidator().process_codebase(vc)
        for resource in vc.walk(topdown=True):
            if resource.is_file:
                continue
            if resource.name == 'build' or resource.name == 'package':
                assert resource.extra_data.get('package_root')
            if resource.name == 'component':
                assert resource.extra_data.get('majority')
