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

import codecs
from collections import OrderedDict
from functools import partial
import json
from hashlib import sha1
import os
import posixpath
import sys

# from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import create_dir
from commoncode.fileutils import delete
from commoncode.fileutils import get_temp_dir
from commoncode.fileutils import path_to_bytes
from commoncode.fileutils import path_to_unicode
from commoncode.system import on_linux
from commoncode.timeutils import time2tstamp

from scancode import scans_cache_dir


"""
Cache scan results for a file or directory disk using a file-based cache.

The approach is to cache the scan of a file using these data structure and files:
 - a resources list contains all the Resource objects scanned.
 - for each file being scanned, we store a JSON file that contains the
   corresponding scan data. This file is named after the hash of its path.

Once a scan is completed, we iterate the cache to output the final scan results:
First iterate the resources and from the path collect the cached scanned result.
This iterator is then streamed to the final JSON output.

Finally once a scan is completed the cache is destroyed to free up disk space.

Internally the cache is organized as a tree of directories named after the first
few characters or a path hash. This is to avoid having having too many files per
directory that can make some filesystems choke as well as having directories
that are too deep or having file paths that are too long which problematic on
some OS.
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
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))


def get_cache_dir(base_cache_dir=scans_cache_dir):
    """
    Return a new, created and unique cache storage directory.
    """
    create_dir(base_cache_dir)
    # create a unique temp directory in cache_dir
    prefix = time2tstamp() + u'-'
    cache_dir = get_temp_dir(base_cache_dir, prefix=prefix)
    if on_linux:
        cache_dir = path_to_bytes(cache_dir)
    return cache_dir


def get_scans_cache_class(base_cache_dir=scans_cache_dir):
    """
    Return a new persistent cache class configured with a unique storage
    directory.
    """
    cache_dir = get_cache_dir(base_cache_dir=base_cache_dir)
    sc = ScanFileCache(cache_dir)
    sc.setup()
    return partial(ScanFileCache, cache_dir)


def scan_keys(path):
    """
    Return a cache "keys" tripple for a path composed of three
    paths segments derived from a checksum.

    For example:
    >>> expected = 'fb87db2bb28e9501ac7fdc4812782118f4c94a0f'
    >>> assert expected == sha1('/w421/scancode-toolkit2').hexdigest()
    >>> expected = ('0', 'c', 'a4f74d39ecbf551b1acfc63dc37bf2c8b9482c')
    >>> assert expected == scan_keys('/w421/scancode-toolkit2')

    NOTE: since we use the first character and next two characters as
    directories, we create at most 16 dir at the first level and 16 dir at the
    second level for each first level directory for a maximum total of 16*16 =
    256 directories. For a million files we would have about 4000 files per
    directory on average with this scheme which should keep most file systems
    happy and avoid some performance issues when there are too many files in a
    single directory.
    """
    # ensure that we always pass bytes to the hash function
    path = path_to_bytes(path)
    hexdigest = sha1(path + b'empty hash').hexdigest()
    if on_linux:
        hexdigest = bytes(hexdigest)
    else:
        hexdigest = unicode(hexdigest)
    return hexdigest[0], hexdigest[1], hexdigest[2:]


class ScanFileCache(object):
    """
    A file-based cache for scan results saving results in files and using no
    locking. This is NOT thread-safe and NOT multi-process safe but works OK in
    our context: we cache the scan for a given file once and read it only a few
    times.
    """
    def __init__(self, cache_dir):
        if on_linux:
            self.cache_base_dir = path_to_bytes(cache_dir)
        else:
            self.cache_base_dir = cache_dir
        self.cache_scans_dir = as_posixpath(self.cache_base_dir)

    def setup(self):
        """
        Setup the cache: must be called at least once globally after cache
        initialization.
        """
        create_dir(self.cache_scans_dir)

    def get_cached_scan_path(self, path):
        """
        Return the path where to store a scan in the cache given a path.
        """
        dir1, dir2, file_name = scan_keys(path)

        if on_linux:
            base_path = path_to_bytes(self.cache_scans_dir)
        else:
            base_path = path_to_unicode(self.cache_scans_dir)

        parent = os.path.join(base_path, dir1, dir2)
        create_dir(parent)

        return posixpath.join(parent, file_name)

    def put_scan(self, path, scan_result):
        """
        Put scan_result in the cache if not already cached.
        """
        scan_path = self.get_cached_scan_path(path)
        if not os.path.exists(scan_path):
            with codecs.open(scan_path, 'wb', encoding='utf-8') as cached_scan:
                json.dump(scan_result, cached_scan, check_circular=False)
        if TRACE:
            logger_debug(
                'put_scan:', 'scan_path:', scan_path, 'scan_result:', scan_result, '\n')

    def get_scan(self, path):
        """
        Return scan results from the cache for a path.
        Return None on failure to find the scan results in the cache.
        """
        scan_path = self.get_cached_scan_path(path)
        if os.path.exists(scan_path):
            with codecs.open(scan_path, 'r', encoding='utf-8') as cached_scan:
                return json.load(cached_scan, object_pairs_hook=OrderedDict)

    def iterate(self, resources, scan_names, root_dir=None, paths_subset=tuple()):
        """
        Yield scan data for all cached scans e.g. the whole cache given a list
        of `resources` Resource objects and `scan_names`.

        If a `paths_subset` sequence of paths is provided, then only these paths
        are iterated.
        """
        if on_linux:
            paths_subset = set(path_to_bytes(p) for p in paths_subset)
        else:
            paths_subset = set(path_to_unicode(p) for p in paths_subset)

        for resource in resources:
            resource_path = resource.rel_path
            if paths_subset and resource_path not in paths_subset:
                continue

            scan_result = OrderedDict()

            # always set the path to what was expected based on strip/full/root args
            rooted_path = get_scan_path(resource, root_dir)
            scan_result['path'] = rooted_path

            scan_details = self.get_scan(resource_path)

            if scan_details is None:
                no_scan_details = (
                    'ERROR: scan details unavailable in cache: '
                    'This is either a bug or processing was aborted with '
                    'CTRL-C.')
                scan_result['scan_errors'] = [no_scan_details]
                continue

            infos = scan_details.pop('infos', None)
            if 'infos' in scan_names and infos:
                # info are always collected but only returned if requested
                # we flatten these as direct attributes of a file object
                # FIXME: this should be done in the scan looo NOT HERE!!!
                scan_result.update(infos)

            scan_result.update(scan_details)

            if TRACE:
                logger_debug(
                    'iterate:', 'scan_result:', scan_result,
                    'for resource_path:', rooted_path, '\n')
            yield scan_result

    def clear(self, *args):
        """
        Purge the cache by deleting the corresponding cached data files.
        """
        delete(self.cache_base_dir)


def get_scan_path(resource, root_dir):
    """
    Return a path to use in the scan results
    """
    # FIXME: Resource should handle this paths thingies
    resource_path = resource.rel_path
    if on_linux:
        unicode_path = path_to_unicode(resource_path)
    else:
        unicode_path = resource_path

    if root_dir:
        # must be unicode
        if on_linux:
            root_dir = path_to_unicode(root_dir)
        rooted_path = posixpath.join(root_dir, unicode_path)
    else:
        rooted_path = unicode_path
    rooted_path = as_posixpath(rooted_path)
    logger_debug('get_scan_path:', 'rooted_path:', rooted_path)
    return rooted_path
