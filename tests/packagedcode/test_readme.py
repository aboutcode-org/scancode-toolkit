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

from packagedcode import readme 
from packages_test_utils import PackageTester


class TestReadme(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_thirdparty_basic(self):
        test_file = self.get_test_loc('readme/thirdparty/basic/README.thirdparty')
        expected_loc = self.get_test_loc('readme/thirdparty/basic/README.thirdparty.expected')
        package = readme.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_google_basic(self):
        test_file = self.get_test_loc('readme/google/basic/README.google')
        expected_loc = self.get_test_loc('readme/google/basic/README.google.expected')
        package = readme.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_facebook_basic(self):
        test_file = self.get_test_loc('readme/facebook/basic/README.facebook')
        expected_loc = self.get_test_loc('readme/facebook/basic/README.facebook.expected')
        package = readme.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_chromium_basic(self):
        test_file = self.get_test_loc('readme/chromium/basic/README.chromium')
        expected_loc = self.get_test_loc('readme/chromium/basic/README.chromium.expected')
        package = readme.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_android_basic(self):
        test_file = self.get_test_loc('readme/android/basic/README.android')
        expected_loc = self.get_test_loc('readme/android/basic/README.android.expected')
        package = readme.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_invalid_readme(self):
        test_file = self.get_test_loc('readme/invalid/invalid_file')
        package = readme.parse(test_file)
        assert package == None
