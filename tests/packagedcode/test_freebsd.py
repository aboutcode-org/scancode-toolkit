#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

import os.path
import yaml

from packagedcode import freebsd

from packages_test_utils import PackageTester


class TestFreeBSD(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_with_multi_licenses(self):
        test_file = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/multi_license/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_with_dual_licenses2(self):
        test_file = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license2/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_with_dual_licenses(self):
        test_file = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/dual_license/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_without_licenses(self):
        test_file = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/no_licenses/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_basic2(self):
        test_file = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic2/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_basic(self):
        test_file = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST')
        expected_loc = self.get_test_loc('freebsd/basic/+COMPACT_MANIFEST.expected')
        package = freebsd.parse(test_file)
        self.check_package(package, expected_loc, regen=False)
        package.validate()

    def test_parse_not_yaml(self):
        test_file = self.get_test_loc('freebsd/not_yaml/+COMPACT_MANIFEST')
        try:
            freebsd.parse(test_file)
        except yaml.YAMLError, e:
            assert 'while parsing a block node' in str(e)

    def test_parse_invalid_metafile(self):
        test_file = self.get_test_loc('freebsd/invalid/invalid_metafile')
        package = freebsd.parse(test_file)

        assert package == None
