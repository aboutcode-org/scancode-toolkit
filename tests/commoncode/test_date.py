#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
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
        assert as_yyyymmdd(result) == as_yyyymmdd(now)

    def test_get_file_mtime_for_a_modified_file(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()
        expected = u'1992-05-09 00:00:00'
        m_ts = (24 * 3600) * 134 + (24 * 3600 * 365) * 22
        # setting modified time to expected values
        os.utime(test_file, (m_ts, m_ts))
        assert commoncode.date.get_file_mtime(test_file) == expected

    def test_get_file_mtime_for_a_modified_file_2(self):
        test_file = self.get_temp_file()
        open(test_file, 'w').close()
        # setting modified time to expected values
        expected = u'2011-01-06 14:35:00'
        os.utime(test_file, (1294324500, 1294324500))
        assert commoncode.date.get_file_mtime(test_file) == expected
