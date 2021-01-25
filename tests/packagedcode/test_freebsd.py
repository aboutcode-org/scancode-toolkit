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

import os.path
import saneyaml

from packagedcode import freebsd
from packages_test_utils import PackageTester


class TestFreeBSD(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_with_multi_licenses(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_dual_licenses2(self):
        test_file = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_with_dual_licenses(self):
        test_file = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_without_licenses(self):
        test_file = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_basic2(self):
        test_file = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_basic(self):
        test_file = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_not_yaml(self):
        test_file = self.get_test_loc('freebsd/not_yaml/+COMPACT_MANIFEST')
        try:
            freebsd.parse(test_file)
        except saneyaml.YAMLError as e:
            assert 'while parsing a block node' in str(e)

    def test_parse_invalid_metafile(self):
        test_file = self.get_test_loc('freebsd/invalid/invalid_metafile')
        package = freebsd.parse(test_file)
        assert package == None
