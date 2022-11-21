#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from commoncode import text
from commoncode.testcase import FileBasedTesting

from packagedcode import rubygems
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES

# TODO: Add test with https://rubygems.org/gems/pbox2d/versions/1.0.3-java
# this is a multiple personality package (Java  and Ruby)
# see also https://rubygems.org/downloads/jaro_winkler-1.5.1-java.gem


class TestGemSpec(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_ruby_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/address_standardization.gemspec')
        assert rubygems.GemspecHandler.is_datafile(test_file)

    def test_rubygems_can_parse_gemspec_address_standardization_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/address_standardization.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/address_standardization.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_can_parse_gemspec_arel_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/arel.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/arel.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_cat_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/cat.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/cat.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_github_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/github.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/github.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_mecab_ruby_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/mecab-ruby.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/mecab-ruby.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_oj_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/oj.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/oj.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_rubocop_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/rubocop.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/rubocop.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_rubygems_with_variables_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/with_variables.gemspec')
        expected_loc = self.get_test_loc('rubygems/gemspec/with_variables.gemspec.expected.json')
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestRubyGemMetadata(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_ruby_archive_extracted(self):
        test_file = self.get_test_loc('rubygems/metadata/metadata.gz-extract')
        assert rubygems.GemMetadataArchiveExtractedHandler.is_datafile(test_file)

    def test_build_rubygem_package_does_not_crash(self):
        test_file = self.get_test_loc('rubygems/metadata/metadata.gz-extract')
        rubygems.GemMetadataArchiveExtractedHandler.parse(test_file)


def relative_walk(dir_path, extension='.gem'):
    """
    Walk `dir_path` and yield paths that end with `extension` relative to
    dir_path for.
    """
    for base_dir, _dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith(extension):
                file_path = os.path.join(base_dir, file_name)
                file_path = file_path.replace(dir_path, '', 1)
                file_path = file_path.strip(os.path.sep)
                yield file_path


def create_test_function(test_loc, test_name, regen=REGEN_TEST_FIXTURES):
    """
    Return a test function closed on test arguments.
    """

    # closure on the test params
    def check_rubygem(self):
        loc = self.get_test_loc(test_loc)
        expected_json_loc = loc + '.json'
        packages = list(rubygems.GemArchiveHandler.parse(location=loc))
        package = packages[0]
        package.populate_license_fields()
        package = [package.to_dict()]
        if regen:
            with io.open(expected_json_loc, 'w') as ex:
                json.dump(package, ex, indent=2)

        with io.open(expected_json_loc, encoding='utf-8') as ex:
            expected = json.load(ex)
        assert package == expected

    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    check_rubygem.__name__ = test_name

    return check_rubygem


class TestRubyGemsDataDriven(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def build_tests(test_dir, clazz, prefix='test_rubygems_parse_', regen=REGEN_TEST_FIXTURES):
    """
    Dynamically build test methods for each gem in `test_dir`  and
    attach the test method to the `clazz` class.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    test_dir = os.path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir):
        test_name = prefix + text.python_safe_name(test_file)
        test_pom_loc = os.path.join(test_dir, test_file)
        test_method = create_test_function(test_pom_loc, test_name, regen=regen)
        # attach that method to the class
        setattr(clazz, test_name, test_method)


class TestGemfileLock(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_ruby_gemfilelock(self):
        test_file = self.get_test_loc('rubygems/gemfile-lock/Gemfile.lock')
        assert rubygems.GemfileLockHandler.is_datafile(test_file)

    def test_ruby_gemfile_lock_as_dict(self):
        test_file = self.get_test_loc('rubygems/gemfile-lock/Gemfile.lock')
        expected_loc = self.get_test_loc('rubygems/gemfile-lock/Gemfile.lock.expected')
        packages = rubygems.GemfileLockHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_ruby_gemfile_lock_with_path_as_dict(self):
        test_file = self.get_test_loc('rubygems/gemfile-lock/path/Gemfile.lock')
        expected_loc = self.get_test_loc('rubygems/gemfile-lock/path/Gemfile.lock.expected')
        packages = rubygems.GemfileLockHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


build_tests(
    test_dir='rubygems/gem',
    clazz=TestRubyGemsDataDriven,
    prefix='test_get_gem_package_',
    regen=REGEN_TEST_FIXTURES
)
