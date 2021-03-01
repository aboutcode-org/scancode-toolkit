# # -*- coding: utf-8 -*-

# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import rpm_installed
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester


class TestRpmInstalled(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_xml_from_rpm(self):
        test_installed = self.get_test_loc('rpm_installed/centos-5-rpms.txt')
        result = [package.to_dict(_detailed=True)
            for package in rpm_installed.parse_rpm_db(test_installed)]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=False)
