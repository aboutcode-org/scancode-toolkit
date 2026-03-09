# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# Visit https://aboutcode.org and https://github.com/aboutcode-org/scancode-toolkit/
#
"""
File-level result caching for faster repeated scans.
"""

import hashlib
import json
import os
from pathlib import Path

from commoncode import fileutils
scancode_version = "dev"

class ResultCache:
    """
    Manages cached scan results for files based on content hash.
    """
    
    def __init__(self, cache_dir=None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Custom cache directory path. If None, uses default.
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use platform-appropriate cache directory
            cache_base = Path.home() / '.cache' / 'scancode'
            self.cache_dir = cache_base / 'file_results'
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {'hits': 0, 'misses': 0}
    
    def _get_file_hash(self, file_path, scan_options):
        """
        Generate unique hash for file + scan configuration.
        
        Args:
            file_path: Path to file being scanned
            scan_options: Dict of enabled scan options (e.g., {'license': True})
        
        Returns:
            SHA256 hex digest string
        """
        hasher = hashlib.sha256()
        
        # Hash file content
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        
        # Hash scan configuration to invalidate on option changes
        config_str = f"{scancode_version}:{sorted(scan_options.items())}"
        hasher.update(config_str.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def get_cached_result(self, file_path, scan_options):
        """
        Retrieve cached scan result if available.
        
        Args:
            file_path: Path to file
            scan_options: Dict of scan options
        
        Returns:
            Dict with scan results or None if not cached
        """
        file_hash = self._get_file_hash(file_path, scan_options)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.stats['hits'] += 1
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupted cache, remove it
                cache_file.unlink(missing_ok=True)
                self.stats['misses'] += 1
                return None
        
        self.stats['misses'] += 1
        return None
    
    def store_result(self, file_path, scan_options, result):
        """
        Store scan result in cache.
        
        Args:
            file_path: Path to scanned file
            scan_options: Dict of scan options used
            result: Scan result dict to cache
        """
        file_hash = self._get_file_hash(file_path, scan_options)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except IOError as e:
            # Don't fail scan if cache write fails
            print(f"Warning: Failed to write cache: {e}")
    
    def clear_cache(self):
        """Remove all cached result files."""
        for file in self.cache_dir.glob("*.json"):
            try:
                file.unlink()
            except Exception:
                pass
    
    def get_stats(self):
        """Return cache statistics."""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total * 100) if total > 0 else 0
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate_percent': round(hit_rate, 1)
        }