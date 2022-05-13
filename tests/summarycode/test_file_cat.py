#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os

from commoncode.testcase import FileBasedTesting
from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Resource

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES
from summarycode import file_cat


class TestFileCat(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_ArchiveAndroid(self):
        test_resource = Resource(
            path='',
            is_file='file',
            name='baloney.apk',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert file_cat.ArchiveAndroid.categorize(test_resource)

# Original test from SPATS file-cat:

# class TestFileCat(FileBasedTesting):

#     test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

#     def test_ArchiveAndroid(self):
#         test_resource = Resource(
#             path='',
#             type='file',
#             name='',
#             extension='.apk',
#             mime_type='',
#             file_type='',
#             programming_language=''
#         )
#         assert file_cat_rules.ArchiveAndroid.categorize(test_resource)
