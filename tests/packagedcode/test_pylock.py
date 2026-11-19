#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packages_test_utils import PackageTester

from packagedcode import pylock


class TestPylockTomlHandler(PackageTester):
    # set path to data directory
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_pylock_parse(self):
        test_file = self.get_test_loc("pylock/pylock.toml")
        package = pylock.PylockTomlHandler.parse(test_file)
        expected_loc = self.get_test_loc("pylock/pylock_toml-expected.json")
        self.check_packages_data(package, expected_loc, regen=False)
