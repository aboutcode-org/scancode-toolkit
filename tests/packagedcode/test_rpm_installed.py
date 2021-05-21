# # -*- coding: utf-8 -*-

# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
from unittest import skipIf

from commoncode.system import on_linux

from packagedcode import rpm_installed
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester


def check_files_equals(result, expected, regen=False):
    """
    Check equality between two test text files.
    Regen the expected file if regen is True.
    """
    with open(result) as res:
        result_content = res.read()

    if regen:
        expected_content = result_content
        with open(expected, 'w') as ex:
            ex.write(expected_content)
    else:
        with open(result) as exp:
            expected_content = exp.read()
    assert result_content == expected_content


class TestRpmInstalled(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(not on_linux, 'RPM command is only available on Linux')
    def test_collect_installed_rpmdb_xmlish_from_rootfs(self):
        test_root_dir = self.extract_test_tar('rpm_installed/rootfs/var-lib-rpm.tar.xz')
        test_root_dir = os.path.join(test_root_dir, 'rootfs')
        result_xmlish_loc = rpm_installed.collect_installed_rpmdb_xmlish_from_rootfs(test_root_dir)
        expected_xmlish_loc = self.extract_test_tar('rpm_installed/rootfs/rpm.xmlish.expected.tar.xz')
        expected_xmlish_loc = os.path.join(expected_xmlish_loc, 'rpm.xmlish.expected')
        check_files_equals(result_xmlish_loc, expected_xmlish_loc, regen=False)

    def test_parse_rpm_xmlish(self):
        test_installed = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_does_not_with_empty_or_missing_location(self):
        rpm_installed.parse_rpm_xmlish(None)
        rpm_installed.parse_rpm_xmlish('')
        rpm_installed.parse_rpm_xmlish('/foo/bar/does-not-exists')

    def test_parse_rpm_xmlish_can_detect_license(self):
        test_installed = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish-with-license-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_can_parse_centos8(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/centos-8-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/centos-8-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_can_parse_fc33(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/fc33-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/fc33-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_can_parse_openmandriva(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/openmandriva-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/openmandriva-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_can_parse_opensuse(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/opensuse-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/opensuse-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_rpm_xmlish_can_parse_rhel(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/rhel-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/rhel-rpms.xmlish-expected.json')
        packages = rpm_installed.parse_rpm_xmlish(test_installed, detect_licenses=True)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=False)
