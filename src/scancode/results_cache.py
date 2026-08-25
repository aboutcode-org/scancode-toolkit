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

from commoncode.fileutils import create_dir
from commoncode.hash import binary_chunks
from scancode_config import results_cache_dir


def hasher_from_chunks(chunks):
    """
    Return a sha256 hasher loaded with `chunks`.
    """
    hasher = hashlib.sha256()
    for chunk in chunks:
        hasher.update(chunk)
    return hasher


def compute_results_cache_index(location, path):
    """
    Compute results_cache_index value for a Resource at `location`.
    """
    chunks = binary_chunks(location=location)
    sha256_hasher = hasher_from_chunks(chunks=chunks)
    # TODO: consider using filename instead of path
    sha256_hasher.update(path.encode('utf-8', 'surrogateescape'))
    return sha256_hasher.hexdigest()


def get_results_cache_directory_location(results_cache_index):
    """
    Return the location of the directory containing the cache files for a given
    `results_cache_index` hexstring.
    """
    # Split the hash into two subdirectories using the first two prefix pairs
    prefix1 = results_cache_index[:2]
    prefix2 = results_cache_index[2:4]
    directory_name = results_cache_index[4:]
    return os.path.join(results_cache_dir, prefix1, prefix2, directory_name)


def get_results_cache_file_location(results_cache_index, plugin_name):
    """
    Return the location of the file containing the cached results of the scanner
    `plugin_name` for a resource keyed by `results_cache_index` hexstring.
    """
    results_cache_directory_location = get_results_cache_directory_location(results_cache_index=results_cache_index)
    return os.path.join(results_cache_directory_location, plugin_name)


def get_results_cache_data(results_cache_index, plugin_name):
    """
    Return a mapping containing the results of scan plugin, `plugin_name`, for a
    resource keyed by `resource_cache_index` hexstring. If the cache file does
    not exist, an empty mapping is returned.
    """
    results_cache_file_location = get_results_cache_file_location(
        results_cache_index=results_cache_index,
        plugin_name=plugin_name
    )
    if os.path.exists(results_cache_file_location):
        with open(results_cache_file_location) as f:
            return json.load(f)
    else:
        return {}


def update_results_cache_data(results_cache_index, plugin_name, results):
    """
    Update the results cache with the `results` of the scanner `plugin_name`
    for the resource keyed by `results_cache_index`.
    """
    results_cache_directory_location = get_results_cache_directory_location(
        results_cache_index=results_cache_index
    )
    if not os.path.exists(results_cache_directory_location):
        create_dir(results_cache_directory_location)
    results_cache_file_location = os.path.join(results_cache_directory_location, plugin_name)
    with open(results_cache_file_location, 'w') as f:
        json.dump(results, f)
