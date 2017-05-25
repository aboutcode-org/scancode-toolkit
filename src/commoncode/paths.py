#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

import ntpath
from os.path import commonprefix
import posixpath
import re

from commoncode.text import as_unicode
from commoncode.text import toascii
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import as_winpath
from commoncode.fileutils import is_posixpath


"""
Various path utilities such as common prefix and suffix functions, conversion
to OS-safe paths and to POSIX paths.
"""

#
# Build OS-portable and safer paths

def safe_path(path, posix=False):
    """
    Convert `path` to a safe and portable POSIX path usable on multiple OSes. The
    returned path is an ASCII-only byte string, resolved for relative segments and
    itself relative.

    The `path` is treated as a POSIX path if `posix` is True or as a Windows path
    with blackslash separators otherwise.
    """
    # if the path is UTF, try to use unicode instead
    if not isinstance(path, unicode):
        path = as_unicode(path)

    path = path.strip()

    if not is_posixpath(path):
        path = as_winpath(path)
        posix = False

    path = resolve(path, posix)

    _pathmod, path_sep = path_handlers(path, posix)

    segments = [s.strip() for s in path.split(path_sep) if s.strip()]
    segments = [portable_filename(s) for s in segments]

    # print('safe_path: orig:', orig_path, 'segments:', segments)

    if not segments:
        return '_'

    # always return posix
    sep = isinstance(path, unicode) and u'/' or '/'
    path = sep.join(segments)
    return as_posixpath(path)


def path_handlers(path, posix=True):
    """
    Return a path module and path separator to use for handling (e.g. split and join)
    `path` using either POSIX or Windows conventions depending on the `path` content.
    Force usage of POSIX conventions if `posix` is True.
    """
    # determine if we use posix or windows path handling
    is_posix = is_posixpath(path)
    use_posix = posix or is_posix
    pathmod = use_posix and posixpath or ntpath
    path_sep = use_posix and '/' or '\\'
    path_sep = isinstance(path, unicode) and unicode(path_sep) or path_sep
    return pathmod, path_sep


def resolve(path, posix=True):
    """
    Return a resolved relative POSIX path from `path` where extra slashes including
    leading and trailing slashes are removed, dot '.' and dotdot '..' path segments
    have been removed or resolved as possible. When a dotdot path segment cannot be
    further resolved and would be "escaping" from the provided path "tree", it is
    replaced by the string 'dotdot'.

    The `path` is treated as a POSIX path if `posix` is True (default) or as a
    Windows path with blackslash separators otherwise.
    """
    is_unicode = isinstance(path, unicode)
    dot = is_unicode and u'.' or '.'

    if not path:
        return dot

    path = path.strip()
    if not path:
        return dot

    if not is_posixpath(path):
        path = as_winpath(path)
        posix = False

    pathmod, path_sep = path_handlers(path, posix)

    path = path.strip(path_sep)
    segments = [s.strip() for s in path.split(path_sep) if s.strip()]

    # remove empty (// or ///) or blank (space only) or single dot segments
    segments = [s for s in segments if s and s != '.']

    path = path_sep.join(segments)

    # resolves . dot, .. dotdot
    path = pathmod.normpath(path)

    segments = path.split(path_sep)

    # remove empty or blank segments
    segments = [s.strip() for s in segments if s and s.strip()]

    # is this a windows absolute path? if yes strip the colon to make this relative
    if segments and len(segments[0]) == 2 and segments[0].endswith(':'):
        segments[0] = segments[0][:-1]

    # replace any remaining (usually leading) .. segment with a literal "dotdot"
    dotdot = is_unicode and u'dotdot' or 'dotdot'
    segments = [dotdot if s == '..' else s for s in segments if s]
    if segments:
        path = path_sep.join(segments)
    else:
        path = dot

    path = as_posixpath(path)

    return path


legal_punctuation = "!\#$%&\(\)\+,\-\.;\=@\[\]_\{\}\~"
legal_chars = 'A-Za-z0-9' + legal_punctuation
illegal_chars_re = '[^' + legal_chars + ']'
replace_illegal_chars = re.compile(illegal_chars_re).sub


def portable_filename(filename):
    """
    Return a new name for `filename` that is portable across operating systems.

    In particular the returned file name is guaranteed to be:
    - a portable name on most OSses using a limited ASCII characters set including
      some limited punctuation.
    - a valid name on Linux, Windows and Mac.

    Unicode file names are transliterated to plain ASCII.

    See for more details:
    - http://www.opengroup.org/onlinepubs/007904975/basedefs/xbd_chap03.html
    - https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    - http://www.boost.org/doc/libs/1_36_0/libs/filesystem/doc/portability_guide.htm

    Also inspired by Werkzeug:
    https://raw.githubusercontent.com/pallets/werkzeug/8c2d63ce247ba1345e1b9332a68ceff93b2c07ab/werkzeug/utils.py

    For example:
    >>> expected = 'A___file__with_Spaces.mov'
    >>> assert expected == portable_filename("A:\\ file/ with Spaces.mov")

    Unresolved relative paths will be trated as a single filename. Use
    resolve instead if you want to resolve paths:
    >>> expected = '___.._.._etc_passwd'
    >>> assert expected == portable_filename("../../../etc/passwd")

    Unicode name are transliterated:
    >>> expected = 'This_contain_UMLAUT_umlauts.txt'
    >>> assert expected == portable_filename(u'This contain UMLAUT \xfcml\xe4uts.txt')
    """
    filename = toascii(filename, translit=True)

    if not filename:
        return '_'

    filename = replace_illegal_chars('_', filename)

    # these are illegal both upper and lowercase and with or without an extension
    # we insert an underscore after the base name.
    windows_illegal_names = set([
        'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
        'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9',
        'aux', 'con', 'nul', 'prn'
    ])

    basename, dot, extension = filename.partition('.')
    if basename.lower() in windows_illegal_names:
        filename = ''.join([basename, '_', dot, extension])


    # no name made only of dots.
    if set(filename) == set(['.']):
        filename = 'dot' * len(filename)

    # replaced any leading dotdot
    if filename != '..' and filename.startswith('..'):
        while filename.startswith('..'):
            filename = filename.replace('..', '__', 1)

    return filename

#
# paths comparisons, common prefix and suffix extraction
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
    Split a posix path in a sequence of segments, ignoring leading and trailing
    slash. Return an empty sequence for an empty path and the root path /.
    """
    if not p:
        return []
    p = p.strip('/').split('/')
    return [] if p == [''] else p


def _common_path(p1, p2, common_func):
    """
    Return a common leading or trailing path brtween paths `p1` and `p2` and the
    common length in number of segments using the `common_func` path comparison
    function.
    """
    common, lgth = common_func(split(p1), split(p2))
    common = '/'.join(common) if common else None
    return common, lgth
