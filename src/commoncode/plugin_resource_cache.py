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

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OTHER_SCAN_GROUP
from commoncode.hash import multi_checksums
from scancode_config import resource_cache_dir


RESOURCE_INDEX_DIR = "resource_cache_indices"


def compute_resource_cache_index(location, **kwargs):
    """
    Compute resource cache index value for Resource at `location`
    """
    result = {}

    md5 = multi_checksums(
        location=location,
        checksum_names=('md5')
    ).values()
    md5_bytes = bytes.fromhex(md5)

    # TODO: figure out if we can get the resource path through kwargs
    resource_path = kwargs['path']

    digest = hashlib.md5()
    digest.update(md5_bytes)
    digest.update(
        resource_path.encode('utf-8', 'surrogateescape')
    )
    result['resource_cache_index'] = digest.hexdigest()

    return result


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
            help_group=OTHER_SCAN_GROUP, sort_order=10
            )
    ]

    def is_enabled(self, resource_cache_idx, **kwargs):
        return resource_cache_idx

    def get_scanner(self, **kwargs):
        return compute_resource_cache_index

    def process_codebase(self, codebase, **kwargs):
        """
        Update resource cache
        """

        idx_cache_dir = os.path.join(resource_cache_dir, RESOURCE_INDEX_DIR)

        for resource in codebase:
            # dump all resources to cache
            cache_file = os.path.join(idx_cache_dir, resource.resource_cache_index)
            with open(cache_file, 'wb') as f:
                f.write(json.dumps(resource.serialize(), check_circular=False))
