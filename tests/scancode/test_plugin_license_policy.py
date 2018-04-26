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
from __future__ import unicode_literals

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from scancode_cli_test_utils import load_json_result
from scancode_cli_test_utils import run_scan_click
from scancode.plugin_license_policy import load_license_policy


class TestLicensePolicy(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_process_codebase_info_license(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/license-policy-file.yml')

        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_license_policy/info-license-expected.json')

        run_scan_click(['--info', '--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        approved, restricted = 0, 0
        for result in scan_result['files']:
            if result.get('license_policy') != {}:
                if result.get('license_policy').get('label') == "Approved License":
                    approved += 1
                if result.get('license_policy').get('label') == "Restricted License":
                    restricted += 1

        assert approved == 1
        assert restricted == 4

    def test_process_codebase_license_only(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/license-policy-file.yml')

        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_license_policy/license-only-expected.json')

        run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        approved, restricted = 0, 0
        for result in scan_result['files']:
            if result.get('license_policy') != {}:
                if result.get('license_policy').get('label') == "Approved License":
                    approved += 1
                if result.get('license_policy').get('label') == "Restricted License":
                    restricted += 1

        assert approved == 1
        assert restricted == 4


    def test_process_codebase_info_only(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/license-policy-file.yml')

        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_license_policy/info-only-expected.json')

        run_scan_click(['--info', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        for result in scan_result['files']:
            assert result.get('license_policy') == {}

    def test_process_codebase_invalid_policy_file(self):
        test_dir = self.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
        policy_file = self.get_test_loc('plugin_license_policy/license_policies_invalid.yml')

        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_license_policy/invalid-policy-file-expected.json')

        run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

        scan_result = load_json_result(result_file)

        for result in scan_result['files']:
            assert 'license_policy' in result.keys()

        for result in scan_result['files']:
            assert result.get('license_policy') == {}

    def test_load_license_policy_invalid(self):
        test_file = self.get_test_loc('plugin_license_policy/license_policies_invalid.yml')

        result = load_license_policy(test_file)

        assert {} == result

    def test_load_license_policy_empty(self):
        test_file = self.get_test_loc('plugin_license_policy/license_policies_empty.yml')

        expected = {
            u'license_policies': ''
        }

        result = load_license_policy(test_file)

        assert expected == result

    def test_load_license_policy_valid(self):
        test_file = self.get_test_loc('plugin_license_policy/license_policies_valid.yml')

        expected = {
            u'license_policies': {
                u'broadcom-commercial': {
                    u'color_code': u'#FFcc33',
                    u'icon': u'icon-warning-sign',
                    u'label': u'Restricted License',
                },
                u'bsd-1988': {
                    u'color_code': u'#008000',
                    u'icon': u'icon-ok-circle',
                    u'label': u'Approved License',
                },
                u'esri-devkit': {
                    u'color_code': u'#FFcc33',
                    u'icon': u'icon-warning-sign',
                    u'label': u'Restricted License',
                },
                u'oracle-java-ee-sdk-2010': {
                    u'color_code': u'#FFcc33',
                    u'icon': u'icon-warning-sign',
                    u'label': u'Restricted License',
                },
                u'rh-eula': {
                    u'color_code': u'#FFcc33',
                    u'icon': u'icon-warning-sign',
                    u'label': u'Restricted License',
                },
            }
        }

        result = load_license_policy(test_file)

        assert expected == result
