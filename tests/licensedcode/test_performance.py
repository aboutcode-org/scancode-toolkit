#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import os
from unittest.case import skip
from commoncode.testcase import FileBasedTesting

from licensedcode import detect


class TestMatchingPerf(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # Comment the skip decorator to run this test
    @skip('Use only for local profiling')
    def test_detect_license_performance_profiling(self):
        # pre-index : we are profiling only the detection, not the indexing
        import licensedcode.detect
        licensedcode.detect.get_index()

        import cProfile as profile
        import pstats
        stats = 'detect_license_performance_profile_log.txt'
        from itertools import repeat

        def detect_lic():
            for location in locations:
                list(detect.detect_license(location, perfect=True))

        tf = ['perf/test1.txt', 'perf/whatever.py', 'perf/udll.cxx']

        locations = [self.get_test_loc(f) for f in tf]
        test_py = 'detect_lic()'
        profile.runctx(test_py, globals(), locals(), stats)
        p = pstats.Stats(stats)
        p.sort_stats('cumulative').print_stats()
        # p.print_stats()


class TestIndexingPerformance(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # Comment the skip decorator to run this test
    @skip('Use only for local profiling')
    def test_build_index_performance_profiling(self):
        # pre-load the JSON : we are profiling only the indexing here
#         from licensedcode.json_rules import load_license_rules
#         rules = load_license_rules()

        import cProfile as profile
        import pstats
        from licensedcode import detect
        stats = 'build_index_performance_profile_log.txt'
        test_py = 'detect.get_license_index()'
        profile.runctx(test_py, globals(), locals(), stats)
        p = pstats.Stats(stats)
        p.sort_stats('time').print_stats(40)
        print()
        print()
        print()
        #p.print_stats()


class TestTokenzingPerformance(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # Comment the skip decorator to run this test
    @skip('Use only for local profiling')
    def test_get_tokens_performance_timing(self):
        from timeit import timeit
        setup='''
from licensedcode.models import get_tokens
from commoncode.fileutils import file_iter
from licensedcode import rules_data_dir
import os
rule_files = [os.path.join(rules_data_dir, f) for f in os.listdir(rules_data_dir) if f.endswith('.RULE')]
'''
        test= '''
for f in rule_files:
    get_tokens(f, template=False)
'''
        print()
        print('WITHOUT CACHE')
        print(timeit(stmt=test, setup=setup,number=10))

        setup_cache='''
from licensedcode.models import get_tokens
from commoncode.fileutils import file_iter
from licensedcode import rules_data_dir
import os
rule_files = [os.path.join(rules_data_dir, f) for f in os.listdir(rules_data_dir) if f.endswith('.RULE')]
# preload cache
for f in rule_files:
    get_tokens(f, template=False, _use_cache=True)
'''

        test_cache = '''
for f in rule_files:
    get_tokens(f, template=False, _use_cache=True)
'''

        print()
        print('WITH CACHE')
        print(timeit(stmt=test_cache, setup=setup_cache,number=10))


    # Comment the skip decorator to run this test
    @skip('Use only for local profiling')
    def test_get_all_rules_performance_timing(self):
        from timeit import timeit
        print()
        print('WITHOUT CACHE')
        print(timeit(stmt='from licensedcode.models import get_all_rules;get_all_rules()',number=10))

        print()
        print('WITH CACHE')
        print(timeit(stmt='from licensedcode.models import get_all_rules;get_all_rules(True)',number=10))
