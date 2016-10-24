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

from array import array
from hashlib import md5
from os.path import exists
from os.path import getmtime
from os.path import getsize
from os.path import join

import yg.lockfile  # @UnresolvedImport

from commoncode.fileutils import create_dir
from commoncode.fileutils import file_iter

from licensedcode import src_dir
from licensedcode import license_index_cache_dir
from licensedcode import license_matches_cache_dir


"""
Caching on-disk  of LicenseIndex and LicenseMatches:
"""


"""
An on-disk persistent cache of LicenseIndex. The index is pickled and
invalidated if there are any changes in the code or licenses text or rules.
Loading and dumping the cached index is safe to use across multiple processes
using lock files.
"""

index_lock_file = join(license_index_cache_dir, 'lockfile')
tree_checksum_file = join(license_index_cache_dir, 'tree_checksums')
index_cache_file = join(license_index_cache_dir, 'index_cache')


def tree_checksum(base_dir=src_dir):
    """
    Return a checksum computed from a file tree using the file paths, size and
    last modified time stamps.

    The purpose is to detect is there has been any modification to source code,
    compiled code or licenses or rule files and use this as a proxyx to verify
    the cache consistency.
    """
    hashable = [''.join([loc, str(getmtime(loc)), str(getsize(loc))])
                for loc in file_iter(base_dir)]
    return md5(''.join(hashable)).hexdigest()


LICENSE_INDEX_LOCK_TIMEOUT = 60 * 3


def get_or_build_index_from_cache(force_clear=False):
    """
    Return a LicenseIndex loaded from cache. If the index is stale or does not exist,
    build a new index and caches it. Clear or purge the LicenseMatch cache as needed.
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules
    try:
        # acquire lock and wait until timeout to get a lock or die
        with yg.lockfile.FileLock(index_lock_file, timeout=LICENSE_INDEX_LOCK_TIMEOUT):
            if force_clear:
                license_matches_cache.clear(0)

            # if we have a saved cached index
            if exists(tree_checksum_file) and exists(index_cache_file):
                # load saved tree_checksum and compare with current tree_checksum
                with open(tree_checksum_file, 'rb') as etcs:
                    existing_checksum = etcs.read()
                current_checksum = tree_checksum()
                if current_checksum == existing_checksum:
                    # The cache is consistent with the latest code and data:
                    # we load index from cache
                    with open(index_cache_file, 'rb') as ifc:
                        # Note: loads() is much (twice++???) faster than load()
                        idx = LicenseIndex.loads(ifc.read())
                    return idx

            # Here, the cache is not consistent with the latest code and data:
            # It is either stale or non-existing: we need to cleanup/regen

            # clear the LicenseMatch cache entirely
            license_matches_cache.clear(0)

            # regen the index
            idx = LicenseIndex(get_rules())
            with open(index_cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # save the new checksums tree
            with open(tree_checksum_file, 'wb') as ctcs:
                ctcs.write(tree_checksum())

            return idx

    except yg.lockfile.FileLockTimeout:
        # TODO: unable to lock in a nicer way
        raise


"""
A cache of recent matches from queries and query runs.

Several files in the same project or codebase are highly likely have repeated
identical license headers, texts or notices. Another common pattern is multiple
copies of a complete (and possibly long) license text. By caching and returning
the cached matches right away, we can avoid doing the same matching over and
over.

The approach is to use the hash of a sequence of token ids as a cache key either
for a whole query or a query run and to ignore the actual start position.
As values we cache a list of LicenseMatch objects for this sequence of tokens.

When we have a cache hit, the returned cached LicenseMatch are adjusted for
their query and line positions. This way we can have cache hits for the same
sequence of tokens eventually starting at different positions in different
queries.

The cached list of LicenseMatch may be empty: this way we also cache the absence
of matches for a sequence of tokens. This absence of matches can be as costly to
compute initially than an actual matches.
"""

MATCH_CACHE = '0-cached'


class LicenseMatchCache(object):
    """
    A file-based cache for license matches.
    This is NOT thread-safe, but is multi-process safe.
    """
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        create_dir(cache_dir)
        from diskcache import FanoutCache
        self.cache = FanoutCache(cache_dir)

    def key(self, tokens):
        """
        Return a computed cache key for a sequence of query `tokens` numeric ids.
        """
        return md5(array('h', tokens).tostring()).hexdigest()

    def get(self, query_run):
        """
        Return a sequence of cached LicenseMatch if found in the cache or None.
        It may return an empty sequence if this was a cached value.
        """
        cache_key = self.key(query_run.tokens)
        cached = self.cache.get(cache_key)
        # either we did not get a hit or we got a hit to nothing (empty list)
        # which is a valid cached value
        if not cached:
            return cached

        qrs = query_run.start
        qre = query_run.end
        qlbp = query_run.line_by_pos
        return [lm.rebase(qrs, qre, qlbp, MATCH_CACHE) for lm in cached]

    def put(self, query_run, matches):
        """
        Cache a license `matches` sequence given a `query run` tokens.
        """
        cache_key = self.key(query_run.tokens)
        self.cache[cache_key] = matches
        return cache_key

    def clear(self, *args):
        """
        Purge the cache keeping up to `max_size` of the most recently created
        entries. If `max_size` is zero, the whole cache is purged.
        Raise an exception if a write lock cannot be acquired.
        """
        self.cache.clear()

# global cache
license_matches_cache = LicenseMatchCache(cache_dir=license_matches_cache_dir)
