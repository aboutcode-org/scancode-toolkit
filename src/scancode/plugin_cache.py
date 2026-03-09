# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) nexB Inc. and others. All rights reserved.
#
"""
CLI plugin to enable result caching.
"""

import click

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode.cache_manager import ResultCache


@scan_impl
class CachePlugin(ScanPlugin):
    """
    Enable file-level result caching for faster repeated scans.
    """
    
    options = [
        click.Option(
            ['--cache'],
            is_flag=True,
            default=False,
            help='Enable result caching for faster repeated scans.',
        ),
        click.Option(
            ['--cache-dir'],
            type=click.Path(exists=False, file_okay=False, dir_okay=True),
            metavar='DIR',
            help='Custom directory for cache storage. '
                 'Default: ~/.cache/scancode/file_results',
        ),
        click.Option(
            ['--force-reindex'],
            is_flag=True,
            default=False,
            help='Ignore cache and perform full rescan of all files.',
        ),
    ]
    
    def is_enabled(self, cache, **kwargs):
        return cache
    
    def setup(self, **kwargs):
        """
        Initialize cache manager for the scan.
        """
        pass


def get_cache_manager(cache, cache_dir, **kwargs):
    """
    Factory function to get cache manager instance.
    
    Args:
        cache: Boolean, whether caching is enabled
        cache_dir: Custom cache directory path
    
    Returns:
        ResultCache instance or None if caching disabled
    """
    if not cache:
        return None
    
    return ResultCache(cache_dir=cache_dir)