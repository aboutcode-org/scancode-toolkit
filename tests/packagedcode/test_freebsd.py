#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path
import saneyaml

from packagedcode import freebsd
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestFreeBSD(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_compact_manifest(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        assert freebsd.CompactManifestHandler.is_datafile(test_file)

    def test_parse_with_multi_licenses(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_dual_licenses2(self):
        test_file = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_with_dual_licenses(self):
        test_file = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_without_licenses(self):
        test_file = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_basic2(self):
        test_file = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_basic(self):
        test_file = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST.expected')
        package = freebsd.CompactManifestHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_not_yaml(self):
        test_file = self.get_test_loc('freebsd/not_yaml/+COMPACT_MANIFEST')
        try:
            freebsd.CompactManifestHandler.parse(test_file)
        except saneyaml.YAMLError as e:
            assert 'while parsing a block node' in str(e)
