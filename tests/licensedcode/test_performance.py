#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest.case import skip

import pytest

from commoncode.testcase import FileBasedTesting
from licensedcode import cache
from licensedcode import index
from licensedcode import models
from licensedcode_test_utils import create_rule_from_text_file_and_expression

pytestmark = pytest.mark.scanslow

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

        stats_file = 'test_match_license_performance_profiling_on_limited_index.txt'
        locations = [self.get_test_loc('detect/rule_template/query.txt')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_index_with_single_license(self):
        from time import time
        from licensedcode import query

        # pre-index : we are profiling only the detection, not the indexing
        rule_dir = self.get_test_loc('perf/idx/rules')
        rules = models.load_rules(rule_dir)
        idx = index.LicenseIndex(rules)
        location = self.get_test_loc('perf/idx/query.txt')
        querys = open(location, 'rb').read()

        qry = query.build_query(query_string=querys, idx=idx)

        def mini_seq_match(idx):
            list(idx.get_approximate_matches(qry, [], []))

        # qtokens_as_str = array('h', tokens).tostring()
        start = time()
        for _ in range(100):
            mini_seq_match(idx)
        duration = time() - start
        values = ('ScanCode diff:', duration)
        print(*values)
        raise Exception(values)

    @skip('Use only for local profiling')
    def test_approximate_match_to_indexed_template_with_few_tokens_around_gaps_on_limited_index(self):
        rule = create_rule_from_text_file_and_expression(text_file=self.get_test_loc('index/templates/idx.txt'), license_expression='test',)
        idx = index.LicenseIndex([rule])

        stats_file = 'test_approximate_match_to_indexed_template_with_few_tokens_around_gaps_on_limited_index.txt'
        locations = [self.get_test_loc('index/templates/query.txt')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_match_hash(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()

        stats_file = 'test_match_license_performance_profiling_on_full_index_match_hash.txt'
        locations = [self.get_test_loc('perf/cc-by-nc-sa-3.0.SPDX')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_mixed_matching(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_mixed_matching.txt'
        locations = [self.get_test_loc(f) for f in ['perf/test1.txt', 'perf/whatever.py']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_mixed_matching_long(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_mixed_matching_long.txt'
        locations = [self.get_test_loc(f) for f in ['perf/test1.txt', 'perf/whatever.py', 'perf/udll.cxx']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_with_spurious_filtered_seq_matches(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_with_spurious_filtered_seq_matches.txt'
        locations = [self.get_test_loc(f) for f in ['perf/bsd-new_37.txt']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_with_seq_matches(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_with_seq_matches.txt'
        locations = [self.get_test_loc(f) for f in ['perf/seq_query.txt']]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_binary_lkm(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_binary_lkm.txt'
        locations = [self.get_test_loc('perf/eeepc_acpi.ko')]
        self.profile_match(idx, locations, stats_file)

    @skip('Use only for local profiling')
    def test_match_license_performance_profiling_on_full_index_small_binary_lkm2(self):
        # pre-index : we are profiling only the detection, not the indexing
        idx = cache.get_index()
        stats_file = 'test_match_license_performance_profiling_on_full_index_small_binary_lkm2.txt'
        locations = [self.get_test_loc('perf/ath_pci.ko')]
        self.profile_match(idx, locations, stats_file)


class TestIndexingPerformance(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    @skip('Use only for local profiling')
    def test_build_index_performance_profiling(self):
        import cProfile as profile
        import pstats
        stats = 'test_build_index_performance_profiling.txt'
        test_py = 'from licensedcode import cache;cache.populate_cache(force=True)'
        profile.runctx(test_py, globals(), locals(), stats)
        p = pstats.Stats(stats)
        p.sort_stats('time').print_stats(40)
        raise Exception('indexing perfs test')


class TestTokenizingPerformance(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    @skip('Use only for local profiling')
    def test_get_all_rules_performance_timing(self):
        from timeit import timeit
        print()
        print('With Object or namedtuple')
        print(timeit(stmt='from licensedcode.models import get_rules;list(get_rules())', number=10))

    @skip('Use only for local profiling')
    def test_get_all_rules_performance_profiling(self):
        import cProfile as profile
        import pstats
        stats = 'test_get_all_rules_performance_profiling.txt'
        test_py = 'list(models.get_rules())'
        profile.runctx(test_py, globals(), locals(), stats)
        p = pstats.Stats(stats)
        p.sort_stats('time').print_stats(40)
        raise Exception('get_all_rules perfs test')
