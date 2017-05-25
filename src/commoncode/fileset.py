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

import fnmatch
import logging

import os
from commoncode import fileutils
from commoncode import paths

DEBUG = False
logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

"""
Match files and directories paths based on inclusion and exclusion glob-style
patterns.

For example, this can be used to skip files that match ignore patterns,
similar to a version control ignore files such as .gitignore.

The pattern syntax is the same as fnmatch(5) as implemented in Python.

Patterns are applied to a path this way:
 - Paths are converted to POSIX paths before matching.
 - Patterns are NOT case-sensitive.
 - Leading slashes are ignored.
 - If the pattern contains a /, then the whole path must be matched;
   otherwise, the pattern matches if any path segment matches.
 - When matched, a directory content is matched recursively.
   For instance, when using patterns for ignoring, a matched a directory will
   be ignore with its file and sub-directories at full depth.
 - The order of patterns does not matter.
 - Exclusion patterns are prefixed with an exclamation mark (band or !)
   meaning that matched paths by that pattern will be excluded. Exclusions
   have precedences of inclusions.
 - Patterns starting with # are comments and skipped. use [#] for a literal #.
 - to match paths relative to some root path, you must design your patterns
   and the path tested accordingly. This module does not handles this.

Patterns may include glob wildcards such as:
 - ? : matches any single character.
 - * : matches 0 or more characters.
 - [seq] : matches any character in seq
 - [!seq] :matches any character not in seq
For a literal match, wrap the meta-characters in brackets. For example, '[?]'
matches the character '?'.
"""


def match(path, includes, excludes):
    """
    Return a tuple of two strings if `path` is matched or False if it does
    not. Matching is done based on the set of `includes` and `excludes`
    patterns maps. The returned tuple contains these two strings: pattern
    matched and associated message. The message explains why a path is
    included when matched. The message is always a string (possibly empty).

    `includes` and `excludes` are maps of (fnmtch pattern -> message).
    The order of the includes and excludes items does not matter. If one is
    empty, it is not used for matching. If the `path` is empty, return False.
    """

    includes = includes or {}
    excludes = excludes or {}
    if not path or not path.strip():
        return False

    included = _match(path, includes)
    excluded = _match(path, excludes)
    if DEBUG:
        logger.debug('in_fileset: path: %(path)r included:%(included)r, '
                     'excluded:%(excluded)r .' % locals())
    if excluded:
        return False
    elif included:
        return included
    else:
        return False


def _match(path, patterns):
    """
    Return a message if `path` is matched by a pattern from the `patterns` map
    or False.
    """
    if not path or not patterns:
        return False

    path = fileutils.as_posixpath(path).lower()
    pathstripped = path.lstrip('/')
    if not pathstripped:
        return False
    segments = paths.split(pathstripped)
    if DEBUG:
        logger.debug('_match: path: %(path)r patterns:%(patterns)r.' % locals())
    mtch = False
    for pat, msg in patterns.items():
        if not pat and not pat.strip():
            continue
        msg = msg or ''
        pat = pat.lstrip('/').lower()
        is_plain = '/' not in pat
        if is_plain:
            if any(fnmatch.fnmatchcase(s, pat) for s in segments):
                mtch = msg
                break
        elif (fnmatch.fnmatchcase(path, pat)
              or fnmatch.fnmatchcase(pathstripped, pat)):
            mtch = msg
            break
    if DEBUG:
        logger.debug('_match: match is %(mtch)r' % locals())
    return mtch


def load(location):
    """
    Return a sequence of patterns from a file at location.
    """
    if not location:
        return tuple()
    fn = os.path.abspath(os.path.normpath(os.path.expanduser(location)))
    msg = ('File %(location)s does not exist or not a file.') % locals()
    assert (os.path.exists(fn) and os.path.isfile(fn)), msg
    with open(fn, 'rb') as f:
        return [l.strip() for l in f if l and l.strip()]


def includes_excludes(patterns, message):
    """
    Return a dict of included patterns and a dict of excluded patterns from a
    sequence of `patterns` strings and a `message` setting the message as
    value in the returned mappings. Ignore pattern as comments if prefixed
    with #. Use an empty string is message is None.
    """
    message = message or ''
    BANG = '!'
    DASH = '#'
    included = {}
    excluded = {}
    if not patterns:
        return included, excluded
    for pat in patterns:
        pat = pat.strip()
        if not pat or pat.startswith(DASH):
            continue
        if pat.startswith(BANG):
            cpat = pat.lstrip(BANG)
            if cpat:
                excluded[cpat] = message
            continue
        else:
            included.add[pat] = message
    return included, excluded
