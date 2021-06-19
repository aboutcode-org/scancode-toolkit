
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import pytest

from packagedcode.windows_helpers import parse

from packages_test_utils import PackageTester


class TestWindowsHelpers(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_msi(self):
        test_file = self.get_test_loc('windows_helpers/msi/7z1900-x64.msi')
        expected_loc = self.get_test_loc('windows_helpers/msi/7z1900-x64.msi.expected')
        package = parse(test_file)
        self.check_package(package, expected_loc, regen=False)
