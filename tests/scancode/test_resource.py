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


class TestCodebase(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_walk_defaults(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk())
        expected = [
            ('codebase', False),
              ('abc', True),
              ('et131x.h', True),
              ('dir', False),
                ('that', True),
                ('this', True),
              ('other dir', False),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_topdown(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(topdown=True))
        expected = [
            ('codebase', False),
              ('abc', True),
              ('et131x.h', True),
              ('dir', False),
                ('that', True),
                ('this', True),
              ('other dir', False),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_bottomup(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(topdown=False))
        expected = [
              ('abc', True),
              ('et131x.h', True),
                ('that', True),
                ('this', True),
              ('dir', False),
                ('file', True),
              ('other dir', False),
            ('codebase', False),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_basic(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ('abc', True),
            ('et131x.h', True),
            ('dir', False),
              ('that', True),
              ('this', True),
            ('other dir', False),
              ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_filtered_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        codebase.root.is_filtered = True
        results = list(codebase.walk(skip_filtered=True))
        expected = [
            ('abc', True),
            ('et131x.h', True),
            ('dir', False),
            ('that', True),
            ('this', True),
            ('other dir', False),
            ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_filtered_all(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            res.is_filtered = True
        results = list(codebase.walk(skip_filtered=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_compute_counts_filtered_None(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_None_with_size(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.walk():
            if res.is_file:
                res.size = 10

        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert expected == results

    def test_compute_counts_filtered_None_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=True)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_all(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0,0,0)
        assert expected == results

    def test_compute_counts_filtered_all_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=True)
        for res in codebase.get_resources(None):
            res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0,0,0)
        assert expected == results

    def test_compute_counts_filtered_files(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            if res.is_file:
                res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            if not res.is_file:
                res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 0)
        assert expected == results

    def test_walk_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            if not res.is_file:
                res.is_filtered = True

        results = list(codebase.walk(topdown=True, skip_filtered=True))
        expected = [
              ('abc', True),
              ('et131x.h', True),
                ('that', True),
                ('this', True),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_filtered_skip_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        codebase.root.is_filtered = True
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = [
            ('abc', True),
            ('et131x.h', True),
            ('dir', False),
            ('that', True),
            ('this', True),
            ('other dir', False),
            ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_filtered_all_skip_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        for res in codebase.get_resources(None):
            res.is_filtered = True
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_not_filtered_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_filtered_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)
        codebase.root.is_filtered = True
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = [
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)
        c1 = codebase.root.add_child('some child', is_file=True)
        _c2 = c1.add_child('some child2', is_file=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_skip_filtered_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)

        c1 = codebase.root.add_child('some child', is_file=True)
        c2 = c1.add_child('some child2', is_file=False)
        c2.is_filtered = True
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = [(u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

        c1.is_filtered = True
        results = list(codebase.walk(skip_root=True, skip_filtered=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_dir(self):
        test_codebase = self.get_temp_dir('walk')
        codebase = Codebase(test_codebase, use_cache=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ('walk', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_add_child_can_add_child_to_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, use_cache=False)
        codebase.root.add_child('some child', is_file=True)
        results = list(codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_add_child_can_add_child_to_dir(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase, use_cache=False)
        codebase.root.add_child('some child', is_file=False)
        results = list(codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_get_resource(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase, use_cache=False)
        assert codebase.root is codebase.get_resource(0)

    def test_get_resources(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase, use_cache=False)
        expected = [
            ('codebase', False),
            ('abc', True),
            ('et131x.h', True),
              ('dir', False),
              ('other dir', False),
                ('that', True),
                ('this', True),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in codebase.get_resources(None)]

        expected = [
            ('codebase', False),
            ('abc', True),
              ('dir', False),
                ('this', True),
        ]

        assert expected == [(r.name, r.is_file) for r in codebase.get_resources([0,1,3,6])]

class TestCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_codebase_with_use_cache(self):
        test_codebase = self.get_test_loc('resource/cache/package')
        codebase = Codebase(test_codebase, use_cache=True)
        assert codebase.temp_dir
        assert codebase.cache_dir
        codebase.cache_dir
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
        test_codebase = self.get_test_loc('resource/cache/package')
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
