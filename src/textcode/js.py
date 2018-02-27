# -*- coding: utf-8 -*-
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
from __future__ import division

from collections import Counter
import logging
import os


from typecode import get_type

"""
Extract text from minified JavaScript and JavaScript map files.
These need specific processing because they are often big, single line files.
The approach is to:
 - extract the sourceContent parts of map files and recreate actual sub files from these
 - beautify minified JavaScript files

"""

logger = logging.getLogger(__name__)

bin_dir = os.path.join(os.path.dirname(__file__), 'bin')

extensions = ('.min.js', '.js.map',)


def is_js_map(location):
    """
    Return True is the file at `location` is a JavaScript map file.
    Spe is at:
    https://docs.google.com/document/d/1U1RGAehQwRypUTovF1KRlpiOFze0b-_2gc6fAH0KY0k/edit
    The format is:
        {
            "version" : 3,
            "file": "out.js",
            "sourceRoot": "",
            "sources": ["foo.js", "bar.js"],
            "sourcesContent": [null, null],
            "names": ["src", "maps", "are", "fun"],
            "mappings": "A,AAAB;;ABCDE;"
        }
    We care only about the presence of these tags for detection: version, sources, sourcesContent.
    """


def is_minified_js(location):
    """
    Return True is the file at `location` is a minified JavaScript.
    """
    T = get_type(location)

    # do not care for small files
    if T.size < 64:
        return False

    if not T.is_text:
        return False

    if location.endswith(extensions):
        return True

    with open(location, 'rb') as f:
        start = f.read(1024)

    if start.startswith('<'):
        return True

    # count whitespaces
    no_spaces = ''.join(start.split())

    # count opening and closing tags_count
    counts = Counter(c for c in no_spaces if c in '<>')

    if not all(c in counts for c in '<>'):
        return False

    if not all(counts.values()):
        return False

    # ~ 5 percent of tag <> markers
    has_tags = sum(counts.values()) / len(no_spaces) > 0.05

    # check if we have some significant proportion of tag-like characters
    open_close = counts['>'] / counts['<']
    # ration of open to close should approach 1: accept a 20% drift
    balanced = abs(1 - open_close) < .2
    return has_tags and balanced

