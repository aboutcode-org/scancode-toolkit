#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
from functools import partial
import os
import sys

from commoncode import fileutils
from commoncode import timeutils

from scancode import scans_cache_dir

"""
Caching scans on disk: A cache of all the scan results.

Each scan results for a file or directory is cached on disk.

The approach is to use to cache:
 - the results of a scan, excluding file infos keyed by the hash of a scanned file
 - the file infos, keyed by the path of a scanned file

Once a scan is completed, we iterate the caches to output the scan results using this
procedure: iterate the cached file infos and for each lookup the scan details in the
cached scan results. This iteration is driving the final streaming of results to the
output format (e.g. JSON).

Finally once a scan is completed the cache is destroyed to free up disk space.
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


class ScanCache(object):
    """
    A file-based cache for scan results.
    This is NOT thread-safe, but is multi-process safe.
    """
    def __init__(self, cache_dir):
        self.cache_base_dir = cache_dir
        # subdirs for infos and scans caches
        self.cache_infos_dir = os.path.join(self.cache_base_dir, 'infos')
        self.cache_scans_dir = os.path.join(self.cache_base_dir, 'scans')

        # workaround for https://github.com/grantjenks/python-diskcache/issues/32
        from diskcache import Disk
        class DiskWithNoHighPickleProtocol(Disk):
            "Subclass of diskcache.Disk that always use the lowest pickle protocol."
            def __init__(self, directory, size_threshold, pickle_protocol):
                super(DiskWithNoHighPickleProtocol, self).__init__(directory, size_threshold, pickle_protocol)
                self._protocol = 0

        # and finally cache instances
        from diskcache import Cache
        self.infos = Cache(self.cache_infos_dir, disk=DiskWithNoHighPickleProtocol)
        self.scans = Cache(self.cache_scans_dir, disk=DiskWithNoHighPickleProtocol)

    def scan_key(self, path, file_infos):
        """
        Return a scan cache key for a path and file_infos.
        """
        sha1 = file_infos['sha1']
        # we may eventually store directories, in which case we use the path as a key
        return sha1 or path

    def put_infos(self, path, file_infos):
        """
        Put file_infos for path in the cache and return True if the file referenced
        in file_infos has already been scanned or False otherwise.
        """
        self.infos.set(path, file_infos)
        is_scan_cached = self.scan_key(path, file_infos) in self.scans
        if TRACE:
            logger_debug('put_infos:', 'path:', path, 'is_scan_cached:', is_scan_cached, 'file_infos:', file_infos, '\n')
            logger_debug('put_infos:', 'cached_infos:', self.infos[path], '\n')
        return is_scan_cached

    def put_scan(self, path, file_infos, scan_result):
        """
        Put scan_result in the cache. Also put  file_infos in the cache if needed.
        """
        scan_key = self.scan_key(path, file_infos)
        self.scans.add(scan_key, scan_result)
        if TRACE:
            logger_debug('put_scan:', 'scan_key:', scan_key, 'file_infos:', file_infos, 'scan_result:', scan_result, '\n')
            logger_debug('put_scan:', 'cached_infos:', self.infos[path], '\n')
            logger_debug('put_scan:', 'scan_key:', scan_key, 'cached_scan:', self.scans[scan_key], '\n')

    def iterate(self, with_infos=True):
        """
        Yield scan data for all cached scans e.g. the whole cache.
        If a scan is missing for a given info, an error is appended to scan_errors.
        """
        for path in self.infos:
            file_infos = self.infos[path]
            scan_result = OrderedDict(path=path)
            if with_infos:
                # infos is always collected but only returnedd if asked:
                # we flatten these as direct attributes of a file object
                scan_result.update(file_infos.items())
            else:
                # always include errors even if empty
                scan_result['scan_errors'] = file_infos.get('scan_errors', [])

            no_scan_details = dict(scan_errors=[
                ('ERROR: Requested scan details unavailable in cache.',
                'This is either a bug or processing was aborted with CTRL-C.')]
            )

            scan_key = self.scan_key(path, file_infos)
            scan_details = self.scans.get(scan_key, no_scan_details)
            if TRACE:
                logger_debug('iterate:', 'scan_details:', scan_details, 'for path:', path, 'scan_key:', scan_key, '\n')

            # append errors to other top level errors if any
            scan_errors = scan_details.pop('scan_errors', [])
            scan_result['scan_errors'].extend(scan_errors)

            scan_result.update(scan_details)
            yield scan_result

    def close(self):
        """
        Close the underlying caches.
        """
        if self.infos:
            self.infos.close()
        if self.scans:
            self.scans.close()

    def clear(self, *args):
        """
        Purge the cache by deleting the corresponding cached data files.
        """
        self.close()
        fileutils.delete(self.cache_base_dir)


def get_scans_cache(cache_dir=scans_cache_dir):
    """
    Return a new unique persistent cache instance.
    """
    return ScanCache(cache_dir)


def get_scans_cache_class(cache_dir=scans_cache_dir):
    """
    Return a new unique persistent cache instance.
    """
    fileutils.create_dir(cache_dir)
    # create a unique temp directory in cache_dir
    cache_dir = fileutils.get_temp_dir(cache_dir, prefix=timeutils.time2tstamp() + '-')
    return partial(ScanCache, cache_dir)
