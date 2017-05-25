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

import calendar
from datetime import datetime
import os


def isoformat(utc_date):
    return datetime.isoformat(utc_date).replace('T', ' ')


def get_file_mtime(location, iso=True):
    """
    Return a string containing the last modified date of a file formatted
    as an ISO time stamp is ISO is True or a as raw number since epoch.
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
