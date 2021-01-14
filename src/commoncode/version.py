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

import re


def VERSION_PATTERNS_REGEX():
    return [re.compile(x) for x in [
        # Eclipse features
        r'v\d+\.feature\_(\d+\.){1,3}\d+',

        # Common version patterns
        r'(M?(v\d+(\-|\_))?\d+\.){1,3}\d+[A-Za-z0-9]*((\.|\-|_|~)'
            r'(b|B|rc|r|v|RC|alpha|beta|BETA|M|m|pre|vm|G)?\d+((\-|\.)\d+)?)?'
            r'((\.|\-)(((alpha|dev|beta|rc|FINAL|final|pre)(\-|\_)\d+[A-Za-z]?'
            r'(\-RELEASE)?)|alpha|dev(\.\d+\.\d+)?'
            r'|beta|BETA|final|FINAL|release|fixed|(cr\d(\_\d*)?)))?',
        #
        r'[A-Za-z]?(\d+\_){1,3}\d+\_?[A-Za-z]{0,2}\d+',
        #
        r'(b|rc|r|v|RC|alpha|beta|BETA|M|m|pre|revision-)\d+(\-\d+)?',
        #
        r'current|previous|latest|alpha|beta',
        #
        r'\d{4}-\d{2}-\d{2}',
        #
        r'(\d(\-|\_)){1,2}\d',
        #
        r'\d{5,14}',
    ]]


def hint(path):
    """
    Return a version found in a path or None. Prefix the version with 'v ' if
    the version does not start with v.
    """
    for pattern in VERSION_PATTERNS_REGEX():
        segments = path.split('/')
        # skip the first path segment unless there's only one segment
        first_segment = 1 if len(segments) > 1 else 0
        interesting_segments = segments[first_segment:]
        # we iterate backwards from the end of the paths segments list
        for segment in interesting_segments[::-1]:
            version = re.search(pattern, segment)
            if version:
                v = version.group(0)
                # prefix with v space
                if not v.lower().startswith('v'):
                    v = f'v {v}'
                return v
