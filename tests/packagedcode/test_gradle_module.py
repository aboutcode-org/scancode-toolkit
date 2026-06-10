#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import gradle_module
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestGradleModule(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_datafile_basic(self):
        test_file = self.get_test_loc(
            'gradle_module/basic/converter-moshi-2.11.0.module'
        )
        assert gradle_module.GradleModuleHandler.is_datafile(test_file)

    def test_is_datafile_not_gradle(self):
        test_file = self.get_test_loc(
            'gradle_module/not-gradle/not-a-gradle-module.module'
        )
        assert not gradle_module.GradleModuleHandler.is_datafile(test_file)

    def test_parse_basic(self):
        test_file = self.get_test_loc(
            'gradle_module/basic/converter-moshi-2.11.0.module'
        )
        expected_loc = self.get_test_loc('gradle_module/basic/expected.json')
        packages = gradle_module.GradleModuleHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_no_variants(self):
        test_file = self.get_test_loc(
            'gradle_module/no-variants/minimal.module'
        )
        expected_loc = self.get_test_loc('gradle_module/no-variants/expected.json')
        packages = gradle_module.GradleModuleHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)
