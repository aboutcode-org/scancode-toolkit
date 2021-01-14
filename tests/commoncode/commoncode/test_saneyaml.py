#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
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

import os

import saneyaml

from commoncode.testcase import FileBasedTesting

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSaneyaml(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_load_with_and_without_tags(self):
        test_file_with_tag = self.get_test_loc('saneyaml/metadata1')
        test_file_without_tag = self.get_test_loc('saneyaml/metadata1.notag')
        with_tags = saneyaml.load(open(test_file_with_tag, 'rb').read())
        without_tags = saneyaml.load(open(test_file_without_tag, 'rb').read())
        assert with_tags == without_tags
