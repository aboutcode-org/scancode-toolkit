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

from hashlib import md5
from os.path import exists
from os.path import getsize
from os.path import getmtime
from os.path import join

import cachetools
import yg.lockfile

from commoncode.fileutils import file_iter
from licensedcode import src_dir
from licensedcode import license_index_cache_dir


"""
Various caching strategies either on-disk or in memory:
 - index peristent caching
 - per query and per query-run matches caching
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
    Return a checksum  computed from a file tree using the file paths, size and
    last modified time stamps.
    
    The purpose is to detect is there has been any modification to source code,
    compiled code or licenses or rule files.
    """
    hashable = [''.join([loc, str(getmtime(loc)), str(getsize(loc))]) for loc in file_iter(base_dir)]
    return md5(''.join(hashable)).hexdigest()


def get_or_build_index_from_cache():
    """
    Return a LicenseIndex loaded from cache. If the index is stale or does not
    exist, build a new index and caches it.
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules
    try:
        # acquire global lock file and wait until timeout to get a lock or die
        with yg.lockfile.FileLock(index_lock_file, timeout=60 * 3):
            # if we have a saved cached index
            if exists(tree_checksum_file) and exists(index_cache_file):
                # load saved tree_checksum and compare with current tree_checksum
                with open(tree_checksum_file, 'rb') as etcs:
                    existing_checksum = etcs.read()
                current_checksum = tree_checksum()
                if current_checksum == existing_checksum:
                    # this cached index is valid for the code and data

                    # load index from cache
                    with open(index_cache_file, 'rb') as ifc:
                        # Note: loads() is much (twice++) faster than load()
                        idx = LicenseIndex.loads(ifc.read())
                    return idx

            # here the cache is stale or non-existing: we need to regen the index
            idx = LicenseIndex(get_rules())
            with open(index_cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # and save the checksums
            with open(tree_checksum_file, 'wb') as ctcs:
                ctcs.write(tree_checksum())

            return idx

    except yg.lockfile.FileLockTimeout:
        # TODO: unable to lock in a nicer way
        raise


"""
A cache of recent matches from queries and query runs.

Several files in the same project or codebase are highly likely have repeated
identical license headers, texts or notices. Another common pattern is for
multiple copies of a full (and possibly long) license text. By caching and
returning the cached matches right away, we can avoid doing the same matching
over and over.

The approach is to use the hash of a sequence of token ids as a cache key either
for a whole query or a query run and to ignore positions. And as values we store
the LicenseMatch objects for this sequence of tokens. When we have a cache hit,
the returned cached LicenseMatch are adjusted for their query and line
positions. This way we can have cache hits for the same sequence of tokens
eventually starting at different positions in different queries. Actually we
cache a list of LicenseMatch, and this list may be empty: this way we also cache
the absence of matches for a sequence of tokens. This absence of matches can be
as costly to compute initially than an actual matches.

"""

MATCH_TYPE = 'cached'

matches_cache = cachetools.LRUCache(maxsize=1000)

def cache_key(tokens):
    return md5(' '.join(map(str, tokens))).digest()


def get_cached_matches(query_run):
    """
    Return a list of new LicenseMatch fetched from a cache or None given a list of token
    ids or an empty list if no cached LicenseMatch was found. New LicenseMatch are
    created using the provided start position to update the spans and
    line_by_pos.
    """
    global matches_cache
    if not matches_cache:
        return None
    key = cache_key(query_run.tokens)
    cached = matches_cache.get(key)
    # either we did not get a hit or we got a hit to nothing
    if cached is None:
        return None
    else:
        if not cached:
            return []
        else:
            return [lm.rebase(query_run.start, query_run.line_by_pos, MATCH_TYPE) for lm in cached]


def cache_matches(tokens, matches):
    """
    Add a list of LicenseMatch to the cache given a list of token ids.
    """
    global matches_cache
    key = cache_key(tokens)
    cached = matches_cache.get(key)
    if cached is None:
        matches_cache[key] = matches[:]
