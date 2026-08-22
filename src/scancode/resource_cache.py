#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import hashlib
import json
import os

from commoncode.hash import binary_chunks
from scancode_config import scancode_cache_dir


RESOURCE_CACHE_DIR = os.path.join(scancode_cache_dir, "resource_cache_index")


def hasher_from_chunks(chunks):
    """
    Return a sha256 hasher loaded with `chunks`.
    """
    hasher = hashlib.sha256()
    for chunk in chunks:
        hasher.update(chunk)
    return hasher


def compute_resource_cache_index(location, path):
    """
    Compute resource_cache_index value for Resource at `location`.
    """
    chunks = binary_chunks(location=location)
    sha256_hasher = hasher_from_chunks(chunks=chunks)
    # TODO: consider using filename instead of path
    sha256_hasher.update(path.encode('utf-8', 'surrogateescape'))
    return sha256_hasher.hexdigest()


def get_resource_cache_directory_location(resource_cache_index):
    """
    Return the location of the directory containing the cache files for a given
    `resource_cache_index` hexstring.
    """
    # Split the hash into two subdirectories using the first two prefix pairs
    prefix1 = resource_cache_index[:2]
    prefix2 = resource_cache_index[2:4]
    directory_name = resource_cache_index[4:]
    return os.path.join(RESOURCE_CACHE_DIR, prefix1, prefix2, directory_name)


def get_resource_cache_file_location(resource_cache_index, plugin_name):
    """
    Return the location of the file containing the cached results of the scanner
    `plugin_name` for a resource keyed by `resource_cache_index` hexstring.
    """
    resource_cache_directory_location = get_resource_cache_directory_location(resource_cache_index=resource_cache_index)
    return os.path.join(resource_cache_directory_location, plugin_name)


def get_resource_cache_data(resource_cache_index, plugin_name):
    """
    Return a mapping containing the results of scan plugin, `plugin_name`, for a
    resource keyed by `resource_cache_index` hexstring. If the cache file does
    not exist, an empty mapping is returned.
    """
    resource_cache_file_location = get_resource_cache_file_location(
        resource_cache_index=resource_cache_index,
        plugin_name=plugin_name
    )
    if os.path.exists(resource_cache_file_location):
        with open(resource_cache_file_location) as f:
            return json.load(f)
    else:
        return {}


def update_resource_cache_data(resource_cache_index, plugin_name, results):
    """
    Update the resource cache with the `results` of the scanner `plugin_name`
    for the resource keyed by `resource_cache_index`.
    """
    resource_cache_file_location = get_resource_cache_file_location(
        resource_cache_index=resource_cache_index,
        plugin_name=plugin_name
    )
    with open(resource_cache_file_location, 'w') as f:
        json.dump(results, f)
