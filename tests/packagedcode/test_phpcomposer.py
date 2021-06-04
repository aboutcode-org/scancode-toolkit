#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
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
        assert list(phpcomposer.parse_person(test)) == expected
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
