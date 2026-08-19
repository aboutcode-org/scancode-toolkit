#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import hashlib
import json
import os

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OTHER_SCAN_GROUP
from commoncode.hash import binary_chunks
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode_config import resource_cache_dir


def hasher_from_chunks(chunks):
    """
    Return a sha256 hasher loaded with `chunks`
    """
    hasher = hashlib.sha256()
    for chunk in chunks:
        hasher.update(chunk)
    return hasher


def compute_resource_cache_index(location, path, **kwargs):
    """
    Compute resource cache index value for Resource at `location`
    """
    chunks = binary_chunks(location=location)
    sha256_hasher = hasher_from_chunks(chunks=chunks)
    # TODO: consider using filename instead of path
    sha256_hasher.update(path.encode('utf-8', 'surrogateescape'))

    result = {
        'resource_cache_index': sha256_hasher.hexdigest()
    }

    return result


def get_resource_cache_file_location(resource_cache_index):
    """
    Return the location of the cache file for a given `resource_cache_index`
    hexstring.
    """
    # Split the hash into two subdirectories using the first two prefix pairs
    prefix1 = resource_cache_index[:2]
    prefix2 = resource_cache_index[2:4]
    filename = resource_cache_index[4:]
    resource_cache_file_path = os.path.join(resource_cache_dir, prefix1, prefix2, filename)
    return resource_cache_file_path


@scan_impl
class ResourceCacheIndexScanner(ScanPlugin):
    """
    Compute resource cache index value for Resources in Codebase
    """
    resource_attributes = dict([
        ('resource_cache_index', attr.ib(default=None, repr=False)),
    ])

    run_order = 0
    sort_order = 0

    options = [
        PluggableCommandLineOption(('-rc', '--resource_cache_index'),
            is_flag=True, default=False,
            help='Scan <input> to compute resource cache index values for Resources in Codebase.',
            help_group=OTHER_SCAN_GROUP, sort_order=0
            )
    ]

    def is_enabled(self, resource_cache_index, **kwargs):
        return resource_cache_index

    def get_scanner(self, **kwargs):
        return compute_resource_cache_index

    def process_codebase(self, codebase, **kwargs):
        """
        Update Resource cache
        """
        for resource in codebase:
            # dump all resources to cache
            resource_cache_file_location = get_resource_cache_file_location(
                resource_cache_index=resource.resource_cache_index
            )
            with open(resource_cache_file_location, 'w') as f:
                f.write(json.dumps(resource.serialize(), check_circular=False))
