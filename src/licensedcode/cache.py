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

from __future__ import absolute_import, print_function

from functools import partial
from hashlib import md5
from os.path import exists
from os.path import getmtime
from os.path import getsize
from os.path import join
import sys

from six import reraise
import yg.lockfile  # NOQA

from commoncode.fileutils import resource_iter
from commoncode.fileutils import create_dir
from commoncode import ignore

from scancode_config import scancode_cache_dir
from scancode_config import scancode_src_dir
from scancode_config import SCANCODE_DEV_MODE

"""
An on-disk persistent cache of LicenseIndex. The index is pickled and
invalidated if there are any changes in the code or licenses text or rules.
Loading and dumping the cached index is safe to use across multiple processes
using lock files.
"""

LICENSE_INDEX_LOCK_TIMEOUT = 60 * 4

# global in-memory cache of the main license index instance
_LICENSES_BY_KEY_INDEX = None


def get_index(cache_dir=scancode_cache_dir, check_consistency=SCANCODE_DEV_MODE,
              return_value=True):
    """
    Return and eventually cache an index built from an iterable of rules.
    Build the index from the built-in rules dataset.
    """
    global _LICENSES_BY_KEY_INDEX
    if not _LICENSES_BY_KEY_INDEX:
        _LICENSES_BY_KEY_INDEX = get_cached_index(cache_dir, check_consistency)
    if return_value:
        return _LICENSES_BY_KEY_INDEX


# global in-memory cache of a mapping of key -> license instance
_LICENSES_BY_KEY = {}


def get_licenses_db(licenses_data_dir=None):
    """
    Return a mapping of license key -> license object.
    """
    global _LICENSES_BY_KEY
    if not _LICENSES_BY_KEY :
        from licensedcode.models import load_licenses
        if not licenses_data_dir:
            from licensedcode.models import licenses_data_dir as ldd
            licenses_data_dir = ldd
        _LICENSES_BY_KEY = load_licenses(licenses_data_dir)
    return _LICENSES_BY_KEY


# global in-memory cache for the unknown license symbol
_UNKNOWN_SPDX_SYMBOL = None


def get_unknown_spdx_symbol(licenses_data_dir=None):
    """
    Return the unknown SPDX license symbol.
    """
    global _UNKNOWN_SPDX_SYMBOL
    if not _UNKNOWN_SPDX_SYMBOL:
        from license_expression import LicenseSymbolLike
        licenses = get_licenses_db(licenses_data_dir)
        _UNKNOWN_SPDX_SYMBOL = LicenseSymbolLike(licenses[u'unknown-spdx'])

    return _UNKNOWN_SPDX_SYMBOL


# global in-memory cache for SPDX license as a LicenseSymbol->LicenseLikeSymbol
# wrapping a full License object
_LICENSE_SYMBOLS_BY_SPDX_KEY = None


def get_spdx_symbols(licenses_data_dir=None):
    """
    Return a mapping of (SPDX LicenseSymbol -> lowercased SPDX license key-> key}
    """
    global _LICENSE_SYMBOLS_BY_SPDX_KEY
    if not _LICENSE_SYMBOLS_BY_SPDX_KEY:
        from license_expression import LicenseSymbol
        from license_expression import LicenseSymbolLike
        _LICENSE_SYMBOLS_BY_SPDX_KEY = {}
        licenses = get_licenses_db(licenses_data_dir)

        for lic in licenses.values():
            if not (lic.spdx_license_key or lic.other_spdx_license_keys):
                continue

            symbol = LicenseSymbolLike(lic)
            if lic.spdx_license_key:
                slk = lic.spdx_license_key.lower()
                existing = _LICENSE_SYMBOLS_BY_SPDX_KEY.get(slk)
                if existing:
                    raise ValueError('Duplicated SPDX license key: %(slk)r defined in %(key)r and %(existing)r' % locals())
                _LICENSE_SYMBOLS_BY_SPDX_KEY[slk] = symbol

            for other_spdx in lic.other_spdx_license_keys:
                if not (other_spdx and other_spdx.strip()):
                    continue
                slk = other_spdx.lower()
                existing = _LICENSE_SYMBOLS_BY_SPDX_KEY.get(slk)
                if existing:
                    raise ValueError('Duplicated "other" SPDX license key: %(slk)r defined in %(key)r and %(existing)r' % locals())
                _LICENSE_SYMBOLS_BY_SPDX_KEY[slk] = symbol

    return _LICENSE_SYMBOLS_BY_SPDX_KEY


