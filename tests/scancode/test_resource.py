#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from os.path import dirname
from os.path import exists
from os.path import join

from commoncode.testcase import FileBasedTesting

from scancode.resource import Codebase
from commoncode.fileutils import parent_directory


class TestCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_codebase_with_use_cache(self):
        test_codebase = self.get_test_loc('cache/package')
        codebase = Codebase(test_codebase, use_cache=True)
        assert codebase.cache_base_dir
        assert codebase.cache_dir
        
        root = codebase.root

        assert ('00', '00000000') == root.cache_keys
        cp = root._get_cached_path(create=False)
        assert not exists(cp)
        cp = root._get_cached_path(create=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))

        assert not root._scans

        scans = OrderedDict(this='that')
        scans_put = root.put_scans(scans)
        assert scans == scans_put
        assert scans == root.get_scans()
        assert not root._scans
        assert exists (root._get_cached_path(create=False))

        scans_put = root.put_scans(scans)
        assert scans == scans_put
        assert not root._scans
        assert scans == root.get_scans()
        assert scans is not root.get_scans()
        assert exists (root._get_cached_path(create=False))

        scans = OrderedDict(food='bar')
        scans_put = root.put_scans(scans, update=False)
        assert scans == scans_put
        assert not root._scans
        assert scans == root.get_scans()
        assert scans is not root.get_scans()

        scans2 = OrderedDict(this='that')
        scans_put = root.put_scans(scans2, update=True)
        expected = OrderedDict(this='that', food='bar')
        assert expected == root.get_scans()
        assert expected is not root.get_scans()

        scans = OrderedDict(food='bar')
        scans_put = root.put_scans(scans, update=False)
        assert scans == scans_put
        assert scans == root.get_scans()
        assert not root._scans
        assert scans is not root.get_scans()
        assert exists (root._get_cached_path(create=False))

    def test_codebase_without_use_cache(self):
        test_codebase = self.get_test_loc('cache/package')
        codebase = Codebase(test_codebase, use_cache=False)
        assert not codebase.cache_dir

        root = codebase.root

        assert ('00', '00000000') == root.cache_keys
        assert root._get_cached_path(create=False) is None

        assert not root._scans

        scans = OrderedDict(this='that')
        scans_put = root.put_scans(scans)
        assert scans == scans_put
        assert scans == root.get_scans()
        assert scans_put is root.get_scans()

        scans_put = root.put_scans(scans)
        assert scans == scans_put
        assert scans_put is root.get_scans()

        scans = OrderedDict(food='bar')
        scans_put = root.put_scans(scans, update=False)
        assert scans == scans_put
        assert scans == root.get_scans()
        assert scans_put is root.get_scans()

        scans2 = OrderedDict(this='that')
        scans_put = root.put_scans(scans2, update=True)
        expected = OrderedDict(this='that', food='bar')
        assert expected == root.get_scans()
        assert expected is not root.get_scans()

        scans = OrderedDict(food='bar')
        scans_put = root.put_scans(scans, update=False)
        assert scans == scans_put
        assert scans == root.get_scans()
        assert scans_put is root.get_scans()
        assert scans is not root.get_scans()
