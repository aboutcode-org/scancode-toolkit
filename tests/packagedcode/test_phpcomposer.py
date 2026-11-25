#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import phpcomposer
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


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

    def test_is_manifest_php_composer_json(self):
        test_file = self.get_test_loc('phpcomposer/a-timer/composer.json')
        assert phpcomposer.PhpComposerJsonHandler.is_datafile(test_file)

    def test_parse_atimer(self):
        test_file = self.get_test_loc('phpcomposer/a-timer/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/a-timer/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_framework(self):
        test_file = self.get_test_loc('phpcomposer/framework/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/framework/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_slim(self):
        test_file = self.get_test_loc('phpcomposer/slim/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/slim/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_modern(self):
        test_file = self.get_test_loc('phpcomposer/modern/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/modern/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_fake_license1(self):
        test_file = self.get_test_loc('phpcomposer/fake/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_fake_license2(self):
        test_file = self.get_test_loc('phpcomposer/fake2/composer.json')
        expected_loc = self.get_test_loc('phpcomposer/fake2/composer.json.expected')
        packages = phpcomposer.PhpComposerJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_is_manifest_php_composer_lock(self):
        test_file = self.get_test_loc('phpcomposer/composer.lock')
        assert phpcomposer.PhpComposerLockHandler.is_datafile(test_file)

    def test_parse_composer_lock(self):
        test_file = self.get_test_loc('phpcomposer/composer.lock')
        expected_loc = self.get_test_loc('phpcomposer/composer.lock-expected.json')
        packages = phpcomposer.PhpComposerLockHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_build_package_data_keywords_list(self):
        data = {
            'name': 'monolog/monolog',
            'keywords': ['logging', 'psr-3', 'log'],
        }
        package = phpcomposer.build_package_data(data)
        assert package.keywords == ['logging', 'psr-3', 'log']

    def test_build_package_data_keywords_comma_separated_string(self):
        data = {
            'name': 'monolog/monolog',
            'keywords': 'logging, psr-3, log',
        }
        package = phpcomposer.build_package_data(data)
        assert package.keywords == ['logging', 'psr-3', 'log']

    def test_build_package_data_keywords_single_string(self):
        data = {
            'name': 'monolog/monolog',
            'keywords': 'logging',
        }
        package = phpcomposer.build_package_data(data)
        assert package.keywords == ['logging']

    def test_source_mapper_with_reference(self):
        data = {
            'name': 'monolog/monolog',
            'source': {
                'type': 'git',
                'url': 'https://github.com/Seldaek/monolog.git',
                'reference': 'abc1234',
            },
        }
        package = phpcomposer.build_package_data(data)
        assert package.vcs_url == 'git+https://github.com/Seldaek/monolog.git@abc1234'

    def test_source_mapper_without_reference(self):
        data = {
            'name': 'monolog/monolog',
            'source': {
                'type': 'git',
                'url': 'https://github.com/Seldaek/monolog.git',
            },
        }
        package = phpcomposer.build_package_data(data)
        assert package.vcs_url == 'git+https://github.com/Seldaek/monolog.git'
        assert '@None' not in package.vcs_url
