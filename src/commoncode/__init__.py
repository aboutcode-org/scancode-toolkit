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


def set_re_max_cache(max_cache=1000000):
    """
    Set re and fnmatch _MAXCACHE to 1Million items to cache compiled regex
    aggressively. Their default is a maximum of 100 items and many utilities and
    libraries use a lot of regexes: therefore 100 is not enough to benefit from
    caching.
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
