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

from __future__ import print_function, absolute_import

import logging
import os
import posixpath
import re
import shutil
import sys

from commoncode import fileutils
from commoncode.text import toascii


logger = logging.getLogger(__name__)
DEBUG = False
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


root_dir = os.path.join(os.path.dirname(__file__), 'bin')

# Suffix added to extracted target_dir paths
EXTRACT_SUFFIX = r'-extract'


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
    return path and path.rstrip('\\/').endswith(EXTRACT_SUFFIX)


def is_extracted(location):
    """
    Return True is the location is already extracted to the corresponding
    extraction location.
    """
    return location and os.path.exists(get_extraction_path(location))


def get_extraction_path(path):
    """
    Return a path where to extract.
    """
    return path.rstrip('\\/') + EXTRACT_SUFFIX


def remove_archive_suffix(path):
    """
    Remove all the extracted suffix from a path.
    """
    return re.sub(EXTRACT_SUFFIX, '', path)


def remove_backslashes(directory):
    """
    Walk a directory and rename the files if their names contain backslashes.
    Return a list of errors if any.
    """
    errors = []
    for top, _, files in os.walk(str(directory)):
        for filename in files:
            if '\\' in filename or '..' in filename:

                try:
                    new_path = fileutils.as_posixpath(filename)
                    new_path = new_path.strip('/')
                    new_path = posixpath.normpath(new_path)
                    new_path = new_path.replace('..', '/')
                    new_path = new_path.strip('/')
                    new_path = posixpath.normpath(new_path)
                    segments = new_path.split('/')
                    directory = os.path.join(top, *segments[:-1])
                    fileutils.create_dir(directory)
                    shutil.move(os.path.join(top, filename), os.path.join(top, *segments))
                except Exception:
                    errors.append(os.path.join(top, filename))
    return errors


def extracted_files(location):
    """
    Yield the locations of extracted files in a directory location.
    """
    assert location
    logger.debug('extracted_files for: %(location)r' % locals())
    return fileutils.file_iter(location)


def new_name(location, is_dir=False):
    """
    Return a new non-existing location usable to write a file or create
    directory without overwriting existing files or directories in the same
    parent directory, ignoring the case of the name.
    The case of the name is ignored to ensure that similar results are returned
    across case sensitive (*nix) and case insensitive file systems.
    Some characters illegal for us in file names on some OS are replaced with _
    such as a colon ":" on Windows.

    To find a new unique name:
     * pad a directory name with _X where X is an incremented number.
     * pad a file base name with _X where X is an incremented number and keep
       the extension unchanged.
    """
    assert location

    location = location.rstrip('\\/')
    name = fileutils.file_name(location).strip()
    if (not name or name == '.'
        # windows bare drive path as in c: or z:
        or (name and len(name) == 2 and name.endswith(':'))):
        name = 'file'

    parent = fileutils.parent_directory(location)
    # all existing files or directory as lower case
    siblings_lower = set(s.lower() for s in os.listdir(parent))

    portable_name = name.replace(':', '')

    if portable_name.lower() not in siblings_lower:
        return posixpath.join(parent, portable_name)

    ext = fileutils.file_extension(portable_name)
    base_name = fileutils.file_base_name(portable_name)
    if is_dir:
        # directories have no extension
        ext = ''
        base_name = portable_name

    counter = 1
    while 1:
        new_name = base_name + '_' + str(counter) + ext
        if new_name.lower() not in siblings_lower:
            break
        counter += 1
    return os.path.join(parent, new_name)


def portable_new_name(filename):
    """
    Return a new name for `filename` that is portable across operating systems.
    """
    # https://github.com/pallets/werkzeug/blob/master/werkzeug/utils.py#L253
    # https://raw.githubusercontent.com/pallets/werkzeug/8c2d63ce247ba1345e1b9332a68ceff93b2c07ab/werkzeug/utils.py

    # See also https://github.com/dbr/tvnamer/blob/master/tvnamer/utils.py

    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')

    # https://raw.githubusercontent.com/pallets/werkzeug/8c2d63ce247ba1345e1b9332a68ceff93b2c07ab/werkzeug/_compat.py
    PY2 = sys.version_info[0] == 2
    if PY2:
        text_type = unicode
    else:
        text_type = str    

    def secure_filename(filename):
        r"""Pass it a filename and it will return a secure version of it.  This
        filename can then safely be stored on a regular file system and passed
        to :func:`os.path.join`.  The filename returned is an ASCII only string
        for maximum portability.

        On windows systems the function also makes sure that the file is not
        named after one of the special device files.

        >>> secure_filename("My cool movie.mov")
        'My_cool_movie.mov'
        >>> secure_filename("../../../etc/passwd")
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'

        The function might return an empty filename.  It's your responsibility
        to ensure that the filename is unique and that you generate random
        filename if the function returned an empty one.

        .. versionadded:: 0.5

        :param filename: the filename to secure
        """
        toascii
        if isinstance(filename, unicode):
            from unicodedata import normalize
            filename = normalize('NFKD', filename).encode('ascii', 'ignore')
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, ' ')
        re.sub
        filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                       filename.split()))).strip('._')

        # on nt a couple of special files are present in each folder.  We
        # have to ensure that the target file is not such a filename.  In
        # this case we prepend an underline
        if os.name == 'nt' and filename and \
           filename.split('.')[0].upper() in _windows_device_files:
            filename = '_' + filename

        return filename




def is_portable_file_name(name):
    """
    Return True if `name` is a legal and portable file name on all supported OSes,
    e.g. on Linux/POSIX, Windows and MacOSX.

    See for more details:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    http://stackoverflow.com/questions/122400/what-are-reserved-filenames-for-various-platforms
    http://www.boost.org/doc/libs/1_36_0/libs/filesystem/doc/portability_guide.htm
    """

    windows_reserved_chars1 = '<>:"/\\|?*'
    # null to 31.
    windows_reserved_chars2 = ''.join(map(chr, range(32)))
    # these are illegal both upper and lowercase and with or without an extension
    windows_reserved_base_names1 = [n.lower() for n in (
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    )]
    windows_reserved_base_names2 = [re.compile('^' + n + '\..*$').match for n in windows_reserved_base_names1]

    # not trailing dot in a windows name
    windows_illegal_trailing_chars = ('.',)

    illegal_char = windows_reserved_chars1 + windows_reserved_chars2

    namel = name.lower()
    if (any(c in name for c in illegal_char)
     or any(namel == rn for rn in windows_reserved_base_names1)
     or any(ill(namel) for ill in windows_reserved_base_names2)
     or name.endswith(windows_illegal_trailing_chars)):
        return False
    return True


# http://www.opengroup.org/onlinepubs/007904975/basedefs/xbd_chap03.html
is_portable_posix = re.compile('^[0-9a-zA-Z\._\-]*$').match



class Entry(object):
    """
    An archive entry presenting the common data that exists in all entries
    handled by the various underlying extraction libraries.
    This class interface is similar to the TypeCode Type class.
    """
    # the actual posix as in the archive (relative, absolute, etc)
    path = None
    # path to use for links, typically a normalized target
    actual_path = None
    # where we will really extract, relative to the archive root
    extraction_path = None
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

    def asdict(self):
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
