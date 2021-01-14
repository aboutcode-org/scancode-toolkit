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

import calendar
from datetime import datetime
import os


def isoformat(utc_date):
    return datetime.isoformat(utc_date).replace('T', ' ')


def get_file_mtime(location, iso=True):
    """
    Return a string containing the last modified date of a file formatted
    as an ISO time stamp if ISO is True or as a raw number since epoch.
    """
    date = ''
    # FIXME: use file types
    if not os.path.isdir(location):
        mtime = os.stat(location).st_mtime
        if iso:
            utc_date = datetime.utcfromtimestamp(mtime)
            date = isoformat(utc_date)
        else:
            date = str(mtime)
    return date


def secs_from_epoch(d):
    """
    Return a number of seconds since epoch for a date time stamp
    """
    # FIXME: what does this do?
    return calendar.timegm(datetime.strptime(d.split('.')[0],
                                    '%Y-%m-%d %H:%M:%S').timetuple())
