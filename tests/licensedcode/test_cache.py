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

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode import models
from licensedcode.match import get_texts
from licensedcode import cache


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class LicenseMatchCacheTest(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]
        return [models.Rule(text_file=os.path.join(base, license_key), licenses=[license_key]) for license_key in test_files]

    def test_cached_match_plain(self):
        idx = index.LicenseIndex(self.get_test_rules('cache/plain'))
        cache_dir = self.get_temp_dir('license_cache')

        query_loc = self.get_test_loc('cache/queryplain.txt')
        result = idx.match(location=query_loc, use_cache=cache_dir)
        assert 1 == len(result)
        match = result[0]
        assert 'cache' not in match.matcher

        # match again to check a cache hit
        result = idx.match(location=query_loc, use_cache=cache_dir)
        assert 1 == len(result)
        cached_match = result[0]
        assert 'cache' in cached_match.matcher
        assert match == cached_match

    def test_cached_match_to_template(self):
        rule = models.Rule(text_file=self.get_test_loc('cache/templates/idx.txt'), licenses=['test'],)
        idx = index.LicenseIndex([rule])
        cache_dir = self.get_temp_dir('license_cache')

        query_loc = self.get_test_loc('cache/templates/query.txt')
        result = idx.match(location=query_loc, use_cache=cache_dir)
        assert 1 == len(result)
        match = result[0]
        assert 'cache' not in match.matcher

        # match again to check a cache hit
        result = idx.match(location=query_loc, use_cache=cache_dir)
        assert 1 == len(result)
        cached_match = result[0]
        assert 'cache' in cached_match.matcher
        assert match == cached_match

    def test_cache_hits_with_different_query_runs_rebase_correctly(self):
        bsd_new = 'Redistribution and use in source and binary forms are permitted'
        bsd_no_mod = 'Redistribution and use in source and binary forms unmodified are permitted'
        bsd_orig = 'Redistribution and use in source and binary forms are permitted by the regents'

        rules = [
            models.Rule(_text=bsd_new, licenses=['bsd_new']),
            models.Rule(_text=bsd_no_mod, licenses=['bsd_no_mod']),
            models.Rule(_text=bsd_orig, licenses=['bsd_orig']),
        ]

        idx = index.LicenseIndex(rules)
        cache_dir = self.get_temp_dir('license_cache')

        querys = 'Redistribution and use in source and binary forms are permitted are'
        match = idx.match(query_string=querys, use_cache=cache_dir)[0]
        assert 'cache' not in match.matcher

        expected = 'Redistribution and use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does not hit cache
        querys = 'are Redistribution and use in source and binary forms are permitted are'
        match = idx.match(query_string=querys, use_cache=cache_dir)[0]
        assert 'cache' not in match.matcher

        expected = 'Redistribution and use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does hit cache
        querys = 'are Redistribution and use in source and binary forms are permitted are'
        match = idx.match(query_string=querys, use_cache=cache_dir)[0]
        assert cache.MATCH_CACHE in match.matcher

        expected = 'Redistribution and use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does hit cache, with unknown
        querys = 'are Redistribution and explicit use in source and binary forms are permitted are'
        match = idx.match(query_string=querys, use_cache=cache_dir)[0]
        assert cache.MATCH_CACHE in match.matcher

        expected = 'Redistribution and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does hit cache, with unknown
        querys = 'Redistribution that and explicit use in source and binary forms are permitted are'
        match = idx.match(query_string=querys, use_cache=cache_dir)[0]
        assert cache.MATCH_CACHE in match.matcher

        expected = 'Redistribution [that] and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does hit cache, with unknown
        querys = ('are Redistribution that and explicit use in source and binary forms are permitted are'
                + '\n' * 10
                + 'are Redistribution and explicit use in source and binary forms are permitted are'
        )
        matches = idx.match(query_string=querys, use_cache=cache_dir)
        assert all(cache.MATCH_CACHE in match.matcher for match in matches)

        match = matches[0]
        expected = 'Redistribution [that] and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        match = matches[1]
        expected = 'Redistribution and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        # does hit cache, with unknown, again
        querys = ('are Redistribution that and explicit use in source and binary forms are permitted are'
                + '\n' * 10
                + 'are Redistribution and explicit use in source and binary forms are permitted are'
        )
        matches = idx.match(query_string=querys, use_cache=cache_dir)
        assert all(cache.MATCH_CACHE in match.matcher for match in matches)

        match = matches[0]
        expected = 'Redistribution [that] and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext

        match = matches[1]
        expected = 'Redistribution [that] and [explicit] use in source and binary forms are permitted'
        qtext, _ = get_texts(match, query_string=querys, idx=idx, width=0)
        assert expected == qtext
