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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


def set_re_max_cache(max_cache=1000000):
    """
    Set re and fnmatch _MAXCACHE to 1M to cache regex compiled aggressively
    their default is 100 and many utilities and libraries use a lot of regex
    """
    import re
    import fnmatch

    remax = getattr(re, '_MAXCACHE', 0)
    if remax < max_cache:
        setattr(re, '_MAXCACHE', max_cache)

    fnmatchmax = getattr(fnmatch, '_MAXCACHE', 0)
    if fnmatchmax < max_cache:
        setattr(fnmatch, '_MAXCACHE', max_cache)


set_re_max_cache()
