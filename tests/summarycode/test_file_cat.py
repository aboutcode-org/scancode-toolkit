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

import attr

from commoncode.testcase import FileBasedTesting
from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Resource

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES
from scancode.plugin_info import InfoScanner
from summarycode import file_cat


resource_class = attr.make_class(
        name='TestResource',
        attrs=InfoScanner.resource_attributes,
        slots=True,
        bases=(Resource,)
    )


class TestFileCat(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_ArchiveAndroid(self):
        test_resource_01 = resource_class(
            name='foo.apk',
            location='',
            path='',
            rid='',
            pid='',
            is_file='file',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert file_cat.ArchiveAndroid.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == 'archive'

        test_resource_02 = resource_class(
            name='foo.aar',
            location='',
            path='',
            rid='',
            pid='',
            is_file='file',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert file_cat.ArchiveAndroid.categorize(test_resource_02)
        assert file_cat.categorize_resource(test_resource_02).file_category == 'archive'

    def test_ArchiveDebian(self):
        test_resource_01 = resource_class(
            name='foo.deb',
            location='',
            path='',
            rid='',
            pid='',
            is_file='file',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert file_cat.ArchiveDebian.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == 'archive'

        test_resource_02 = resource_class(
            name='foo.2',
            location='',
            path='',
            rid='',
            pid='',
            is_file='file',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert not file_cat.ArchiveDebian.categorize(test_resource_02)

    def test_ArchiveGeneral(self):
        test_resource_01 = resource_class(
            name='foo.7zip',
            location='',
            path='',
            rid='',
            pid='',
            is_file='file',
            mime_type='',
            file_type='',
            programming_language=''
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == 'archive'
