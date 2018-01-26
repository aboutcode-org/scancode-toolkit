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

from datetime import datetime
import os

from commoncode import testcase
import commoncode.date


class TestDate(testcase.FileBasedTesting):

    def test_secs_from_epoch_can_handle_micro_and_nano_secs(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()
        # setting modified time to desired values
        os.utime(test_file, (1301420665.046481, 1301420665.046481))
        # otherwise the issue does not happen (ie. on mac)
        if 1301420665.0 < os.stat(test_file).st_mtime:
            file_date = commoncode.date.get_file_mtime(test_file)
            commoncode.date.secs_from_epoch(file_date)

    def test_get_file_mtime_for_a_new_file(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()

        def as_yyyymmdd(s):
            return s[:10]

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        result = commoncode.date.get_file_mtime(test_file)
        assert as_yyyymmdd(now) == as_yyyymmdd(result)

    def test_get_file_mtime_for_a_modified_file(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()
        expected = u'1992-05-09 00:00:00'
        m_ts = (24 * 3600) * 134 + (24 * 3600 * 365) * 22
        # setting modified time to expected values
        os.utime(test_file, (m_ts, m_ts))
        assert expected == commoncode.date.get_file_mtime(test_file)

    def test_get_file_mtime_for_a_modified_file_2(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()
        # setting modified time to expected values
        expected = u'2011-01-06 14:35:00'
        os.utime(test_file, (1294324500, 1294324500))
        assert expected == commoncode.date.get_file_mtime(test_file)
