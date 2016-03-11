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

import yg.lockfile

from commoncode.fileutils import file_iter
from licensedcode import src_dir
from licensedcode import license_index_cache_dir


index_lock_file = join(license_index_cache_dir, 'lockfile')
tree_checksum_file = join(license_index_cache_dir, 'tree_checksums')
index_cache_file = join(license_index_cache_dir, 'index_cache')


def tree_checksum(base_dir=src_dir):
    """
    Return a checksum  computed from a file tree using the file paths, size and
    modification time stamps
    """
    hashable = [''.join([loc, str(getmtime(loc)), str(getsize(loc))]) for loc in file_iter(base_dir)]
    return md5(''.join(hashable)).hexdigest()


def get_or_build_index_from_cache():
    """
    Return a LicenseIndex loaded from cache or build a new index and caches it.
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
                #  if this cached index is current for the code and data
                if current_checksum == existing_checksum:
                    # load index from cache
                    with open(index_cache_file, 'rb') as ifc:
                        idx = LicenseIndex.loads(ifc.read())
                        return idx

            #here the cache is stale or non-existing: we need to regen the index
            idx = LicenseIndex(get_rules())
            with open(index_cache_file, 'wb') as ifc:
                ifc.write(idx.dumps())

            # and save the checksums
            with open(tree_checksum_file, 'wb') as ctcs:
                ctcs.write(tree_checksum())

            return idx

    except yg.lockfile.FileLockTimeout:
        # handle unable to lock
        raise
