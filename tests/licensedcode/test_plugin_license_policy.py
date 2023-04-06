#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from licensedcode.plugin_license_policy import has_policy_duplicates
from licensedcode.plugin_license_policy import load_license_policy
from scancode.cli_test_utils import load_json_result
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES

class TestLicensePolicy(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_end_to_end_scan_with_license_policy(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_info_license_valid_policy_file.yml')
        result_file = self.get_temp_file('json')
        args = [
            '--info',
            '--license',
            '--license-policy',
            policy_file,
            test_dir,
            '--json-pp',
            result_file
        ]
        run_scan_click(args)
        test_loc = self.get_test_loc('plugin_license_policy/policy-codebase.expected.json')
        check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_end_to_end_scan_with_license_policy_multiple_text(self):
        test_dir = self.get_test_loc('plugin_license_policy/file_with_multiple_licenses.txt')
        policy_file = self.get_test_loc('plugin_license_policy/sample_valid_policy_file.yml')
        result_file = self.get_temp_file('json')
        args = [
            '--info',
            '--license',
            '--license-policy',
            policy_file,
            test_dir,
            '--json-pp',
            result_file
        ]
        run_scan_click(args)
        test_loc = self.get_test_loc('plugin_license_policy/file_with_multiple_licenses.expected.json')
        check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)

    def test_process_codebase_info_license_duplicate_key_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_info_license_duplicate_key_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--info', '--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()
            assert result['license_policy'] == []

    def test_process_codebase_info_license_valid_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_info_license_valid_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--info', '--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        approved, restricted = 0, 0
        for result in scan_result['files']:
            if result.get('license_policy') != []:
                if result.get('license_policy')[0].get('label') == "Approved License":
                    approved += 1
                if result.get('license_policy')[0].get('label') == "Restricted License":
                    restricted += 1

        assert approved == 1
        assert restricted == 4

    def test_process_codebase_license_only_valid_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_license_only_valid_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        approved, restricted = 0, 0
        for result in scan_result['files']:
            if result.get('license_policy') != []:
                if result.get('license_policy')[0].get('label') == "Approved License":
                    approved += 1
                if result.get('license_policy')[0].get('label') == "Restricted License":
                    restricted += 1

        assert approved == 1
        assert restricted == 4

    def test_process_codebase_info_only_valid_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_info_only_valid_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--info', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        for result in scan_result['files']:
            assert result.get('license_policy') == []

    def test_process_codebase_empty_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_empty_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        for result in scan_result['files']:
            assert result.get('license_policy') == []

    def test_process_codebase_invalid_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/process_codebase_invalid_policy_file.yml')

        result_file = self.get_temp_file('json')

        run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        for result in scan_result['files']:
            assert result.get('license_policy') == []

    def test_has_policy_duplcates_invalid_dupes(self):
        test_file = self.get_test_loc('plugin_license_policy/has_policy_duplicates_invalid_dupes.yml')

        result = has_policy_duplicates(test_file)

        assert result == True

    def test_has_policy_duplcates_valid(self):
        test_file = self.get_test_loc('plugin_license_policy/has_policy_duplicates_valid.yml')

        result = has_policy_duplicates(test_file)

        assert result == False

    def test_has_policy_duplicates_empty(self):
        test_file = self.get_test_loc('plugin_license_policy/has_policy_duplicates_empty.yml')

        result = has_policy_duplicates(test_file)

        assert result == False

    def test_has_policy_duplicates_invalid_no_dupes(self):
        test_file = self.get_test_loc('plugin_license_policy/has_policy_duplicates_invalid_no_dupes.yml')

        result = has_policy_duplicates(test_file)

        assert result == False

    def test_load_license_policy_duplicate_keys(self):
        test_file = self.get_test_loc('plugin_license_policy/load_license_policy_duplicate_keys.yml')

        expected = dict([
            ('license_policies', [
                dict([
                    ('license_key', 'broadcom-commercial'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'bsd-1988'),
                    ('label', 'Approved License'),
                    ('color_code', '#008000'),
                    ('icon', 'icon-ok-circle'),
                ]),
                dict([
                    ('license_key', 'esri-devkit'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'oracle-java-ee-sdk-2010'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'rh-eula'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'broadcom-commercial'),
                    ('label', 'Approved License'),
                    ('color_code', '#008000'),
                    ('icon', 'icon-ok-circle'),
                ]),
            ])
        ])

        result = load_license_policy(test_file)

        assert result == expected

    def test_load_license_policy_valid(self):
        test_file = self.get_test_loc('plugin_license_policy/load_license_policy_valid.yml')

        expected = dict([
            ('license_policies', [
                dict([
                    ('license_key', 'broadcom-commercial'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'bsd-1988'),
                    ('label', 'Approved License'),
                    ('color_code', '#008000'),
                    ('icon', 'icon-ok-circle'),
                ]),
                dict([
                    ('license_key', 'esri-devkit'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'oracle-java-ee-sdk-2010'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
                dict([
                    ('license_key', 'rh-eula'),
                    ('label', 'Restricted License'),
                    ('color_code', '#FFcc33'),
                    ('icon', 'icon-warning-sign'),
                ]),
            ])
        ])

        result = load_license_policy(test_file)

        assert result == expected

    def test_load_license_policy_empty(self):
        test_file = self.get_test_loc('plugin_license_policy/load_license_policy_empty.yml')

        expected = dict([
            (u'license_policies', [])
        ])

        result = load_license_policy(test_file)

        assert result == expected

    def test_load_license_policy_invalid(self):
        test_file = self.get_test_loc('plugin_license_policy/load_license_policy_invalid.yml')

        result = load_license_policy(test_file)

        assert result == {}