def get_cached_index(cache_dir=scancode_cache_dir,
                     check_consistency=SCANCODE_DEV_MODE,
                     # used for testing only
                     timeout=LICENSE_INDEX_LOCK_TIMEOUT,
                     tree_base_dir=scancode_src_dir,
                     licenses_data_dir=None, rules_data_dir=None,):
    """
    Return a LicenseIndex: either load a cached index or build and cache the
    index.
    - If the cache does not exist, a new index is built an cached.
    - If `check_consistency` is True, the cache is checked for consistency and
      rebuilt if inconsistent or stale.
    - If `check_consistency` is False, the cache is NOT checked for consistency
      If the cache files exist but ARE stale, the cache WILL NOT be rebuilt
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules
    from licensedcode.models import get_all_spdx_key_tokens
    from licensedcode.models import licenses_data_dir as ldd
    from licensedcode.models import rules_data_dir as rdd

    licenses_data_dir = licenses_data_dir or ldd
    rules_data_dir = rules_data_dir or rdd

    lock_file, checksum_file, cache_file = get_license_cache_paths(cache_dir)

    has_cache = exists(cache_file)
    has_tree_checksum = exists(checksum_file)

    # bypass check if no consistency check is needed
    if has_cache and has_tree_checksum and not check_consistency:
        return load_index(cache_file)

    # here, we have no cache or we want a validity check: lock, check
    # and build or rebuild as needed
    try:
        # acquire lock and wait until timeout to get a lock or die
        with yg.lockfile.FileLock(lock_file, timeout=timeout):
            current_checksum = None
            # is the current cache consistent or stale?
            if has_cache and has_tree_checksum:
                # if we have a saved cached index
                # load saved tree_checksum and compare with current tree_checksum
                with open(checksum_file, 'rb') as etcs:
                    existing_checksum = etcs.read()
                current_checksum = tree_checksum(tree_base_dir=tree_base_dir)
                if current_checksum == existing_checksum:
                    # The cache is consistent with the latest code and data
                    # load and return
                    return load_index(cache_file)

            # Here, the cache is not consistent with the latest code and
            # data: It is either stale or non-existing: we need to
            # rebuild the index and cache it
            rules = get_rules(
                licenses_data_dir=licenses_data_dir,
                rules_data_dir=rules_data_dir)

            license_db = get_licenses_db(licenses_data_dir=licenses_data_dir)
            spdx_tokens = set(get_all_spdx_key_tokens(license_db))

            idx = LicenseIndex(rules, _spdx_tokens=spdx_tokens)

            with open(cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # save the new checksums tree
            with open(checksum_file, 'wb') as ctcs:
                ctcs.write(current_checksum
                           or tree_checksum(tree_base_dir=tree_base_dir))

            return idx

    except yg.lockfile.FileLockTimeout:
        # TODO: handle unable to lock in a nicer way
        raise


def load_index(cache_file):
    """
    Return a LicenseIndex loaded from cache.
    """
    from licensedcode.index import LicenseIndex
    with open(cache_file, 'rb') as ifc:
        # Note: weird but read() + loads() is much (twice++???) faster than load()
        try:
            return LicenseIndex.loads(ifc.read())
        except:
            ex_type, ex_msg, ex_traceback = sys.exc_info()
            message = (str(ex_msg) +
                '\nERROR: Failed to load license cache (the file may be corrupted ?).\n'
                'Please delete "{cache_file}" and retry.\n'
                'If the problem persists, copy this error message '
                'and submit a bug report.\n'.format(**locals()))
            reraise(ex_type, message, ex_traceback)


_ignored_from_hash = partial(
    ignore.is_ignored,
    ignores={
        '*.pyc': 'pyc files',
        '*~': 'temp gedit files',
        '*.swp': 'vi swap files'
    },
    unignores={}
)


def tree_checksum(tree_base_dir=scancode_src_dir, _ignored=_ignored_from_hash):
    """
    Return a checksum computed from a file tree using the file paths, size and
    last modified time stamps. The purpose is to detect is there has been any
    modification to source code or data files and use this as a proxy to verify
    the cache consistency.

    NOTE: this is not 100% fool proof but good enough in practice.
    """
    resources = resource_iter(tree_base_dir, ignored=_ignored, with_dirs=False)
    hashable = (pth + str(getmtime(pth)) + str(getsize(pth)) for pth in resources)
    return md5(''.join(sorted(hashable))).hexdigest()


def get_license_cache_paths(cache_dir=scancode_cache_dir):
    """
    Return a tuple of index cache files given a master `cache_dir`
    """
    idx_cache_dir = join(cache_dir, 'license_index')
    create_dir(idx_cache_dir)

    lock_file = join(idx_cache_dir, 'lockfile')
    checksum_file = join(idx_cache_dir, 'tree_checksums')
    cache_file = join(idx_cache_dir, 'index_cache')

    return lock_file, checksum_file, cache_file
