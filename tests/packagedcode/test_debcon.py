#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
from __future__ import print_function
from __future__ import unicode_literals

from os import path

from packagedcode import debcon
from packages_test_utils import PackageTester


class TestDebcon(PackageTester):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_get_paragraph__from_status(self):
        test_file = self.get_test_loc('debcon/status/simple_status')
        expected_loc = 'debcon/status/simple_status-expected.json'
        results = list(debcon.get_paragraph(test_file))
        self.check_json(results, expected_loc, regen=False)

        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)

    def test_get_paragraph__from_sources(self):
        test_file = self.get_test_loc('debcon/sources/simple_sources')
        expected_loc = 'debcon/sources/simple_sources-expected.json'
        results = list(debcon.get_paragraph(test_file))
        self.check_json(results, expected_loc, regen=False)

        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)

    def test_get_paragraph__from_packages(self):
        test_file = self.get_test_loc('debcon/packages/simple_packages')
        expected_loc = 'debcon/packages/simple_packages-expected.json'
        results = list(debcon.get_paragraph(test_file))
        self.check_json(results, expected_loc, regen=False)

        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)

    def test_get_paragraphs__from_copyrights_dep5_1(self):
        test_file = self.get_test_loc('debcon/copyright/dep5-b43-fwcutter.copyright')
        expected_loc = 'debcon/copyright/dep5-b43-fwcutter.copyright-expected.json'
        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)

    def test_get_paragraphs__from_copyrights_dep5_3(self):
        test_file = self.get_test_loc('debcon/copyright/dep5-rpm.copyright')
        expected_loc = 'debcon/copyright/dep5-rpm.copyright-expected.json'
        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)

    def test_get_paragraphs__from_copyrights_dep5_dropbear(self):
        test_file = self.get_test_loc('debcon/copyright/dropbear.copyright')
        expected_loc = 'debcon/copyright/dropbear.copyright-expected.json'
        results = list(debcon.get_paragraphs(test_file))
        self.check_json(results, expected_loc, regen=False)
