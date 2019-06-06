#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

import os

from packages_test_utils import PackageTester

from packagedcode import phpcomposer


class TestPHPcomposer(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_person(self):
        test = [
            {
                "name": "Nils Adermann",
                "email": "naderman@naderman.de",
                "homepage": "http://www.naderman.de",
                "role": "Developer"
            },
            {
                "name": "Jordi Boggiano",
                "email": "j.boggiano@seld.be",
                "homepage": "http://seld.be",
                "role": "Developer"
            }
        ]
        expected = [('Nils Adermann', 'Developer', 'naderman@naderman.de', 'http://www.naderman.de'),
                    ('Jordi Boggiano', 'Developer', 'j.boggiano@seld.be', 'http://seld.be')
        ]
        assert expected == list(phpcomposer.parse_person(test))

    def test_parse_atimer(self):
        test_file = self.get_test_loc('phpcomposer/a-timer/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/a-timer/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_framework(self):
        test_file = self.get_test_loc('phpcomposer/framework/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/framework/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_slim(self):
        test_file = self.get_test_loc('phpcomposer/slim/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/slim/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_modern(self):
        test_file = self.get_test_loc('phpcomposer/modern/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/modern/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_fake_license1(self):
        test_file = self.get_test_loc('phpcomposer/fake/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_fake_license2(self):
        test_file = self.get_test_loc('phpcomposer/fake2/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake2/composer.json.expected')
        package = phpcomposer.parse(test_file)
        self.check_package(package, expected_loc, regen=False)