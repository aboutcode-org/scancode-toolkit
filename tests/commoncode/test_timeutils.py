#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from datetime import datetime

from commoncode.testcase import FileBasedTesting
from commoncode.timeutils import time2tstamp
from commoncode.timeutils import tstamp2time
from commoncode.timeutils import UTC


class TestTimeStamp(FileBasedTesting):

    def test_time2tstamp_is_path_safe_and_file_is_writable(self):
        ts = time2tstamp()
        tf = self.get_temp_file(extension='ext', dir_name=ts, file_name=ts)
        fd = open(tf, 'w')
        fd.write('a')
        fd.close()

    def test_time2tstamp_accepts_existing_datetimes(self):
        ts = time2tstamp()
        tf = self.get_temp_file(extension='ext', dir_name=ts, file_name=ts)
        fd = open(tf, 'w')
        fd.write('a')
        fd.close()

    def test_time2tstamp_raises_on_non_datetime(self):
        self.assertRaises(AttributeError, time2tstamp, 'some')
        self.assertRaises(AttributeError, time2tstamp, 1)

    def test_time2tstamp_tstamp2time_is_idempotent(self):
        dt = datetime.utcnow()
        ts = time2tstamp(dt)
        dt_from_ts = tstamp2time(ts)
        assert dt_from_ts == dt

    def test_tstamp2time_format(self):
        import re
        ts = time2tstamp()
        pat = r'^20\d\d-[0-1][0-9]-[0-3]\dT[0-2]\d[0-6]\d[0-6]\d.\d\d\d\d\d\d$'
        assert re.match(pat, ts)

    def test_tstamp2time(self):
        dt_from_ts = tstamp2time('2010-11-12T131415.000016')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=16, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time2(self):
        dt_from_ts = tstamp2time('20101112T131415.000016')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=16, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time3(self):
        dt_from_ts = tstamp2time('20101112T131415.000016Z')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=16, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time4(self):
        dt_from_ts = tstamp2time('2010-11-12T131415')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time5(self):
        dt_from_ts = tstamp2time('2010-11-12T13:14:15')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time6(self):
        dt_from_ts = tstamp2time('20101112T13:14:15')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time7(self):
        dt_from_ts = tstamp2time('20101112T13:14:15Z')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time8(self):
        dt_from_ts = tstamp2time('20101112T13:14:15Z')
        assert datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time9(self):
        dt_from_ts = tstamp2time('2010-06-30T21:26:40.000Z')
        assert datetime(year=2010, month=6, day=30, hour=21, minute=26, second=40, microsecond=0, tzinfo=UTC()) == dt_from_ts

    def test_tstamp2time_raise(self):
        self.assertRaises(ValueError, tstamp2time, '201011A12T13:14:15Z')
