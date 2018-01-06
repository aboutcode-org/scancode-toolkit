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
from __future__ import unicode_literals

from collections import OrderedDict
import os
import traceback

import attr

from commoncode.filetype import is_dir
from commoncode.filetype import is_file
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import path_to_bytes
from commoncode.fileutils import path_to_unicode
from commoncode.system import on_linux

from scancode.cache import get_cache_dir
from scancode.utils import get_relative_path

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str
    str = unicode
except NameError:
    # Python 3
    unicode = str


"""
An abstraction for files and directories used throughout ScanCode. ScanCode
deals with a lot of these as they are the basic unit of processing. They are
eventually cached or stored and this module hides all the details of iterating
files, path handling, caching or storing the file and directoy medatata.
"""


@attr.attributes(slots=True)
class Resource(object):
    """
    A resource represent a file or directory with essential "file
    information" and the scanned data details.
    """
    # LEGACY: TODO: remove
    scans_cache_class = attr.attrib(default=None)
    is_cached = attr.attrib(default=False, type=bool)
    abs_path = attr.attrib(default=None)
    base_is_dir = attr.attrib(default=True, type=bool)
    len_base_path = attr.attrib(default=0, type=int)
    rel_path = attr.attrib(default=None)
    # END LEGACY

    name = attr.attrib(default=None)
    parent = attr.attrib(default=None)
    children = attr.attrib(default=attr.Factory(list))

    has_infos = attr.attrib(default=False)
    infos = attr.attrib(default=attr.Factory(OrderedDict))
    scans = attr.attrib(default=attr.Factory(OrderedDict))

    def __attrs_post_init__(self):
        self.scans_cache_class = self.scans_cache_class()
        posix_path = as_posixpath(self.abs_path)
        # keep the path as relative to the original base_path, always Unicode
        self.rel_path = get_relative_path(posix_path, self.len_base_path, self.base_is_dir)
        self.infos['path'] = self.rel_path

    def get_infos(self):
        if not self.has_infos:
            self.infos.update(scan_infos(self.abs_path))
            self.has_infos = True
        return self.infos

    def walk(self, topdown=True):
        """
        Walk this Resource in a manner similar to os.walk
        """
        if topdown:
            yield self, self.children
        for child in self.children:
            for sc in child.walk(topdown):
                yield sc
        if not topdown:
            yield self, self.children


def scan_infos(location):
    """
    Scan one file or directory and return file_infos data. This always
    contains an extra 'errors' key with a list of error messages,
    possibly empty. If `diag` is True, additional diagnostic messages
    are included.
    """
    # FIXME: WE SHOULD PROCESS THIS IS MEMORY AND AS PART OF THE SCAN PROPER... and BOTTOM UP!!!!
    # THE PROCESSING TIME OF SIZE AGGREGATION ON DIRECTORY IS WAY WAY TOO HIGH!!!
    errors = []
    try:
        infos = get_file_infos(location)
    except Exception as e:
        # never fail but instead add an error message.
        infos = _empty_file_infos()
        errors = ['ERROR: infos: ' + e.message]
        errors.append('ERROR: infos: ' + traceback.format_exc())
    # put errors last
    infos['scan_errors'] = errors
    return infos


def get_file_infos(location):
    """
    Return a mapping of file information collected from the file or
    directory at `location`.
    """
    from commoncode import fileutils
    from commoncode import filetype
    from commoncode.hash import multi_checksums
    from typecode import contenttype

    if on_linux:
        location = path_to_bytes(location)
    else:
        location = path_to_unicode(location)

    infos = OrderedDict()
    is_file = filetype.is_file(location)
    is_dir = filetype.is_dir(location)

    T = contenttype.get_type(location)

    infos['type'] = filetype.get_type(location, short=False)
    name = fileutils.file_name(location)
    if is_file:
        base_name, extension = fileutils.splitext(location)
    else:
        base_name = name
        extension = ''

    if on_linux:
        infos['name'] = path_to_unicode(name)
        infos['base_name'] = path_to_unicode(base_name)
        infos['extension'] = path_to_unicode(extension)
    else:
        infos['name'] = name
        infos['base_name'] = base_name
        infos['extension'] = extension

    infos['date'] = is_file and filetype.get_last_modified_date(location) or None
    infos['size'] = T.size
    infos.update(multi_checksums(location, ('sha1', 'md5',)))
    infos['files_count'] = is_dir and filetype.get_file_count(location) or None
    infos['mime_type'] = is_file and T.mimetype_file or None
    infos['file_type'] = is_file and T.filetype_file or None
    infos['programming_language'] = is_file and T.programming_language or None
    infos['is_binary'] = bool(is_file and T.is_binary)
    infos['is_text'] = bool(is_file and T.is_text)
    infos['is_archive'] = bool(is_file and T.is_archive)
    infos['is_media'] = bool(is_file and T.is_media)
    infos['is_source'] = bool(is_file and T.is_source)
    infos['is_script'] = bool(is_file and T.is_script)

    return infos


# FIXME: this smells bad
def _empty_file_infos():
    """
    Return an empty mapping of file info, used in case of failure.
    """
    infos = OrderedDict()
    infos['type'] = None
    infos['name'] = None
    infos['extension'] = None
    infos['date'] = None
    infos['size'] = None
    infos['sha1'] = None
    infos['md5'] = None
    infos['files_count'] = None
    infos['mime_type'] = None
    infos['file_type'] = None
    infos['programming_language'] = None
    infos['is_binary'] = False
    infos['is_text'] = False
    infos['is_archive'] = False
    infos['is_media'] = False
    infos['is_source'] = False
    infos['is_script'] = False
    return infos


class Codebase(object):
    """
    Represent a codebase being scanned. A Codebase is a tree of Resources.
    """
    def __init__(self, root_location):
        """
        Initialize a new codebase rooted as the `root_location` existing
        file or directory.
        NOTE: no check is made on the location and it must be an existing location.
        """

        self.location = root_location
        # FIXME: encoding???
        self.location_native = path_to_bytes(root_location)
        self.is_file = is_file(self.location_native)
        self.is_dir = is_dir(self.location_native)
        self.cache_dir = get_cache_dir()
        self.root = None

    def collect(self):
        """
        Return a root Resource for this codebase by walking its root_location.
        """
        location = self.location
        if on_linux:
            location = self.location_native

        def on_error(error):
            raise error

        root_dir = Resource()
        for top, dirs, files in os.walk(
            location, topdown=True, onerror=on_error, followlinks=False):
            for dr in dirs:
                pass
