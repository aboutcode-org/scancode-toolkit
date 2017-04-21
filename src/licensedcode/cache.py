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

from functools import partial
from hashlib import md5
import os
from os.path import exists
from os.path import getmtime
from os.path import getsize
from os.path import join

import yg.lockfile  # @UnresolvedImport

from commoncode.fileutils import file_iter
from commoncode import ignore

from licensedcode import src_dir
from licensedcode import license_index_cache_dir


"""
An on-disk persistent cache of LicenseIndex. The index is pickled and invalidated if
there are any changes in the code or licenses text or rules. Loading and dumping the
cached index is safe to use across multiple processes using lock files.
"""

index_lock_file = join(license_index_cache_dir, 'lockfile')
tree_checksum_file = join(license_index_cache_dir, 'tree_checksums')
index_cache_file = join(license_index_cache_dir, 'index_cache')


_ignored_from_hash = partial(ignore.is_ignored, ignores={'*.pyc': 'pyc files'}, unignores={})


def tree_checksum(base_dir=src_dir, ignored=_ignored_from_hash):
    """
    Return a checksum computed from a file tree using the file paths, size and
    last modified time stamps.

    The purpose is to detect is there has been any modification to source code,
    compiled code or licenses or rule files and use this as a proxy to verify the
    cache consistency.
    """
    hashable = [''.join([loc, str(getmtime(loc)), str(getsize(loc))])
                for loc in file_iter(base_dir, ignored=_ignored_from_hash)]
    return md5(''.join(hashable)).hexdigest()


LICENSE_INDEX_LOCK_TIMEOUT = 60 * 3


# If this environment variable exists, the cache validity check will
# never be bypassed
DEV_MODE = os.environ.has_key('SCANCODE_DEV_MODE')


def get_or_build_index_from_cache(bypass_validity_check=True, dev_mode=DEV_MODE):
    """
    Return a LicenseIndex loaded from cache. If the index is stale or
    does not exist, build a new index and caches it based on the
    provided arguments.

    If `bypass_validity_check` is True, the cache is NOT checked for
    validity. Only its presence is checked and it is built only if it
    not present. If present and stale, the cache WIL NOT be rebuilt.
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules

    has_cache = exists(index_cache_file)

    if has_cache and bypass_validity_check and not dev_mode:
        return load_cache()

    # we have no cache or we want a validity check: lock, check and
    # load. build if needed
    try:
        # acquire lock and wait until timeout to get a lock or die
        with yg.lockfile.FileLock(index_lock_file, timeout=LICENSE_INDEX_LOCK_TIMEOUT):
            current_checksum = None
            # if we have a saved cached index
            if exists(tree_checksum_file) and has_cache:
                # load saved tree_checksum and compare with current tree_checksum
                with open(tree_checksum_file, 'rb') as etcs:
                    existing_checksum = etcs.read()
                current_checksum = tree_checksum()
                if current_checksum == existing_checksum:
                    # The cache is consistent with the latest code and data:
                    # we load index from cache
                    return load_cache()

            # Here, the cache is not consistent with the latest code and data:
            # It is either stale or non-existing: we need to cleanup/regen
            # regen the index
            idx = LicenseIndex(get_rules())
            with open(index_cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # save the new checksums tree
            with open(tree_checksum_file, 'wb') as ctcs:
                ctcs.write(current_checksum or tree_checksum())

            return idx

    except yg.lockfile.FileLockTimeout:
        # TODO: unable to lock in a nicer way
        raise


def load_cache():
    """
    Return a LicenseIndex loaded from cache.
    """
    from licensedcode.index import LicenseIndex
    with open(index_cache_file, 'rb') as ifc:
        # Note: weird but read() + loads() is much (twice++???) faster than load()
        idx = LicenseIndex.loads(ifc.read())
    return idx

