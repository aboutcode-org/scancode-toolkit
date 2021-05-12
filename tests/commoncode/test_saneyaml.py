#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
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
        assert without_tags == with_tags
