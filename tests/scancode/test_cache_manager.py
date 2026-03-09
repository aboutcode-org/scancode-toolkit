# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) nexB Inc. and others. All rights reserved.
#
"""
Tests for result caching functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from scancode.cache_manager import ResultCache


class TestResultCache:
    
    def test_cache_stores_and_retrieves_results(self):
        """Test basic cache store and retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=tmpdir)
            
            # Create a test file
            test_file = Path(tmpdir) / 'test.py'
            test_file.write_text('# Test file\nprint("hello")')
            
            scan_options = {'license': True, 'copyright': False}
            result = {'licenses': ['MIT'], 'path': str(test_file)}
            
            # Store result
            cache.store_result(test_file, scan_options, result)
            
            # Retrieve result
            cached = cache.get_cached_result(test_file, scan_options)
            
            assert cached is not None
            assert cached['licenses'] == ['MIT']
            assert cache.stats['hits'] == 1
    
    def test_cache_miss_on_file_change(self):
        """Test cache invalidation when file content changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=tmpdir)
            test_file = Path(tmpdir) / 'test.py'
            
            # First content and scan
            test_file.write_text('# Version 1')
            scan_options = {'license': True}
            result1 = {'version': 1}
            cache.store_result(test_file, scan_options, result1)
            
            # Modify file
            test_file.write_text('# Version 2')
            
            # Should be cache miss
            cached = cache.get_cached_result(test_file, scan_options)
            assert cached is None
            assert cache.stats['misses'] == 1
    
    def test_cache_miss_on_scan_options_change(self):
        """Test cache invalidation when scan options change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=tmpdir)
            test_file = Path(tmpdir) / 'test.py'
            test_file.write_text('# Test')
            
            # First scan with license
            options1 = {'license': True}
            cache.store_result(test_file, options1, {'result': 1})
            
            # Second scan with copyright added
            options2 = {'license': True, 'copyright': True}
            cached = cache.get_cached_result(test_file, options2)
            
            assert cached is None  # Should miss due to different options
    
    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=tmpdir)
            test_file = Path(tmpdir) / 'test.py'
            test_file.write_text('# Test')
            
            options = {'license': True}
            
            # First scan: miss
            cache.get_cached_result(test_file, options)
            
            # Store and retrieve: hit
            cache.store_result(test_file, options, {'data': 'test'})
            cache.get_cached_result(test_file, options)
            
            stats = cache.get_stats()
            assert stats['hits'] == 1
            assert stats['misses'] == 1
            assert stats['hit_rate_percent'] == 50.0
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=tmpdir)
            test_file = Path(tmpdir) / 'test.py'
            test_file.write_text('# Test')
            
            options = {'license': True}
            cache.store_result(test_file, options, {'data': 'test'})
            
            # Clear cache
            cache.clear_cache()
            
            # Should be miss after clear
            cached = cache.get_cached_result(test_file, options)
            assert cached is None