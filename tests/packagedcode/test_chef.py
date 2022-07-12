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
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan


class TestChef(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_chef_metadata_json_is_package_data_file(self):
        test_file = self.get_test_loc('chef/basic/metadata.json')
        assert chef.ChefMetadataJsonHandler.is_datafile(test_file)

    def test_chef_metadata_rb_from_json(self):
        test_file = self.get_test_loc('chef/basic/metadata.json')
        expected_file = self.get_test_loc('chef/basic/metadata.json.expected')
        self.check_packages_data(
            chef.ChefMetadataJsonHandler.parse(test_file), expected_file, regen=REGEN_TEST_FIXTURES
        )

    def test_chef_metadata_rb_is_package_data_file(self):
        test_file = self.get_test_loc('chef/basic/metadata.rb')
        assert chef.ChefMetadataRbHandler.is_datafile(test_file)

    def test_parse_from_rb(self):
        test_file = self.get_test_loc('chef/basic/metadata.rb')
        expected_file = self.get_test_loc('chef/basic/metadata.rb.expected')
        self.check_packages_data(
            chef.ChefMetadataRbHandler.parse(test_file), expected_file, regen=REGEN_TEST_FIXTURES
        )

    def test_parse_from_rb_dependency_requirement(self):
        test_file = self.get_test_loc('chef/dependencies/metadata.rb')
        expected_file = self.get_test_loc('chef/dependencies/metadata.rb.expected')
        self.check_packages_data(
            chef.ChefMetadataRbHandler.parse(test_file), expected_file, regen=REGEN_TEST_FIXTURES
        )

    def test_build_package(self):
        package_data = dict(
            type='chef',
            name='test',
            version='0.01',
            description='test package',
            license='public-domain',
        )
        expected_file = self.get_test_loc('chef/basic/test_package.json.expected')
        self.check_package_data(
            chef.build_package(package_data, datasource_id='chef_cookbook_metadata_rb'),
            expected_file,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_build_package_long_description(self):
        package_data = dict(
            type='chef',
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
        )
        expected_file = self.get_test_loc('chef/basic/test_package.json.expected')
        self.check_package_data(
            chef.build_package(package_data, datasource_id='chef_cookbook_metadata_rb'),
            expected_file,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_build_package_dependencies(self):
        package_data = dict(
            type='chef',
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            dependencies={'test dependency': '0.01'},
        )
        expected_file = self.get_test_loc('chef/basic/test_package_dependencies.json.expected')
        self.check_package_data(
            chef.build_package(package_data, datasource_id='chef_cookbook_metadata_rb'),
            expected_file,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_build_package_parties(self):
        package_data = dict(
            type='chef',
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            maintainer='test maintainer',
            maintainer_email='test_maintainer@example.com',
        )
        expected_file = self.get_test_loc('chef/basic/test_package_parties.json.expected')
        self.check_package_data(
            chef.build_package(package_data, datasource_id='chef_cookbook_metadata_rb'),
            expected_file,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_build_package_code_view_url_and_bug_tracking_url(self):
        package_data = dict(
            type='chef',
            name='test',
            version='0.01',
            long_description='test package',
            license='public-domain',
            source_url='example.com',
            issues_url='example.com/issues',
        )
        expected_file = self.get_test_loc(
            'chef/basic/test_package_code_view_url_and_bug_tracking_url.json.expected'
        )
        self.check_package_data(
            chef.build_package(package_data, datasource_id='chef_cookbook_metadata_rb'),
            expected_file,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_scan_cli_works(self):
        test_file = self.get_test_loc('chef/package/')
        expected_file = self.get_test_loc('chef/package.scan.expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )
