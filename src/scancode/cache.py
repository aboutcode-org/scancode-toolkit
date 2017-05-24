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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
from functools import partial
import json
from hashlib import sha1
import os
import posixpath
import sys

from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode import timeutils

from scancode import scans_cache_dir

"""
Cache scan results for a file or directory disk using a file-based cache.

The approach is to cache the scan of a file using these files:
 - one "global" file contains a log of all the paths scanned.
 - for each file being scanned, we store a file that contains the corresponding file
   info data as JSON. This file is named after the hash of the path of a scanned file.
 - for each unique file being scanned (e.g. based on its content SHA1), we store a
   another JSON file that contains the corresponding scan data. This file is named
   after the hash of the scanned file content.

Once a scan is completed, we iterate the cache to output the final scan results:
First iterate the global log file to get the paths, from there collect the cached
file info for that file and from the path and file info collect the cached scanned
result. This iterator is then streamed to the final JSON output.

Finally once a scan is completed the cache is destroyed to free up disk space.

Internally the cache is organized as a tree of directories named after the first few
characters or a path hash or file hash. This is to avoid having having too many files
per directory that can make some filesystems choke as well as having directories that
are too deep or having file paths that are too long which problematic on some OS.
"""

# Tracing flags
TRACE = False

def logger_debug(*args):
    pass

if TRACE:
    import logging

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


def get_scans_cache_class(cache_dir=scans_cache_dir):
    """
    Return a new persistent cache class configured with a unique storage directory.
    """
    # create a unique temp directory in cache_dir
    fileutils.create_dir(cache_dir)
    # ensure that the cache dir is alwasy unicode
    cache_dir = fileutils.get_temp_dir(unicode(cache_dir), prefix=unicode(timeutils.time2tstamp()) + u'-')
    sc = ScanFileCache(cache_dir)
    sc.setup()
    return partial(ScanFileCache, cache_dir)


def info_keys(path):
    """
    Return a file info cache keys tripple for a path.

    For example:
    >>> expected = 'fb87db2bb28e9501ac7fdc4812782118f4c94a0f'
    >>> assert expected == sha1('/w421/scancode-toolkit2').hexdigest()
    >>> expected = ('f', 'b', '87db2bb28e9501ac7fdc4812782118f4c94a0f')
    >>> assert expected == info_keys('/w421/scancode-toolkit2')
    """
    # ensure that we always pass bytes to the hash function
    if isinstance(path, unicode):
        pa = path.encode('utf-8')
    else:
        pa = path
    return keys_from_hash(sha1(pa).hexdigest())


def scan_keys(path, file_info):
    """
    Return a scan cache keys tripple for a path and file_info. If the file_info
    sha1 is empty (e.g. such as a directory), return a key based on the path instead.
    """
    # we "get" because in some off cases getting file info may have failed.
    sha1_digest = file_info.get('sha1')
    if sha1_digest:
        return keys_from_hash(sha1_digest)
    else:
        # we may eventually store directories, in which case we use the path as a key
        # with some extra seed
        return  info_keys('empty hash' + path)


def keys_from_hash(hexdigest):
    """
    Return a cache keys triple for a hash hexdigest string.

    NOTE: since we use the first character and next two characters as directories, we
    create at most 16 dir at the first level and 16 dir at the second level for each
    first level directory for a maximum total of 16*16 = 256 directories. For a
    million files we would have about 4000 files per directory on average with this
    scheme which should keep most file systems happy and avoid some performance
    issues when there are too many files in a single directory.

    For example:
    >>> expected = ('f', 'b', '87db2bb28e9501ac7fdc4812782118f4c94a0f')
    >>> assert expected == keys_from_hash('fb87db2bb28e9501ac7fdc4812782118f4c94a0f')
    """
    return hexdigest[0], hexdigest[1], hexdigest[2:]


def paths_from_keys(base_path, keys):
    """
    Return a tuple of (parent dir path, filename) built from a cache keys triple and
    a base_directory. Ensure that the parent directory exist.
    """
    dir1, dir2, fname = keys
    parent = os.path.join(base_path, dir1, dir2)
    fileutils.create_dir(parent)
    return parent, fname


