#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os.path

from packagedcode import about

from packages_test_utils import PackageTester


class TestAbout(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_about_file_home_url(self):
        test_file = self.get_test_loc('about/apipkg.ABOUT')
        package = about.parse(test_file)
        expected_loc = self.get_test_loc('about/apipkg.ABOUT-expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_about_file_homepage_url(self):
        test_file = self.get_test_loc('about/appdirs.ABOUT')
        package = about.parse(test_file)
        expected_loc = self.get_test_loc('about/appdirs.ABOUT-expected')
        self.check_package(package, expected_loc, regen=False)
