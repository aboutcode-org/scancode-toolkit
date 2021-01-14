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

from datetime import datetime

import commoncode.date

from commoncode import testcase


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
