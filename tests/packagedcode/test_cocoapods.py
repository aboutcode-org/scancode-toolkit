#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode.cocoapods import get_urls
from packagedcode.cocoapods import PodspecHandler
from packagedcode.cocoapods import PodspecJsonHandler
from packagedcode.cocoapods import PodfileLockHandler
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click


class TestCocoaPodspec(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podspec(self):
        test_file = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec')
        assert PodspecHandler.is_datafile(test_file)

    def test_cocoapods_can_parse_BadgeHub(self):
        test_file = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/BadgeHub.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_flutter_paytabs_bridge(self):
        test_file = self.get_test_loc('cocoapods/podspec/flutter_paytabs_bridge.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/flutter_paytabs_bridge.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_kmmWebSocket(self):
        test_file = self.get_test_loc('cocoapods/podspec/kmmWebSocket.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/kmmWebSocket.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_LoadingShimmer(self):
        test_file = self.get_test_loc('cocoapods/podspec/LoadingShimmer.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/LoadingShimmer.podspec.expected.json', must_exist=False)
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_nanopb(self):
        test_file = self.get_test_loc('cocoapods/podspec/nanopb.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/nanopb.podspec.expected.json', must_exist=False)
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_PayTabsSDK(self):
        test_file = self.get_test_loc('cocoapods/podspec/PayTabsSDK.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/PayTabsSDK.podspec.expected.json', must_exist=False)
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_RxDataSources(self):
        test_file = self.get_test_loc('cocoapods/podspec/RxDataSources.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/RxDataSources.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_Starscream(self):
        test_file = self.get_test_loc('cocoapods/podspec/Starscream.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/Starscream.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_parse_SwiftLib(self):
        test_file = self.get_test_loc('cocoapods/podspec/SwiftLib.podspec')
        expected_loc = self.get_test_loc('cocoapods/podspec/SwiftLib.podspec.expected.json')
        packages = PodspecHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_get_urls(self):
        result = get_urls(name=None, version=None, homepage_url=None, vcs_url=None)
        expected = {
            'api_data_url': None,
            'bug_tracking_url': None,
            'code_view_url': None,
            'repository_download_url': None,
            'repository_homepage_url': None,
        }
        assert expected == result

        result = get_urls(name='foo', version=None, homepage_url=None, vcs_url=None)
        expected = {
            'api_data_url': None,
            'bug_tracking_url': None,
            'code_view_url': None,
            'repository_download_url': None,
            'repository_homepage_url': 'https://cocoapods.org/pods/foo',
        }
        assert expected == result

        result = get_urls(name='foo', version='1.2.3', homepage_url=None, vcs_url=None)
        expected = {
            'api_data_url': 'https://raw.githubusercontent.com/CocoaPods/Specs/blob/master/Specs/a/c/b/foo/1.2.3/foo.podspec.json',
            'bug_tracking_url': None,
            'code_view_url': None,
            'repository_download_url': None,
            'repository_homepage_url': 'https://cocoapods.org/pods/foo',
        }
        assert expected == result

        result = get_urls(
            name='foo',
            version='1.2.3',
            homepage_url='https://home.org',
            vcs_url='httsp://github.com/foo/bar.git',
        )
        expected = {
            'api_data_url': 'https://raw.githubusercontent.com/CocoaPods/Specs/blob/master/Specs/a/c/b/foo/1.2.3/foo.podspec.json',
            'bug_tracking_url': 'httsp://github.com/foo/bar/issues/',
            'code_view_url': 'httsp://github.com/foo/bar/tree/1.2.3',
            'repository_download_url': 'httsp://github.com/foo/bar/archive/refs/tags/1.2.3.zip',
            'repository_homepage_url': 'https://cocoapods.org/pods/foo',
        }
        assert expected == result


class TestCocoaPodspecJson(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podspec_json(self):
        test_file = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json')
        assert PodspecJsonHandler.is_datafile(test_file)

    def test_cocoapods_can_parse_FirebaseAnalytics(self):
        test_file = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json')
        expected_loc = self.get_test_loc('cocoapods/podspec.json/FirebaseAnalytics.podspec.json.expected.json')
        packages = PodspecJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestCocoaPodfileLock(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_detect_podfile_lock(self):
        test_file = self.get_test_loc('cocoapods/podfile.lock/braintree_ios_Podfile.lock')
        assert PodfileLockHandler.is_datafile(test_file)

    def test_cocoapods_can_parse_braintree_ios(self):
        test_file = self.get_test_loc('cocoapods/podfile.lock/braintree_ios_Podfile.lock')
        expected_loc = self.get_test_loc('cocoapods/podfile.lock/braintree_ios_Podfile.lock.expected.json')
        packages = PodfileLockHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestCocoapodsEndToEndAssemble(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cocoapods_can_assemble_with_single_podspec(self):
        test_file = self.get_test_loc('cocoapods/assemble/single-podspec')
        expected_file = self.get_test_loc('cocoapods/assemble/single-podspec-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_multiple_podspec(self):
        test_file = self.get_test_loc('cocoapods/assemble/multiple-podspec')
        expected_file = self.get_test_loc('cocoapods/assemble/multiple-podspec-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_solo_podspec(self):
        test_file = self.get_test_loc('cocoapods/assemble/solo/RxDataSources.podspec')
        expected_file = self.get_test_loc('cocoapods/assemble/solo/RxDataSources.podspec-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_solo_podfile(self):
        test_file = self.get_test_loc('cocoapods/assemble/solo/Podfile')
        expected_file = self.get_test_loc('cocoapods/assemble/solo/Podfile-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_solo_podfile_lock(self):
        test_file = self.get_test_loc('cocoapods/assemble/solo/Podfile.lock')
        expected_file = self.get_test_loc('cocoapods/assemble/solo/Podfile.lock-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_many_podspecs_podfile_and_podfile_lock(self):
        test_file = self.get_test_loc('cocoapods/assemble/many-podspecs')
        expected_file = self.get_test_loc('cocoapods/assemble/many-podspecs-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_cocoapods_can_assemble_with_many_podspecs_podfile_and_podfile_lock_with_license(self):
        test_file = self.get_test_loc('cocoapods/assemble/many-podspecs')
        expected_file = self.get_test_loc('cocoapods/assemble/many-podspecs-with-license-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', '--license', test_file, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)
