#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
from os.path import dirname
from os.path import join

from commoncode.hash import binary_chunks
from commoncode.testcase import FileDrivenTesting
from scancode import results_cache


class TestResultsCache(FileDrivenTesting):
    test_data_dir = join(dirname(__file__), 'data')
    test_results_cache = join(test_data_dir, 'results_cache/results')
    test_results_cache_index = "b0e3dd13b9b5980bb1ca7aab89e5490cb136952374489a755947ac004309b035"

    def test_hasher_from_chunks(self):
        test_file_loc = self.get_test_loc('results_cache/package.json')
        chunks = binary_chunks(location=test_file_loc)
        hasher = results_cache.hasher_from_chunks(chunks=chunks)
        expected = "cb6f5a82e473620da4d1aecf82dd4d4fa9ada393a7679b28a42cac86f0a83c92"
        assert hasher.hexdigest() == expected

    def test_compute_results_cache_index(self):
        test_file_loc = self.get_test_loc('results_cache/package.json')
        results_cache_index = results_cache.compute_results_cache_index(location=test_file_loc, filename='package.json')
        assert results_cache_index == self.test_results_cache_index

    def test_get_results_cache_directory_location(self):
        results_cache_directory_location = results_cache.get_results_cache_directory_location(
            results_cache_index=self.test_results_cache_index,
            results_cache_dir=self.test_results_cache,
        )
        expected_results_cache_directory_location = join(
            self.test_results_cache, 'b0/e3/dd13b9b5980bb1ca7aab89e5490cb136952374489a755947ac004309b035'
        )
        assert results_cache_directory_location == expected_results_cache_directory_location

    def test_get_results_cache_file_location(self):
        for plugin_name in ['copyrights', 'emails', 'info', 'licenses', 'packages', 'urls']:
            results_cache_file_location = results_cache.get_results_cache_file_location(
                results_cache_index=self.test_results_cache_index,
                plugin_name=plugin_name,
                results_cache_dir=self.test_results_cache,
            )
            expected_results_cache_file_location = join(
                self.test_results_cache, 'b0/e3/dd13b9b5980bb1ca7aab89e5490cb136952374489a755947ac004309b035', plugin_name
            )
            assert results_cache_file_location == expected_results_cache_file_location

    def test_get_results_cache_data(self):
        for plugin_name in ['copyrights', 'emails', 'info', 'licenses', 'packages', 'urls']:
            results_cache_data = results_cache.get_results_cache_data(
                results_cache_index=self.test_results_cache_index,
                plugin_name=plugin_name,
                results_cache_dir=self.test_results_cache,
            )
            expected_results_cache_file_location = join(
                self.test_results_cache, 'b0/e3/dd13b9b5980bb1ca7aab89e5490cb136952374489a755947ac004309b035', plugin_name
            )
            with open(expected_results_cache_file_location) as f:
                expected_results_cache_data = json.load(f)
            assert results_cache_data == expected_results_cache_data

    def test_update_results_cache_data(self):
        temp_results_cache_directory_location = self.get_temp_dir()
        test_plugin_name = 'test'
        test_data = {
            'name': 'asdf',
            'version': '1.0.0',
        }
        results_cache.update_results_cache_data(
            results_cache_index=self.test_results_cache_index,
            plugin_name=test_plugin_name,
            results=test_data,
            results_cache_dir=temp_results_cache_directory_location,
        )
        results_cache_file_location = join(
            temp_results_cache_directory_location,
            'b0/e3/dd13b9b5980bb1ca7aab89e5490cb136952374489a755947ac004309b035',
            test_plugin_name
        )
        with open(results_cache_file_location) as f:
            results_cache_data = json.load(f)
        assert results_cache_data == test_data
