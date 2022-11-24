#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest
from commoncode.testcase import FileBasedTesting

from packagedcode import rubygems
from packages_test_utils import get_test_file_paths
from packages_test_utils import PackageTesterBase
from scancode_config import REGEN_TEST_FIXTURES

# TODO: Add test with https://rubygems.org/gems/pbox2d/versions/1.0.3-java
# this is a multiple personality package (Java  and Ruby)
# see also https://rubygems.org/downloads/jaro_winkler-1.5.1-java.gem

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestGemMetadataArchiveExtractedHandler(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_is_datafile_ruby_archive_extracted(self):
        test_file = self.get_test_loc('rubygems/metadata/metadata.gz-extract')
        assert rubygems.GemMetadataArchiveExtractedHandler.is_datafile(test_file)

    def test_parse_ruby_archive_extracted(self):
        test_file = self.get_test_loc('rubygems/metadata/metadata.gz-extract')
        rubygems.GemMetadataArchiveExtractedHandler.parse(test_file)


class TestGemspecHandler(PackageTesterBase):
    test_data_dir = TEST_DATA_DIR

    def test_is_datafile_ruby_gemspec(self):
        test_file = self.get_test_loc('rubygems/gemspec/address_standardization.gemspec')
        assert rubygems.GemspecHandler.is_datafile(test_file)

    gemspecs = (
        list(get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/gemfile/**/*.gemspec"))
        +list(get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/gemspec/**/*.gemspec"))
    )

    @pytest.mark.parametrize("test_path", gemspecs)
    def test_parse_gemspec(self, test_path, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc(test_path)
        expected_loc = f'{test_file}.expected.json'
        packages = rubygems.GemspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, must_exist=False, regen=regen)


class TestGemArchiveHandler(PackageTesterBase):
    test_data_dir = TEST_DATA_DIR

    def test_is_datafile_gem(self):
        test_file = self.get_test_loc('rubygems/gem/a_okay-0.1.0.gem')
        assert rubygems.GemArchiveHandler.is_datafile(test_file)

    @pytest.mark.parametrize(
        "test_path",
        get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/gem/**/*.gem")
    )
    def test_parse_dot_gem_archive(self, test_path, regen=REGEN_TEST_FIXTURES):
        test_loc = self.get_test_loc(test_path)
        expected_loc = test_loc + '-expected.json'
        packages = list(rubygems.GemArchiveHandler.parse(location=test_loc))
        for p in packages:
            p.populate_license_fields()
        self.check_packages_data(packages, expected_loc, must_exist=False, regen=regen)


class TestGemfileAndGemfileLockHandler(PackageTesterBase):
    test_data_dir = TEST_DATA_DIR

    def test_is_datafile_ruby_gemfile(self):
        test_file = self.get_test_loc('rubygems/gemfile/1/Gemfile')
        assert rubygems.GemfileHandler.is_datafile(test_file)

    def test_is_datafile_ruby_gemfilelock(self):
        test_file = self.get_test_loc('rubygems/gemfile/gemfile-lock/Gemfile.lock')
        assert rubygems.GemfileLockHandler.is_datafile(test_file)

    @pytest.mark.parametrize(
        "test_path",
        get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/gemfile/**/Gemfile")
    )
    def test_parse_gemfile(self, test_path, regen=REGEN_TEST_FIXTURES):
        test_loc = self.get_test_loc(test_path)
        expected_loc = test_loc + '-expected.json'
        packages = list(rubygems.GemfileHandler.parse(location=test_loc))
        self.check_packages_data(packages, expected_loc, must_exist=False, regen=regen)

    @pytest.mark.parametrize(
        "test_path",
        get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/gemfile/**/Gemfile.lock")
    )
    def test_parse_gemfile_lock(self, test_path, regen=REGEN_TEST_FIXTURES):
        test_loc = self.get_test_loc(test_path)
        expected_loc = test_loc + '-expected.json'
        packages = list(rubygems.GemfileLockHandler.parse(location=test_loc))
        self.check_packages_data(packages, expected_loc, must_exist=False, regen=regen)

