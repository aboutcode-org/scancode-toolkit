#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from commoncode.system import py3
from commoncode.testcase import FileBasedTesting

from typecode import extractible


class TestExtractible(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test__can_extract(self):
        tests = (
            ('contenttype/archive/a.tar.gz', True),
            ('contenttype/archive/crashing-squashfs', False),
            ('contenttype/archive/dbase.fdt', False),
            ('contenttype/archive/e.tar', True),
            ('contenttype/archive/e.tar.bz2', True),
            ('contenttype/archive/e.tar.gz', True),
            ('contenttype/archive/file_4.26-1.diff.gz', True),
            ('contenttype/archive/posixnotgnu.tar', True),
            ('contenttype/archive/sqfs-gz.sqs', False),
            ('contenttype/archive/sqfs-lzo.sqs', False),
            ('contenttype/archive/sqfs-xz.sqs', False),
            ('contenttype/archive/win-archive.lib', False),
            ('contenttype/archive/test.tar.lzma', True if py3 else False),
            ('contenttype/archive/test.tar.xz', True if py3 else False),
            ('contenttype/archive/test.zip', True),
        )
        for location, expected in tests:
            test_file = self.get_test_loc(location)
            result = extractible._can_extract(test_file)
            assert result == expected, '{} should extractible: {}'.format(location, expected)
