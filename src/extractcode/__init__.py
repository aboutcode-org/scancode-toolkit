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

import logging
import os
import posixpath
import re
import shutil
import sys

from commoncode.fileutils import as_posixpath
from commoncode.fileutils import create_dir
from commoncode.fileutils import file_name
from commoncode.fileutils import fsencode
from commoncode.fileutils import parent_directory
from commoncode.text import toascii
from commoncode.system import on_linux
from os.path import dirname
from os.path import join
from os.path import exists

logger = logging.getLogger(__name__)
DEBUG = False
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

root_dir = join(dirname(__file__), 'bin')

POSIX_PATH_SEP = b'/' if on_linux else '/'
WIN_PATH_SEP = b'\\' if on_linux else '\\'
PATHS_SEPS = POSIX_PATH_SEP + WIN_PATH_SEP
EMPTY_STRING = b'' if on_linux else ''
DOT = b'.' if on_linux else '.'
DOTDOT = DOT + DOT
UNDERSCORE = b'_' if on_linux else '_'

# Suffix added to extracted target_dir paths
EXTRACT_SUFFIX = b'-extract' if on_linux else r'-extract'

# high level archive "kinds"
docs = 1
regular = 2
regular_nested = 3
package = 4
file_system = 5
patches = 6
special_package = 7

kind_labels = {
    1: 'docs',
    2: 'regular',
    3: 'regular',
    4: 'package',
    5: 'file_system',
    6: 'patches',
    7: 'special_package',
}

# note: do not include special_package in all by default
all_kinds = (regular, regular_nested, package, file_system, docs, patches, special_package)
default_kinds = (regular, regular_nested, package)

# map user-visible extract types to tuples of "kinds"
extract_types = {
    'default': (regular, regular_nested, package,),
    'all': all_kinds,
    'package': (package,),
    'filesystem': (file_system,),
    'doc': (docs,),
    'patch': (patches,),
    'special_package': (special_package,),
}


def is_extraction_path(path):
    """
    Return True is the path points to an extraction path.
    """
    if on_linux:
        path = fsencode(path)

    return path and path.rstrip(PATHS_SEPS).endswith(EXTRACT_SUFFIX)


def is_extracted(location):
    """
    Return True is the location is already extracted to the corresponding
    extraction location.
    """
    if on_linux:
        location = fsencode(location)
    return location and exists(get_extraction_path(location))


def get_extraction_path(path):
    """
    Return a path where to extract.
    """
    if on_linux:
        path = fsencode(path)
    return path.rstrip(PATHS_SEPS) + EXTRACT_SUFFIX


def remove_archive_suffix(path):
    """
    Remove all the extracted suffix from a path.
    """
    if on_linux:
        path = fsencode(path)
    return re.sub(EXTRACT_SUFFIX, EMPTY_STRING, path)


def remove_backslashes_and_dotdots(directory):
    """
    Walk a directory and rename the files if their names contain backslashes.
    Return a list of errors if any.
    """
    if on_linux:
        directory = fsencode(directory)
    errors = []
    for top, _, files in os.walk(directory):
        for filename in files:
            if not (WIN_PATH_SEP in filename or DOTDOT in filename):
                continue
            try:
                new_path = as_posixpath(filename)
                new_path = new_path.strip(POSIX_PATH_SEP)
                new_path = posixpath.normpath(new_path)
                new_path = new_path.replace(DOTDOT, POSIX_PATH_SEP)
                new_path = new_path.strip(POSIX_PATH_SEP)
                new_path = posixpath.normpath(new_path)
                segments = new_path.split(POSIX_PATH_SEP)
                directory = join(top, *segments[:-1])
                create_dir(directory)
                shutil.move(join(top, filename), join(top, *segments))
            except Exception:
                errors.append(join(top, filename))
    return errors


def new_name(location, is_dir=False):
    """
    Return a new non-existing location from a `location` usable to write a file
    or create directory without overwriting existing files or directories in the same
    parent directory, ignoring the case of the filename.

    The case of the filename is ignored to ensure that similar results are returned
    across case sensitive (*nix) and case insensitive file systems.

    To find a new unique filename, this tries new names this way:
     * pad a directory name with _X where X is an incremented number.
     * pad a file base name with _X where X is an incremented number and keep
       the extension unchanged.
    """
    assert location
    if on_linux:
        location = fsencode(location)
    location = location.rstrip(PATHS_SEPS)
    assert location

    parent = parent_directory(location)

    # all existing files or directory as lower case
    siblings_lower = set(s.lower() for s in os.listdir(parent))

    filename = file_name(location)

    # corner case
    if filename in (DOT, DOT):
        filename = UNDERSCORE

    # if unique, return this
    if filename.lower() not in siblings_lower:
        return join(parent, filename)

    # otherwise seek a unique name
    if is_dir:
        # directories do not have an "extension"
        base_name = filename
        ext = EMPTY_STRING
    else:
        base_name, dot, ext = filename.partition(DOT)
        if dot:
            ext = dot + ext
        else:
            base_name = filename
            ext = EMPTY_STRING

    # find a unique filename, adding a counter int to the base_name
    counter = 1
    while 1:
        filename = base_name + UNDERSCORE + str(counter) + ext
        if filename.lower() not in siblings_lower:
            break
        counter += 1
    return join(parent, filename)


# TODO: use attrs and slots
class Entry(object):
    """
    An archive entry presenting the common data that exists in all entries
    handled by the various underlying extraction libraries.
    This class interface is similar to the TypeCode Type class.
    """
    # the actual posix as in the archive (relative, absolute, etc)
    path = None

    # path to use for links, typically a normalized target
    # FIXME: not used
    actual_path = None

    # where we will really extract, relative to the archive root
    # FIXME: not used
    extraction_path = None

    # in bytes
    size = 0
    date = None
    is_file = True
    is_dir = False
    is_special = False
    is_hardlink = False
    is_symlink = False
    is_broken_link = False
    link_target = None
    should_extract = False

    def fix_path(self):
        """
        Fix paths that are absolute, relative, backslashes and other
        shenanigans. Update the extraction path.
        """
        # TODO: Implement ME

    def __repr__(self):
        msg = (
            '%(__name__)s(path=%(path)r, size=%(size)r, '
            'is_file=%(is_file)r, is_dir=%(is_dir)r, '
            'is_hardlink=%(is_hardlink)r, is_symlink=%(is_symlink)r, '
            'link_target=%(link_target)r, is_broken_link=%(is_broken_link)r, '
            'is_special=%(is_special)r)'
        )
        d = dict(self.__class__.__dict__)
        d.update(self.__dict__)
        d['__name__'] = self.__class__.__name__
        return msg % d

    def to_dict(self):
        return {
            'path':self.path,
            'size': self.size,
            'is_file': self.is_file,
            'is_dir': self.is_dir,
            'is_hardlink': self.is_hardlink,
            'is_symlink': self.is_symlink,
            'link_target': self.link_target,
            'is_broken_link': self.is_broken_link,
            'is_special': self.is_special
        }


class ExtractError(Exception):
    pass


class ExtractErrorPasswordProtected(ExtractError):
    pass


class ExtractErrorFailedToExtract(ExtractError):
    pass


class ExtractWarningIncorrectEntry(ExtractError):
    pass


class ExtractWarningTrailingGarbage(ExtractError):
    pass
