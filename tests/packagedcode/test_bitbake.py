#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import bitbake

from scancode_config import REGEN_TEST_FIXTURES

from packages_test_utils import PackageTester


class TestBitbake(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_bitbake(self):
        test_file = self.get_test_loc('bitbake/netbase_6.1.bb')
        packages = bitbake.BitbakeBbManifestHandler.parse(location=test_file)
        expected_loc = self.get_test_loc('bitbake/netbase_6.1.bb-expected')
        self.check_packages_data(
            packages_data=packages,
            expected_loc=expected_loc,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_parse_bitbake_dependencies(self):
        test_file = self.get_test_loc('bitbake/initramfs-live-install-testfs_1.0.bb')
        packages = bitbake.BitbakeBbManifestHandler.parse(location=test_file)
        expected_loc = self.get_test_loc('bitbake/initramfs-live-install-testfs_1.0.bb-expected')
        self.check_packages_data(
            packages_data=packages,
            expected_loc=expected_loc,
            regen=REGEN_TEST_FIXTURES,
        )