class ScanFileCache(object):
    """
    A file-based cache for scan results saving results in files and using no locking.
    This is NOT thread-safe and NOT multi-process safe but works OK in our context:
    we cache the scan for a given file once and read it only a few times.
    """
    def __init__(self, cache_dir):
        self.cache_base_dir = cache_dir
        # subdirs for info and scans caches
        self.cache_infos_dir = as_posixpath(os.path.join(self.cache_base_dir, u'infos/'))
        self.cache_scans_dir = as_posixpath(os.path.join(self.cache_base_dir, u'scans/'))
        self.cache_files_log = as_posixpath(os.path.join(self.cache_base_dir, u'files_log'))

    def setup(self):
        """
        Setup the cache: must be called at least once globally after cache
        initialization.
        """
        os.makedirs(self.cache_infos_dir)
        os.makedirs(self.cache_scans_dir)

    @classmethod
    def log_file_path(cls, logfile_fd, path):
        """
        Log file path in the cache logfile_fd **opened** file descriptor.
        """
        # we dump one path per line.
        logfile_fd.write(path)
        logfile_fd.write('\n')

    def get_cached_info_path(self, path):
        """
        Return the path where to store a file info in the cache given a path.
        """
        keys = info_keys(path)
        paths = paths_from_keys(self.cache_infos_dir, keys)
        return posixpath.join(*paths)

    def put_info(self, path, file_info):
        """
        Put file_info for path in the cache and return True if the file referenced
        in file_info has already been scanned or False otherwise.
        """
        info_path = self.get_cached_info_path(path)
        with open(info_path, 'w') as cached_infos:
            json.dump(file_info, cached_infos, check_circular=False)
        scan_path = self.get_cached_scan_path(path, file_info)
        is_scan_cached = os.path.exists(scan_path)
        if TRACE:
            logger_debug('put_infos:', 'path:', path, 'is_scan_cached:', is_scan_cached, 'file_info:', file_info, '\n')
        return is_scan_cached

    def get_info(self, path):
        """
        Return file info from the cache for a path.
        Return None on failure to find the info in the cache.
        """
        info_path = self.get_cached_info_path(path)
        if os.path.exists(info_path):
            with codecs.open(info_path, 'r', encoding='utf-8') as ci:
                return json.load(ci, object_pairs_hook=OrderedDict)

    def get_cached_scan_path(self, path, file_info):
        """
        Return the path where to store a scan in the cache given a path and file_info.
        """
        keys = scan_keys(path, file_info)
        paths = paths_from_keys(self.cache_scans_dir, keys)
        return posixpath.join(*paths)

    def put_scan(self, path, file_info, scan_result):
        """
        Put scan_result in the cache if not already cached.
        """
        scan_path = self.get_cached_scan_path(path, file_info)
        if not os.path.exists(scan_path):
            with open(scan_path, 'w') as cached_scan:
                json.dump(scan_result, cached_scan, check_circular=False)
        if TRACE:
            logger_debug('put_scan:', 'scan_path:', scan_path, 'file_info:', file_info, 'scan_result:', scan_result, '\n')

    def get_scan(self, path, file_info):
        """
        Return scan results from the cache for a path and file_info.
        Return None on failure to find the scan results in the cache.
        """
        scan_path = self.get_cached_scan_path(path, file_info)
        if os.path.exists(scan_path):
            with codecs.open(scan_path, 'r', encoding='utf-8') as cs:
                return json.load(cs, object_pairs_hook=OrderedDict)

    def iterate(self, scan_names, root_dir=None, paths_subset=tuple()):
        """
        Yield scan data for all cached scans e.g. the whole cache given
        a list of scan names.
        If a `paths_subset` sequence of paths is provided, then only
        these paths are iterated.

        The logfile MUST have been closed before calling this method.
        """
        paths_subset = set(paths_subset)
        with codecs.open(self.cache_files_log, 'r', encoding='utf-8') as cached_files:
            # iterate the list of (path, (info keys)), one by line
            for file_log in cached_files:
                path = file_log.rstrip('\n')
                if paths_subset and path not in paths_subset:
                    continue
                file_info = self.get_info(path)

                if root_dir:
                    rooted_path = posixpath.join(root_dir, path)
                else:
                    rooted_path = path
                logger_debug('iterate:', 'rooted_path:', rooted_path)

                # rare but possible corner case
                if file_info is None:
                    no_info = ('ERROR: file info unavailable in cache: '
                               'This is either a bug or processing was aborted with CTRL-C.')
                    scan_result = OrderedDict(path=rooted_path)
                    scan_result['scan_errors'] = [no_info]
                    if TRACE:
                        logger_debug('iterate:', 'scan_result:', scan_result, 'for path:', rooted_path, '\n')
                    yield scan_result
                    continue

                path = file_info.pop('path')
                scan_result = OrderedDict(path=rooted_path)

                if 'infos' in scan_names:
                    # infos is always collected but only returned if requested
                    # we flatten these as direct attributes of a file object
                    scan_result.update(file_info.items())
                if not scan_result.get('scan_errors'):
                    scan_result['scan_errors'] = []

                # check if we have more than just infos
                if ['infos'] != scan_names:
                    errors = scan_result['scan_errors']
                    scan_details = self.get_scan(path, file_info)
                    if scan_details is None:
                        no_scan_details = (
                            'ERROR: scan details unavailable in cache: '
                            'This is either a bug or processing was aborted with CTRL-C.')
                        errors.append(no_scan_details)
                    else:
                        # append errors to other top level errors if any
                        scan_errors = scan_details.pop('scan_errors', [])
                        errors.extend(scan_errors)
                        scan_result.update(scan_details)

                if TRACE:
                    logger_debug('iterate:', 'scan_result:', scan_result, 'for path:', rooted_path, '\n')
                yield scan_result

    def clear(self, *args):
        """
        Purge the cache by deleting the corresponding cached data files.
        """
        fileutils.delete(self.cache_base_dir)
