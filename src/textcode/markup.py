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
import re

from typecode import get_type

"""
Extract text from HTML, XML and related angular markup-like files.
"""

logger = logging.getLogger(__name__)

bin_dir = os.path.join(os.path.dirname(__file__), 'bin')

extensions = ('.html', '.htm', '.php', '.phps', '.jsp', '.jspx' , '.xml', '.pom',)


def is_markup(location):
    """
    Return True is the file at `location` is some kind of markup, such as HTML,
    XML, PHP, etc.
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
    # ratio of open to close tags should approach 1: accept a 20% drift
    balanced = abs(1 - open_close) < .2
    return has_tags and balanced


def demarkup(location):
    """
    Return an iterator of unicode text lines for the file at `location` lightly
    stripping markup if the file is some kind of markup, such as HTML, XML, PHP,
    etc. The whitespaces are collapsed to one space.
    """
    from textcode.analysis import unicode_text_lines

    for line in unicode_text_lines(location):
        yield demarkup_text(line)


def demarkup_text(text):
    """
    Return text lightly stripped from markup. The whitespaces are collapsed to
    one space.
    """

    # keep the opening tag name of certain tags that contains these strings
    # note: <s> are from debian copyright files
    kept_tags = ('lic', 'copy', 'www', 'http', 'auth', 'contr', 'leg', 'inc', '@', '<s>', '</s>')

    # find start and closing tags or the first white space whichever comes first
    # or entities
    # this regex is such that ' '.join(tags.split(a))==a

    tags_ents = re.compile(r'(</?[^\s></]+(?:>|\s)?|&[^\s&]+;|href|[\'"]?\/\>)', re.IGNORECASE).split

    cleaned = []
    for token in tags_ents(text):
        if token.lower().startswith(('<', '&', 'href')) and not any(k in token.lower() for k in kept_tags):
            continue
        else:
            cleaned.append(token)
    return u' '.join(cleaned)
