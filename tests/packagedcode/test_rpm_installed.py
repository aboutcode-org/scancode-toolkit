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
from functools import partial
from unittest import skipIf

import pytest
from commoncode.system import on_linux

from packagedcode.rpm import RpmInstalledSqliteDatabaseHandler
from packagedcode import rpm_installed
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


def check_files_equals(result, expected, regen=REGEN_TEST_FIXTURES):
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


rpm_datasource_id = RpmInstalledSqliteDatabaseHandler.datasource_id
rpm_package_type = RpmInstalledSqliteDatabaseHandler.default_package_type

parse_rpm_xmlish = partial(
    rpm_installed.parse_rpm_xmlish,
    datasource_id=RpmInstalledSqliteDatabaseHandler.datasource_id,
    package_type=RpmInstalledSqliteDatabaseHandler.default_package_type,
)


class TestRpmInstalled(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(not on_linux, 'RPM command is only available on Linux')
    def test_collect_installed_rpmdb_xmlish_from_rootfs(self):
        test_root_dir = self.extract_test_tar('rpm_installed/rootfs/var-lib-rpm.tar.xz')
        test_root_dir = os.path.join(test_root_dir, 'rootfs')
        result_xmlish_loc = rpm_installed.collect_installed_rpmdb_xmlish_from_rootfs(test_root_dir)
        expected_xmlish_loc = self.extract_test_tar('rpm_installed/rootfs/rpm.xmlish.expected.tar.xz')
        expected_xmlish_loc = os.path.join(expected_xmlish_loc, 'rpm.xmlish.expected')
        check_files_equals(result_xmlish_loc, expected_xmlish_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish(self):
        test_installed = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_does_not_fail_with_empty_or_missing_location(self):
        parse_rpm_xmlish(location=None)
        parse_rpm_xmlish(location='')
        parse_rpm_xmlish(location='/foo/bar/does-not-exists')

    def test_parse_rpm_xmlish_can_detect_license(self):
        test_installed = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/xmlish/centos-5-rpms.xmlish-with-license-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_can_parse_centos8(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/centos-8-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/centos-8-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_can_parse_fc33(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/fc33-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/fc33-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_can_parse_openmandriva(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/openmandriva-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/openmandriva-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_can_parse_opensuse(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/opensuse-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/opensuse-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_rpm_xmlish_can_parse_rhel(self):
        test_installed = self.get_test_loc('rpm_installed/distro-xmlish/rhel-rpms.xmlish')
        expected = self.get_test_loc('rpm_installed/distro-xmlish/rhel-rpms.xmlish-expected.json')
        packages = parse_rpm_xmlish(location=test_installed)
        result = [package.to_dict(_detailed=True) for package in packages]
        result = json.loads(json.dumps(result))
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    @pytest.mark.scanslow
    @pytest.mark.skipif(not on_linux, reason='RPM command is only available on Linux')
    def test_scan_system_package_end_to_end_installed_rpms_fedora_bdb(self):
        test_dir = self.extract_test_tar('rpm_installed/end-to-end/bdb-fedora-rootfs.tar.xz')
        test_dir = os.path.join(test_dir, 'rootfs')
        expected_file = self.get_test_loc(f'rpm_installed/end-to-end/bdb-fedora-rootfs.tar.xz-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
