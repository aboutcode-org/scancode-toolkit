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

from licensedcode import root_dir
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


_ignored_from_hash = partial(
    ignore.is_ignored,
    ignores={'*.pyc': 'pyc files', '*~': 'temp gedit files', '*.swp': 'vi swap files'},
    unignores={}
)


def tree_checksum(tree_base_dir=src_dir, _ignored=_ignored_from_hash):
    """
    Return a checksum computed from a file tree using the file paths,
    size and last modified time stamps.
    The purpose is to detect is there has been any modification to
    source code or data files and use this as a proxy to verify the
    cache consistency.

    NOTE: this is not 100% fool proof but good enough in practice.
    """
    hashable = (pth + str(getmtime(pth)) + str(getsize(pth))
                for pth in file_iter(tree_base_dir, ignored=_ignored))
    return md5(''.join(sorted(hashable))).hexdigest()


LICENSE_INDEX_LOCK_TIMEOUT = 60 * 3


# If this file exists at the root, the cache is always checked for consistency
DEV_MODE = os.path.exists(os.path.join(root_dir, 'SCANCODE_DEV_MODE'))


def get_or_build_index_through_cache(
        check_consistency=DEV_MODE,
        return_index=True,
        # used for testing only
        _tree_base_dir=src_dir,
        _tree_checksum_file=tree_checksum_file,
        _index_lock_file=index_lock_file,
        _index_cache_file=index_cache_file,
        _licenses_data_dir=None,
        _rules_data_dir=None,
        _timeout=LICENSE_INDEX_LOCK_TIMEOUT,
        ):
    """
    Check and build or rebuild the LicenseIndex cache.
    If the cache does not exist, a new index is built an cached.
    Return the LicenseIndex if return_index is True.

    If `check_consistency` is True, the cache is checked for consistency
    and rebuilt if inconsistent or stale.

    If `check_consistency` is False, the cache is NOT checked for consistency
    If the cache files exist but stale, the cache WILL NOT be rebuilt
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules
    from licensedcode.models import licenses_data_dir
    from licensedcode.models import rules_data_dir
    _licenses_data_dir = _licenses_data_dir or licenses_data_dir
    _rules_data_dir = _rules_data_dir or rules_data_dir

    has_cache = exists(_index_cache_file)
    has_tree_checksum =  exists(_tree_checksum_file)

    # bypass check if no consistency check is needed
    if has_cache and has_tree_checksum and not check_consistency:
        return return_index and _load_index(_index_cache_file)

    # here, we have no cache or we want a validity check: lock, check
    # and build or rebuild as needed
    try:
        # acquire lock and wait until timeout to get a lock or die
        with yg.lockfile.FileLock(_index_lock_file, timeout=_timeout):
            current_checksum = None
            # is the current cache consistent or stale?
            if has_cache and has_tree_checksum:
                # if we have a saved cached index
                # load saved tree_checksum and compare with current tree_checksum
                with open(_tree_checksum_file, 'rb') as etcs:
                    existing_checksum = etcs.read()
                current_checksum = tree_checksum(tree_base_dir=_tree_base_dir)
                if current_checksum == existing_checksum:
                    # The cache is consistent with the latest code and data
                    # load and return
                    return return_index and _load_index(_index_cache_file)

            # Here, the cache is not consistent with the latest code and
            # data: It is either stale or non-existing: we need to
            # rebuild the index and cache it
            rules = get_rules(
                licenses_data_dir=_licenses_data_dir,
                rules_data_dir=_rules_data_dir)
            idx = LicenseIndex(rules)
            with open(_index_cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # save the new checksums tree
            with open(_tree_checksum_file, 'wb') as ctcs:
                ctcs.write(current_checksum or tree_checksum(tree_base_dir=_tree_base_dir))

            return return_index and idx

    except yg.lockfile.FileLockTimeout:
        # TODO: handle unable to lock in a nicer way
        raise


def _load_index(_index_cache_file=index_cache_file):
    """
    Return a LicenseIndex loaded from cache.
    """
    from licensedcode.index import LicenseIndex

    with open(_index_cache_file, 'rb') as ifc:
        # Note: weird but read() + loads() is much (twice++???) faster than load()
        idx = LicenseIndex.loads(ifc.read())
    return idx


"""Check the license index and reindex if needed."""
reindex = partial(get_or_build_index_through_cache, check_consistency=True, return_index=False)


# global in-memory license index instance
_LICENSES_INDEX = None


def get_index(_return_index=True):
    """
    Return and eventually cache an index built from an iterable of rules.
    Build the index from the built-in rules dataset.
    """
    global _LICENSES_INDEX
    if not _LICENSES_INDEX:
        _LICENSES_INDEX = get_or_build_index_through_cache()
    return _return_index and _LICENSES_INDEX


# global cache of licenses as mapping of lic key -> lic object
_LICENSES = {}


def get_licenses_db(licenses_data_dir=None):
    """
    Return a mapping of license key -> license object.
    """
    global _LICENSES
    if not _LICENSES :
        from licensedcode.models import load_licenses
        if not licenses_data_dir:
            from licensedcode.models import licenses_data_dir as ldd
            licenses_data_dir = ldd
        _LICENSES = load_licenses(licenses_data_dir)
    return _LICENSES
