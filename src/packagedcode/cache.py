#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import json
import attr
import fnmatch

from commoncode.fileutils import create_dir

from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
from packagedcode import SYSTEM_PACKAGE_DATAFILE_HANDLERS

from scancode_config import packagedcode_cache_dir
from scancode_config import scancode_cache_dir

"""
An on-disk persistent cache of package manifest patterns and related package
manifest handlers mapping. Loading and dumping the cached package manifest
patterns is safe to use across multiple processes using lock files.
"""

# global in-memory cache of the PkgManifestPatternsCache
_PACKAGE_CACHE = None

PACKAGE_INDEX_LOCK_TIMEOUT = 60 * 6
PACKAGE_INDEX_DIR = 'package_patterns_index'
PACKAGE_INDEX_FILENAME = 'index_cache'
PACKAGE_LOCKFILE_NAME = 'scancode_package_index_lockfile'
PACKAGE_CHECKSUM_FILE = 'scancode_package_index_tree_checksums'


@attr.s
class PkgManifestPatternsCache:
    """
    Represent cachable package manifest regex patterns, prematchers
    and mappings from regex patterns to datasource IDs for all datafile
    handlers.
    """

    handler_by_regex = attr.ib(default=attr.Factory(dict))
    system_multiregex_patterns = attr.ib(default=attr.Factory(list))
    application_multiregex_patterns = attr.ib(default=attr.Factory(list))

    @staticmethod
    def all_multiregex_patterns(self):
        return self.application_multiregex_patterns + [
            multiregex_pattern
            for multiregex_pattern in self.system_multiregex_patterns
            if multiregex_pattern not in self.application_multiregex_patterns
        ]

    @classmethod
    def from_mapping(cls, cache_mapping):
        return cls(**cache_mapping)

    @staticmethod
    def load_or_build(
        packagedcode_cache_dir=packagedcode_cache_dir,
        scancode_cache_dir=scancode_cache_dir,
        force=False,
        timeout=PACKAGE_INDEX_LOCK_TIMEOUT,
    ):
        """
        Load or build and save and return a PkgManifestPatternsCache object.

        We either load a cached PkgManifestPatternsCache or build and cache the patterns.

        - If the cache exists, it is returned unless corrupted.
        - If ``force`` is True, or if the cache does not exist a new index is built
          and cached.
        """
        idx_cache_dir = os.path.join(packagedcode_cache_dir, PACKAGE_INDEX_DIR)
        create_dir(idx_cache_dir)
        cache_file = os.path.join(idx_cache_dir, PACKAGE_INDEX_FILENAME)
        has_cache = os.path.exists(cache_file) and os.path.getsize(cache_file)

        # bypass build if cache exists
        if has_cache and not force:
            try:
                return load_cache_file(cache_file)
            except Exception as e:
                # work around some rare Windows quirks
                import traceback
                print('Inconsistent License cache: rebuilding index.')
                print(str(e))
                print(traceback.format_exc())


        from scancode import lockfile
        lock_file = os.path.join(scancode_cache_dir, PACKAGE_LOCKFILE_NAME)

        # here, we have no cache: lock, check and rebuild
        try:
            # acquire lock and wait until timeout to get a lock or die
            with lockfile.FileLock(lock_file).locked(timeout=timeout):

                system_multiregex_patterns, system_handlers_by_regex = build_mappings_and_multiregex_patterns(
                    datafile_handlers=SYSTEM_PACKAGE_DATAFILE_HANDLERS,
                )
                application_multiregex_patterns, application_handlers_by_regex = build_mappings_and_multiregex_patterns(
                    datafile_handlers=APPLICATION_PACKAGE_DATAFILE_HANDLERS,
                )
                package_cache = PkgManifestPatternsCache(
                    handler_by_regex=system_handlers_by_regex + application_handlers_by_regex,
                    system_multiregex_patterns=system_multiregex_patterns,
                    application_multiregex_patterns=application_multiregex_patterns,
                )
                package_cache.dump(cache_file)
                return package_cache

        except lockfile.LockTimeout:
            # TODO: handle unable to lock in a nicer way
            raise

    def dump(self, cache_file):
        """
        Dump this package cache on disk at ``cache_file``.
        """
        package_cache = {}
        with open(cache_file, 'w') as f:
            json.dump(package_cache, f)


def get_prematchers_from_glob_pattern(pattern):
    return [
        prematcher.lower().lstrip("/")
        for prematcher in pattern.split("*")
        if prematcher
    ]


def build_mappings_and_multiregex_patterns(
    datafile_handlers,
):
    """
    Return an index built from rules and licenses directories
    """
    with_patterns = []

    for handler in datafile_handlers:
        if handler.path_patterns:
            with_patterns.append(handler)

    handler_by_regex = {}
    prematchers_by_regex = {}

    for handler in with_patterns:
        for pattern in handler.path_patterns:
            regex_pattern = fnmatch.translate(pattern)
            regex_pattern = fr"{regex_pattern}"

            prematchers_by_regex[regex_pattern] = get_prematchers_from_glob_pattern(pattern)

            if regex_pattern in handler_by_regex:
                handler_by_regex[regex_pattern].append(handler.datasource_id)
            else:
                handler_by_regex[regex_pattern]= [handler.datasource_id]

    multiregex_patterns = []
    for regex in handler_by_regex.keys():
        regex_and_prematcher = (regex, prematchers_by_regex.get(regex, []))
        multiregex_patterns.append(regex_and_prematcher)

    return handler_by_regex, multiregex_patterns


def get_cache(
    force=False,
):
    """
    Return a PkgManifestPatternsCache either rebuilt, cached or loaded from disk.
    """
    global _PACKAGE_CACHE

    if force or not _PACKAGE_CACHE:
        _PACKAGE_CACHE = PkgManifestPatternsCache.load_or_build(
            packagedcode_cache_dir=packagedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=force,
            # used for testing only
            timeout=PACKAGE_INDEX_LOCK_TIMEOUT,
        )
    return _PACKAGE_CACHE


def load_cache_file(cache_file):
    """
    Return a PkgManifestPatternsCache loaded from JSON ``cache_file``.
    """
    with open(cache_file) as f:
        cache = json.load(f)

    return PkgManifestPatternsCache.from_mapping(cache)
