#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import chef
from packages_test_utils import PackageTester


class TestChef(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_from_json(self):
        test_file = self.get_test_loc('chef/basic/metadata.json')
        expected_file = self.get_test_loc('chef/basic/metadata.json.expected')
        self.check_package(chef.parse(test_file), expected_file, regen=False)

    def test_parse_from_rb(self):
        test_file = self.get_test_loc('chef/basic/metadata.rb')
        expected_file = self.get_test_loc('chef/basic/metadata.rb.expected')
        self.check_package(chef.parse(test_file), expected_file, regen=False)

    def test_parse_from_rb_dependency_requirement(self):
        test_file = self.get_test_loc('chef/dependencies/metadata.rb')
        expected_file = self.get_test_loc('chef/dependencies/metadata.rb.expected')
        self.check_package(chef.parse(test_file), expected_file, regen=False)

    def test_build_package(self):
        package_data = dict(
            name='test',
            version='0.01',
            description='test package',
            license='public-domain'
        )
        expected_file = self.get_test_loc('chef/basic/test_package.json.expected')
        self.check_package(chef.build_package(package_data), expected_file, regen=False)

    def test_build_package_long_description(self):
        package_data = dict(
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain'
        )
        expected_file = self.get_test_loc('chef/basic/test_package.json.expected')
        self.check_package(chef.build_package(package_data), expected_file, regen=False)

    def test_build_package_dependencies(self):
        package_data = dict(
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            dependencies={'test dependency': '0.01'}
        )
        expected_file = self.get_test_loc('chef/basic/test_package_dependencies.json.expected')
        self.check_package(chef.build_package(package_data), expected_file, regen=False)

    def test_build_package_parties(self):
        package_data = dict(
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            maintainer='test maintainer',
            maintainer_email='test_maintainer@example.com',
        )
        expected_file = self.get_test_loc('chef/basic/test_package_parties.json.expected')
        self.check_package(chef.build_package(package_data), expected_file, regen=False)

    def test_build_package_code_view_url_and_bug_tracking_url(self):
        package_data = dict(
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            source_url='example.com',
            issues_url='example.com/issues'
        )
        expected_file = self.get_test_loc('chef/basic/test_package_code_view_url_and_bug_tracking_url.json.expected')
        self.check_package(chef.build_package(package_data), expected_file, regen=False)
