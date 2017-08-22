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

import os
from collections import OrderedDict
from datetime import datetime

from commoncode.system import on_posix
from commoncode.functional import memoize


"""
Low level file type utilities, essentially a wrapper around os.path and stat.
"""

def is_link(location):
    """
    Return True if `location` is a symbolic link.
    """
    return location and os.path.islink(location)


def is_file(location):
    """
    Return True if `location` is a file.
    """
    return (location and os.path.isfile(location)
            and not is_link(location) and not is_broken_link(location))


def is_dir(location):
    """
    Return True if `location` is a directory.
    """
    return (location and os.path.isdir(location) and not is_file(location)
            and not is_link(location) and not is_broken_link(location))


def is_regular(location):
    """
    Return True if `location` is regular. A regular location is a file or a
    dir and not a special file or symlink.
    """
    return location and (is_file(location) or is_dir(location))


def is_special(location):
    """
    Return True if `location` is a special file . A special file is not a
    regular file, i.e. anything such as a broken link, block file, fifo,
    socket, character device or else.
    """
    return not is_regular(location)


def is_broken_link(location):
    """
    Return True if `location` is a broken link.
    """
    # always false on windows, until Python supports junctions/links
    if on_posix and is_link(location):
        target = get_link_target(location)
        target_loc = os.path.join(os.path.dirname(location), target)
        return target and not os.path.exists(target_loc)


def get_link_target(location):
    """
    Return the link target for `location` if this is a Link or an empty
    string.
    """
    target = ''
    # always false on windows, until Python supports junctions/links
    if on_posix and is_link(location):
        try:
            # return false on OSes not supporting links
            target = os.readlink(location)
        except UnicodeEncodeError:
            # location is unicode but readlink can fail in some cases
            pass
    return target


# Map of type checker function -> short type code
# The order of types check matters: link -> file -> directory -> special
TYPES = OrderedDict([
    (is_link, ('l', 'link',)),
    (is_file, ('f', 'file',)),
    (is_dir, ('d', 'directory',)),
    (is_special, ('s', 'special',))
])


def get_type(location, short=True):
    """
    Return the type of the `location` or None if it does not exist.
    Return the short form (single character) or long form if short=False
    """
    if location:
        for type_checker in TYPES:
            tc = type_checker(location)
            if tc:
                short_form, long_form = TYPES[type_checker]
                return short and short_form or long_form


def is_readable(location):
    """
    Return True if the file at location has readable permission set.
    Does not follow links.
    """
    if location:
        if is_dir(location):
            return os.access(location, os.R_OK | os.X_OK)
        else:
            return os.access(location, os.R_OK)


def is_writable(location):
    """
    Return True if the file at location has writeable permission set.
    Does not follow links.
    """
    if location:
        if is_dir(location):
            return os.access(location, os.R_OK | os.W_OK | os.X_OK)
        else:
            return os.access(location, os.R_OK | os.W_OK)


def is_executable(location):
    """
    Return True if the file at location has executable permission set.
    Does not follow links.
    """
    if location:
        if is_dir(location):
            return os.access(location, os.R_OK | os.W_OK | os.X_OK)
        else:
            return os.access(location, os.X_OK)


def is_rwx(location):
    """
    Return True if the file at location has read, write and executable
    permission set. Does not follow links.
    """
    return is_readable(location) and is_writable(location) and is_executable(location)


def get_last_modified_date(location):
    """
    Return the last modified date stamp of a file as YYYYMMDD format. The date
    of non-files (dir, links, special) is always an empty string.
    """
    yyyymmdd = ''
    if is_file(location):
        utc_date = datetime.isoformat(
            datetime.utcfromtimestamp(os.path.getmtime(location))
        )
        yyyymmdd = utc_date[:10]
    return yyyymmdd


counting_functions = {
    'file_count': lambda _: 1,
    'file_size': os.path.getsize,
}

@memoize
def counter(location, counting_function):
    """
    Return a count for a single file or a cumulative count for a directory
    tree at `location`.

    Get a callable from the counting_functions registry using the
    `counting_function` string. Call this callable with a `location` argument
    to determine the count value for a single file. This allow memoization
    with hashable arguments.

    Only regular files and directories have a count. The count for a directory
    is the recursive count sum of the directory file and directory
    descendants.

    Any other file type such as a special file or link has a zero size. Does
    not follow links.
    """
    if not (is_file(location) or is_dir(location)):
        return 0

    count = 0
    if is_file(location):
        count_fun = counting_functions[counting_function]
        return count_fun(location)
    elif is_dir(location):
        count += sum(counter(os.path.join(location, p), counting_function)
                     for p in os.listdir(location))
    return count


def get_file_count(location):
    """
    Return the cumulative number of files in the directory tree at `location`
    or 1 if `location` is a file. Only regular files are counted. Everything
    else has a zero size.
    """
    return counter(location, 'file_count')


def get_size(location):
    """
    Return the size in bytes of a file at `location` or if `location` is a
    directory, the cumulative size of all files in this directory tree. Only
    regular files have a size. Everything else has a zero size.
    """
    return counter(location, 'file_size')
