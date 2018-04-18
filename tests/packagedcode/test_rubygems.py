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

import codecs
import json
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import rubygems


class TestRubyGems(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_gemspec(self, test_loc, expected_loc, regen=False):
        test_loc = self.get_test_loc(test_loc)
        expected_loc = self.get_test_loc(expected_loc)
        results = rubygems.get_spec(test_loc)

        try:
            # fix absolute paths for testing
            rel_path = results['loaded_from']
            rel_path = [p for p in rel_path.split('/') if p]
            rel_path = '/'.join(rel_path[-2:])
            results['loaded_from'] = rel_path
        except:
            pass

        if regen:
            with codecs.open(expected_loc, 'wb', encoding='UTF-8') as ex:
                json.dump(results, ex, indent=2)
        with open(expected_loc) as ex:
            expected = json.load(ex)

        assert sorted(expected.items()) == sorted(results.items())

    def test_rubygems_address_standardization_gemspec(self):
        self.check_gemspec(
            'rubygems/address_standardization.gemspec',
            'rubygems/address_standardization.gemspec.expected.json')

    def test_rubygems_archive_tar_minitar_0_5_2_gem(self):
        self.check_gemspec(
            'rubygems/archive-tar-minitar-0.5.2.gem',
            'rubygems/archive-tar-minitar-0.5.2.gem.expected.json')

    def test_rubygems_arel_gemspec(self):
        self.check_gemspec(
            'rubygems/arel.gemspec',
            'rubygems/arel.gemspec.expected.json')

    def test_rubygems_blankslate_3_1_3_gem(self):
        self.check_gemspec(
            'rubygems/blankslate-3.1.3.gem',
            'rubygems/blankslate-3.1.3.gem.expected.json')

    def test_rubygems_m2r_2_1_0_gem(self):
        self.check_gemspec(
            'rubygems/m2r-2.1.0.gem',
            'rubygems/m2r-2.1.0.gem.expected.json')

    def test_rubygems_mysmallidea_address_standardization_0_4_1_gem(self):
        self.check_gemspec(
            'rubygems/mysmallidea-address_standardization-0.4.1.gem',
            'rubygems/mysmallidea-address_standardization-0.4.1.gem.expected.json')

    def test_rubygems_mysmallidea_mad_mimi_mailer_0_0_9_gem(self):
        self.check_gemspec(
            'rubygems/mysmallidea-mad_mimi_mailer-0.0.9.gem',
            'rubygems/mysmallidea-mad_mimi_mailer-0.0.9.gem.expected.json')

    def test_rubygems_ng_rails_csrf_0_1_0_gem(self):
        self.check_gemspec(
            'rubygems/ng-rails-csrf-0.1.0.gem',
            'rubygems/ng-rails-csrf-0.1.0.gem.expected.json')

    def test_rubygems_small_wonder_0_1_10_gem(self):
        self.check_gemspec(
            'rubygems/small_wonder-0.1.10.gem',
            'rubygems/small_wonder-0.1.10.gem.expected.json')

    def test_rubygems_small_0_2_gem(self):
        self.check_gemspec(
            'rubygems/small-0.2.gem',
            'rubygems/small-0.2.gem.expected.json')

    def test_rubygems_sprockets_vendor_gems_0_1_3_gem(self):
        self.check_gemspec(
            'rubygems/sprockets-vendor_gems-0.1.3.gem',
            'rubygems/sprockets-vendor_gems-0.1.3.gem.expected.json')
