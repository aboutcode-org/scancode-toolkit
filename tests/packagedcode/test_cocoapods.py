#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode.cocoapods import Podspec
from packagedcode.cocoapods import PodfileLock
from packagedcode.cocoapods import PodspecJson
from packages_test_utils import PackageTester


class TestCocoaPodspec(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podspec(self):
        test_file = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec')
        assert Podspec.is_package_data_file(test_file)

    def test_cocoapods_can_parse_BadgeHub(self):
        test_file = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec.expected.json')
        packages = Podspec.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_cocoapods_can_parse_LoadingShimmer(self):
        test_file = self.get_test_loc('cocoapods/podspec/LoadingShimmer.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/LoadingShimmer.podspec.expected.json')
        packages = Podspec.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_cocoapods_can_parse_nanopb(self):
        test_file = self.get_test_loc('cocoapods/podspec/nanopb.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/nanopb.podspec.expected.json')
        packages = Podspec.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_cocoapods_can_parse_Starscream(self):
        test_file = self.get_test_loc('cocoapods/podspec/Starscream.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/Starscream.podspec.expected.json')
        packages = Podspec.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)

    def test_cocoapods_can_parse_SwiftLib(self):
        test_file = self.get_test_loc('cocoapods/podspec/SwiftLib.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/SwiftLib.podspec.expected.json')
        packages = Podspec.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)


class TestCocoaPodspecJson(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podspec_json(self):
        test_file = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json')
        assert PodspecJson.is_package_data_file(test_file)

    def test_cocoapods_can_parse_FirebaseAnalytics(self):
        test_file = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json')
        expected_loc = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json.expected.json')
        packages = PodspecJson.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)


class TestCocoaPodfileLock(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podfile_lock(self):
        test_file = self.get_test_loc('cocoapods/podfle.lock/braintree_ios_Podfile.lock')
        assert PodfileLock.is_package_data_file(test_file)

    def test_cocoapods_can_parse_braintree_ios(self):
        test_file = self.get_test_loc('cocoapods/podfle.lock/braintree_ios_Podfile.lock')
        expected_loc = self.get_test_loc('cocoapods/podfle.lock/braintree_ios_Podfile.lock.expected.json')
        packages = PodfileLock.recognize(test_file)
        self.check_packages(packages, expected_loc, regen=False)
