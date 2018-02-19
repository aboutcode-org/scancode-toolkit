#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

from datetime import datetime
from datetime import tzinfo
from functools import update_wrapper
from functools import wraps
from time import time

"""
Time is of the essence: path safe time stamps creation and conversion to
datetime objects.
"""


class UTC(tzinfo):
    """UTC timezone"""

    def utcoffset(self, dt):  # NOQA
        return None

    def tzname(self, dt):  # NOQA
        return 'UTC'

    def dst(self, dt):  # NOQA
        return None


def time2tstamp(dt=None, path_safe=True):
    """
    Return a timestamp representing the datetime object (assumed to be in UTC
    time) or the current UTC time (if dt == None) formatted using the ISO 8601
    standard as a basis, extended to be path safe is path_safe is True.

    The Python isoformat returns a time stamp that complies with this standard
    but has limitations when used in a file or directory name. Here we
    transform the returned time stamp such that the result still complies with
    the ISO standard and can be safely used as part of a of file or directory
    name in a portable and OS safe fashion including on Windows where colons
    are not allowed in file names, or on posix where / denotes a path segment
    separator.

    For times, the ISO 8601 format specifies either a colon : (extended format)
    or nothing as a separator (basic format). Here Python defaults to using a
    colon. We therefore remove all the colons to be safe across filesystems. (a
    colon is not a valid path char on Windows)

    Another character may show up in the ISO representation such as / for time
    intervals. We could replace the forward slash with a double hyphen (--) as
    a separator instead (see Section 4.4.2 of the ISO standard). However since
    there are several places where hyphens are used, this makes it difficult to
    parse back. Instead we use an _ (underscore) to make the time stamp easier
    to convert back to a datetime object.
    """
    # TODO: check that the dt is effectively in UTC
    datim = dt or datetime.utcnow()
    iso = datim.isoformat()
    if path_safe:
        iso = iso.replace(':', '').replace('/', '_')
    return iso


def tstamp2time(stamp):
    """
    Convert a UTC timestamp to a datetime object.
    """
    # handle both basic and extended formats
    tformat = '%Y-%m-%dT%H%M%S' if stamp[4] == '-' else '%Y%m%dT%H%M%S'
    # normalize
    dt_ms = stamp.strip().replace('Z', '').replace(':', '')

    dt_ms = dt_ms.split('.')
    isodatim = dt_ms[0]
    datim = datetime.strptime(isodatim, tformat)
    # all stamps must be UTC
    datim = datim.replace(tzinfo=UTC())

    # deal with optional microsec
    try:
        microsec = dt_ms[1]
    except:
        microsec = None
    if microsec:
        microsec = int(microsec)
        if 0 <= microsec <= 999999:
            datim = datim.replace(microsecond=microsec)
    return datim


def timed(fun):
    """
    Decorate `fun` callable to return a tuple of (timing, result) where timing
    is a function execution time in seconds as a float and result is the value
    returned by calling `fun`.

    Note: this decorator will not work as expected for functions that return
    generators.
    """

    @wraps(fun)
    def _timed(*args, **kwargs):
        start = time()
        result = fun(*args, **kwargs)
        return time() - start, result

    return update_wrapper(_timed, fun)
