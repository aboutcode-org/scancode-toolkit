#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import fnmatch
import pickle
import multiregex

import attr
import click

from collections import defaultdict

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

# This is the Pickle protocol we use, which was added in Python 3.4.
PICKLE_PROTOCOL = 4

PACKAGE_INDEX_LOCK_TIMEOUT = 60
PACKAGE_INDEX_DIR = 'package_patterns_index'
PACKAGE_INDEX_FILENAME = 'index_cache'
PACKAGE_LOCKFILE_NAME = 'scancode_package_index_lockfile'


@attr.s
class PkgManifestPatternsCache:
    """
    Represent cachable package manifest regex patterns, prematchers
    and mappings from regex patterns to datasource IDs for all datafile
    handlers.
    """

    handler_by_regex = attr.ib(default=attr.Factory(dict))
    system_package_matcher = attr.ib(default=None)
    application_package_matcher = attr.ib(default=None)
    all_package_matcher = attr.ib(default=None)

    @staticmethod
    def all_multiregex_patterns(application_multiregex_patterns, system_multiregex_patterns):
        return application_multiregex_patterns + [
            multiregex_pattern
            for multiregex_pattern in system_multiregex_patterns
            if multiregex_pattern not in application_multiregex_patterns
        ]

    @classmethod
    def load_or_build(
        cls,
        packagedcode_cache_dir=packagedcode_cache_dir,
        scancode_cache_dir=scancode_cache_dir,
        force=False,
        timeout=PACKAGE_INDEX_LOCK_TIMEOUT,
        system_package_datafile_handlers=SYSTEM_PACKAGE_DATAFILE_HANDLERS,
        application_package_datafile_handlers=APPLICATION_PACKAGE_DATAFILE_HANDLERS,
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
                print('Inconsistent Package cache: rebuilding index.')
                print(str(e))
                print(traceback.format_exc())

        from scancode import lockfile
        lock_file = os.path.join(scancode_cache_dir, PACKAGE_LOCKFILE_NAME)

        # here, we have no cache: lock, check and rebuild
        try:
            # acquire lock and wait until timeout to get a lock or die
            with lockfile.FileLock(lock_file).locked(timeout=timeout):

                system_multiregexes = build_mappings_and_multiregex_patterns(
                    datafile_handlers=system_package_datafile_handlers,
                )
                application_multiregexes = build_mappings_and_multiregex_patterns(
                    datafile_handlers=application_package_datafile_handlers,
                )
                all_multiregex_matcher = PkgManifestPatternsCache.all_multiregex_patterns(
                    application_multiregex_patterns=application_multiregexes.patterns,
                    system_multiregex_patterns=system_multiregexes.patterns,
                )
                system_package_matcher = multiregex.RegexMatcher(system_multiregexes.patterns)
                application_package_matcher = multiregex.RegexMatcher(application_multiregexes.patterns)
                all_package_matcher = multiregex.RegexMatcher(all_multiregex_matcher)
                handler_by_regex = (
                    system_multiregexes.handler_by_regex |
                    application_multiregexes.handler_by_regex
                )
                package_cache = cls(
                    handler_by_regex=handler_by_regex,
                    system_package_matcher=system_package_matcher,
                    application_package_matcher=application_package_matcher,
                    all_package_matcher=all_package_matcher,
                )
                package_cache.dump(cache_file)
                return package_cache

        except lockfile.LockTimeout:
            # TODO: handle unable to lock in a nicer way
            raise 

    def dump(self, cache_file):
        """
        Dump this license cache on disk at ``cache_file``.
        """
        with open(cache_file, 'wb') as fn:
            pickle.dump(self, fn, protocol=PICKLE_PROTOCOL)


def get_prematchers_from_glob_pattern(pattern):
    """
    Get a list of prematchers required to initialize the
    multiregex matchers for a package manifest pattern.

    Prematchers are words that must be present for a pattern to
    be matched, and this acts as a pre-matching filter for fast
    matching.
    >>> get_prematchers_from_glob_pattern('*pyproject.toml')
    ['pyproject.toml']
    """
    return [
        prematcher.lower().lstrip("/")
        for prematcher in pattern.split("*")
        if prematcher
    ]

@attr.s
class AcceleratedPattern():
    regex :str = attr.ib(default=None) # regular expression string
    prematchers :list[str] = attr.ib(default=[]) # list of prematcher strinsg for this regex
    handler_datasource_ids :list[str] = attr.ib(default=[]) # handler


@attr.s
class MultiRegexPatternsandMappings:
    multiregex_patterns :list[AcceleratedPattern] = attr.ib(default=[])
    handler_by_regex :dict = attr.ib(default={})

    @property
    def patterns(self):
        return [
            (pattern.regex, pattern.prematchers)
            for pattern in self.multiregex_patterns 
        ]


def build_mappings_and_multiregex_patterns(datafile_handlers):
    """
    Return a mapping of regex patterns to datafile handler IDs and
    multiregex patterns consisting of regex patterns and prematchers.
    """
    handler_by_regex = defaultdict(list)
    multiregex_patterns = []

    if not datafile_handlers:
        return multiregex_patterns, handler_by_regex

    with_patterns = []

    for handler in datafile_handlers:
        if handler.path_patterns:
            with_patterns.append(handler)

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

    for regex, handler_ids in handler_by_regex.items():
        regex_and_prematcher = AcceleratedPattern(
            regex=regex,
            prematchers=prematchers_by_regex.get(regex, []),
            handler_datasource_ids=handler_ids,
        )
        multiregex_patterns.append(regex_and_prematcher)

    return MultiRegexPatternsandMappings(
        handler_by_regex=handler_by_regex,
        multiregex_patterns=multiregex_patterns,
    )


def get_cache(
    force=False,
    packagedcode_cache_dir=packagedcode_cache_dir,
    scancode_cache_dir=scancode_cache_dir,
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
    Return a PkgManifestPatternsCache loaded from ``cache_file``.
    """
    with open(cache_file, 'rb') as lfc:
        try:
            return pickle.load(lfc)
        except Exception as e:
            msg = (
                'ERROR: Failed to load package cache (the file may be corrupted ?).\n'
                f'Please delete "{cache_file}" and retry.\n'
                'If the problem persists, copy this error message '
                'and submit a bug report at https://github.com/nexB/scancode-toolkit/issues/'
            )
            raise Exception(msg) from e


@click.command(name='scancode-reindex-package-patterns')
@click.help_option('-h', '--help')
def cache_package_patterns(*args, **kwargs):
    """Create scancode package manifest patterns cache and exit"""
    click.echo('Rebuilding the package cache patterns...')
    get_cache(force=True)
    click.echo('Done.')


if __name__ == '__main__':
    cache_package_patterns()
