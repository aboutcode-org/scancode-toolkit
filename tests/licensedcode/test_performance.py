#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from unittest.case import skip

from commoncode.testcase import FileBasedTesting

from licensedcode import cache
from licensedcode import index
from licensedcode import models

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Instructions: Comment out the skip decorators to run a test. Do not commit without a skip


class TestMatchingPerf(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def profile_match(self, idx, locations, stats_file, top=50):
        import cProfile as profile
        import pstats

        def detect_lic():
            for location in locations:
                list(idx.match(location))

        test_py = 'detect_lic()'
        profile.runctx(test_py, globals(), locals(), stats_file)
        p = pstats.Stats(stats_file)
        p.sort_stats('time').print_stats(top)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_limited_index(self):
        # pre-index : we are profiling only the detection, not the indexing
        rule_dir = self.get_test_loc('detect/rule_template/rules')
        rules = models.load_rules(rule_dir)
        idx = index.LicenseIndex(rules)

        stats_file = 'license_match_limited_index_profile_log.txt'
        locations = [self.get_test_loc('detect/rule_template/query.txt')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_approximate_match_to_indexed_template_with_few_tokens_around_gaps_on_limited_index(self):
        rule = models.Rule(text_file=self.get_test_loc('index/templates/idx.txt'), licenses=['test'],)
        idx = index.LicenseIndex([rule])

        stats_file = 'license_approx_match_limited_index_profile_log.txt'
        locations = [self.get_test_loc('index/templates/query.txt')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_match_hash(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()

        stats_file = 'license_match_chunk_full_index_profile_log.txt'
        locations = [self.get_test_loc('perf/cc-by-nc-sa-3.0.SPDX')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_mixed_matching(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'license_match_mixed_matching_full_index_profile_log1.txt'
        locations = [self.get_test_loc(f) for f in ['perf/test1.txt', 'perf/whatever.py']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_mixed_matching_long(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'license_match_mixed_matching_full_index_profile_log2.txt'
        locations = [self.get_test_loc(f) for f in ['perf/test1.txt', 'perf/whatever.py', 'perf/udll.cxx']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_with_spurious_filtered_seq_matches(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'license_match_mixed_matching_full_index_profile_filtered_seq_matches_log.txt'
        locations = [self.get_test_loc(f) for f in ['perf/bsd-new_37.txt']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_binary_lkm(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'license_match_full_index_profile_log.txt'
        locations = [self.get_test_loc('perf/eeepc_acpi.ko')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_small_binary_lkm2(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'license_match_full_index_profile_log.txt'
        locations = [self.get_test_loc('perf/ath_pci.ko')]
        self.profile_match(idx, locations, stats_file)


class TestIndexingPerformance(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    @skip('Use only for local profiling')
    def test_build_index_performance_profiling(self):
        import cProfile as profile
        import pstats
        stats = 'build_index_performance_profile_log.txt'
        test_py = 'cache.get_index()'
        profile.runctx(test_py, globals(), locals(), stats)
        p = pstats.Stats(stats)
        p.sort_stats('time').print_stats(40)


class TestTokenizingPerformance(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    @skip('Use only for local profiling')
    def test_get_all_rules_performance_timing(self):
        from timeit import timeit
        print()
        print('With Object or namedtuple')
        print(timeit(stmt='from licensedcode.models import get_all_rules;get_all_rules()', number=10))
