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


from os.path import commonprefix
import string
import posixpath

from commoncode import fileutils
from commoncode import text

"""
Various path utilities such as common prefix and suffix functions, conversion
to OS-safe paths and to POSIX paths.
"""


def resolve(path):
    """
    Resolve and return a path-like string `path` to a posix relative path
    string where extra slashes including leading and trailing slashes, dot
    '.' and dotdot '..' path segments have been removed or normalized or
    resolved with the provided path "tree". When a dotdot path segment cannot
    be further resolved by "escaping" the provided path tree, it is replaced
    by the string 'dotdot'.
    """
    slash, dot, dotdot = '/', '.', 'dotdot'
    if isinstance(path, unicode):
        slash, dot, dotdot = u'/', u'.', u'dotdot'

    if not path:
        return dot

    path = path.strip()
    if not path:
        return dot

    path = fileutils.as_posixpath(path)
    path = path.strip(slash)
    segments = [s.strip() for s in path.split(slash)]
    # remove empty (// or ///) or blank (space only) or single dot segments
    segments = [s for s in segments if s and s != '.']
    path = slash.join(segments)
    # resolves ..
    path = posixpath.normpath(path)
    # replace .. with literal dotdot
    segments = path.split(slash)
    segments = [dotdot if s == '..' else s for s in segments]
    path = slash.join(segments)
    return path


#
# Build OS-portable and safer paths
#

"""
To convert a path to a safe cross-os path, we use a characters translation
table. This will replaces all non-safe characters by an underscore char.
"""
allchars = string.maketrans('', '')


# table of non safe characters: Exclude digit,letters and a select subset of
# supported punctuation, all the rest is junk. nb: we consider the backslash
# as path safe for now, but we convert these later to posix path
not_path_safe = string.translate(allchars,
                                 allchars,
                                 '0123456789'
                                 'abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#+-./_\\')

# create translation table to replace non-safe chars with underscore char
path_safe = string.maketrans(not_path_safe, '_' * len(not_path_safe))


def safe_path(path, lowered=True, resolved=True):
    """
    Convert a path-like string `path` to a posix path string safer to use as a
    file path on all OSes. The path is lowercased. Non-ASCII alphanumeric
    characters and spaces are replaced with an underscore.
    The path is optionally resolved and lowercased.
    """
    safe = path.strip()
    # TODO: replace COM/PRN/LPT windows special names
    # TODO: resolve 'UNC' windows paths
    # TODO: strip leading windows drives
    # remove any unsafe chars
    safe = safe.translate(path_safe)
    safe = text.toascii(safe)
    safe = fileutils.as_posixpath(safe)
    if lowered:
        safe = safe.lower()
    if resolved:
        safe = resolve(safe)
    return safe


#
# paths comparisons
#
def common_prefix(s1, s2):
    """
    Return the common leading subsequence of two sequences and its length.
    """
    if not s1 or not s2:
        return None, 0
    common = commonprefix((s1, s2,))
    if common:
        return common, len(common)
    else:
        return None, 0


def common_suffix(s1, s2):
    """
    Return the common trailing subsequence between two sequences and its length.
    """
    if not s1 or not s2:
        return None, 0
    # revert the seqs and get a common prefix
    common, lgth = common_prefix(s1[::-1], s2[::-1])
    # revert again
    common = common[::-1] if common else common
    return common, lgth


def common_path_prefix(p1, p2):
    """
    Return the common leading path between two posix paths and the number of
    matched path segments.
    """
    return _common_path(p1, p2, common_func=common_prefix)


def common_path_suffix(p1, p2):
    """
    Return the common trailing path between two posix paths and the number of
    matched path segments.
    """
    return _common_path(p1, p2, common_func=common_suffix)


def split(p):
    """
    Split a posix path in a sequence of segments, ignoring leading and
    trailing slash. Return an empty sequence for an empty path and the root /.
    """
    if not p:
        return []
    p = p.strip('/').split('/')
    return [] if p == [''] else p


def _common_path(p1, p2, common_func):
    """
    Common function to compute common leading or trailing paths.
    """
    common, lgth = common_func(split(p1), split(p2))
    common = '/'.join(common) if common else None
    return common, lgth
