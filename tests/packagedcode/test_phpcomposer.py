#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_framework(self):
        test_file = self.get_test_loc('phpcomposer/framework/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/framework/composer.json.expected')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_slim(self):
        test_file = self.get_test_loc('phpcomposer/slim/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/slim/composer.json.expected')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_modern(self):
        test_file = self.get_test_loc('phpcomposer/modern/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/modern/composer.json.expected')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_fake_license1(self):
        test_file = self.get_test_loc('phpcomposer/fake/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake/composer.json.expected')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_fake_license2(self):
        test_file = self.get_test_loc('phpcomposer/fake2/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake2/composer.json.expected')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_composer_lock(self):
        test_file = self.get_test_loc('phpcomposer/composer.lock')
        expected_loc = self.get_test_loc('phpcomposer/composer.lock-expected.json')
        packages = phpcomposer.parse(test_file)
        self.check_packages(packages, expected_loc, regen=False)
