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

from __future__ import absolute_import, print_function

import re

from commoncode.system import on_linux


def VERSION_PATTERNS_REGEX():
    return [re.compile(x) for x in [
    # Eclipse features
    'v\d+\.feature\_(\d+\.){1,3}\d+',
    # Common version patterns
    '(M?(v\d+(\-|\_))?\d+\.){1,3}\d+[A-Za-z0-9]*((\.|\-|_|~)'
        '(b|B|rc|r|v|RC|alpha|beta|BETA|M|m|pre|vm|G)?\d+((\-|\.)\d+)?)?'
        '((\.|\-)(((alpha|dev|beta|rc|FINAL|final|pre)(\-|\_)\d+[A-Za-z]?'
        '(\-RELEASE)?)|alpha|dev(\.\d+\.\d+)?'
        '|beta|BETA|final|FINAL|release|fixed|(cr\d(\_\d*)?)))?',
    #
    '[A-Za-z]?(\d+\_){1,3}\d+\_?[A-Za-z]{0,2}\d+',
    #
    '(b|rc|r|v|RC|alpha|beta|BETA|M|m|pre|revision-)\d+(\-\d+)?',
    #
    'current|previous|latest|alpha|beta',
    #
    '\d{4}-\d{2}-\d{2}',
    #
    '(\d(\-|\_)){1,2}\d',
    #
    '\d{5,14}',
]]


POSIX_PATH_SEP = b'/' if on_linux else '/'
EMPTY_STRING = b' ' if on_linux else ' '
VERSION_PREFIX = b'v' if on_linux else 'v'


def hint(path):
    """
    Return a version found in a path or None. Prefix the version with 'v ' if
    the version does not start with v.
    """
    for pattern in VERSION_PATTERNS_REGEX():
        segments = path.split(POSIX_PATH_SEP)
        # skip the first path segment unless there's only one segment
        first_segment = 1 if len(segments) > 1 else 0
        interesting_segments = segments[first_segment:]
        # we iterate backwards from the end of the paths segments list
        for segment in interesting_segments[::-1]:
            version = re.search(pattern, segment)
            if version:
                v = version.group(0)
                if not v.lower().startswith(VERSION_PREFIX):
                    v = VERSION_PREFIX + EMPTY_STRING + v
                return v
