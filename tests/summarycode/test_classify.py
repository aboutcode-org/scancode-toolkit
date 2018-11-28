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
from scancode.resource import Codebase
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from summarycode.classify import set_classification_flags
from summarycode.classify import FileClassifier


class TestClassify(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_set_classification_flags_is_readme(self):
        test_dir = self.get_test_loc('classify/readme')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_readme

    def test_set_classification_flags_is_legal(self):
        test_dir = self.get_test_loc('classify/legal')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_legal

    def test_set_classification_flags_not_is_legal(self):
        test_dir = self.get_test_loc('classify/not-legal')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert not res.is_legal

    def test_set_classification_flags_is_manifest(self):
        test_dir = self.get_test_loc('classify/manifest')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_manifest

    def test_classify_cli_option(self):
        test_dir = self.get_test_loc('classify/cli')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('classify/cli.expected.json')
        run_scan_click(['--info', '--classify', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)
