#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from commoncode.testcase import FileBasedTesting
from licensedcode import legal

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSpecialFiles(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_license_special_files(self):
        tests = [
            ('legal/COPYING', 'yes'),
            ('legal/Copyrights', 'maybe'),
            ('legal/LICENSE', 'yes'),
            ('legal/Notice', 'yes'),
            ('legal/no_license_in_here.java', 'maybe'),
            ('legal/noticE.html', 'yes'),
            ('legal/useless_notice.txt', 'maybe')
        ]

        for tf, expected in tests:
            assert expected == legal.is_special_legal_file(self.get_test_loc(tf))
