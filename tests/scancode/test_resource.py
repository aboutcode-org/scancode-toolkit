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

from os.path import dirname
from os.path import exists
from os.path import join

from commoncode.testcase import FileBasedTesting

from scancode.resource import Codebase
from commoncode.fileutils import parent_directory
from scancode.resource import get_path


class TestCodebase(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_walk_defaults(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
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
        codebase = Codebase(test_codebase)
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
        codebase = Codebase(test_codebase)
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
        codebase = Codebase(test_codebase)
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

    def test_walk_filtered_with_filtered_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        results = list(codebase.walk_filtered())
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

    def test_walk_filtered_with_all_filtered(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
        results = list(codebase.walk_filtered())
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_compute_counts_filtered_None(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_None_with_size(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.size = 10

        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert expected == results

    def test_compute_counts_filtered_None_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_all(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_compute_counts_filtered_all_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_compute_counts_filtered_files(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 0)
        assert expected == results

    def test_walk_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True

        results = list(codebase.walk_filtered(topdown=True))
        expected = [
              ('abc', True),
              ('et131x.h', True),
                ('that', True),
                ('this', True),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_filtered_skip_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        results = list(codebase.walk_filtered(skip_root=True))
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

    def test_walk_filtered_all_skip_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_filtered__with_skip_root_and_filtered_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase.create_resource('some child', parent=codebase.root, is_file=True)
        _c2 = codebase.create_resource('some child2', parent=c1, is_file=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_filtered_with_skip_root_and_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase.create_resource('some child', parent=codebase.root, is_file=True)
        c2 = codebase.create_resource('some child2', parent=c1, is_file=False)
        c2.is_filtered = True
        codebase.save_resource(c2)

        results = list(codebase.walk_filtered(skip_root=True))
        expected = [(u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

        c1.is_filtered = True
        codebase.save_resource(c1)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_dir(self):
        test_codebase = self.get_temp_dir('walk')
        codebase = Codebase(test_codebase, strip_root=True)

        results = list(codebase.walk(skip_root=True))
        expected = [
            ('walk', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_create_resource_can_add_child_to_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        codebase.create_resource('some child', codebase.root, is_file=True)
        results = list(codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_create_resource_can_add_child_to_dir(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        codebase.create_resource('some child', codebase.root, is_file=False)
        results = list(codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_get_resource(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        assert codebase.root is codebase.get_resource(0)

    def test_get_path(self):
        import os
        from commoncode.fileutils import fsdecode
        from commoncode.fileutils import fsencode
        from commoncode.system import on_linux

        test_dir = self.get_test_loc('resource/samples')
        locations = []
        for top, dirs, files in os.walk(test_dir):
            for x in dirs:
                locations.append(os.path.join(top, x))
            for x in files:
                locations.append(os.path.join(top, x))
        transcoder = fsencode if on_linux else fsdecode
        locations = [transcoder(p) for p in locations]
        root_location = transcoder(test_dir)

        expected_default = [
            u'samples/JGroups', u'samples/zlib', u'samples/arch',
            u'samples/README', u'samples/screenshot.png',
            u'samples/JGroups/src', u'samples/JGroups/licenses',
            u'samples/JGroups/LICENSE', u'samples/JGroups/EULA',
            u'samples/JGroups/src/GuardedBy.java',
            u'samples/JGroups/src/ImmutableReference.java',
            u'samples/JGroups/src/RouterStub.java',
            u'samples/JGroups/src/S3_PING.java',
            u'samples/JGroups/src/FixedMembershipToken.java',
            u'samples/JGroups/src/RouterStubManager.java',
            u'samples/JGroups/src/RATE_LIMITER.java',
            u'samples/JGroups/licenses/cpl-1.0.txt',
            u'samples/JGroups/licenses/bouncycastle.txt',
            u'samples/JGroups/licenses/lgpl.txt',
            u'samples/JGroups/licenses/apache-2.0.txt',
            u'samples/JGroups/licenses/apache-1.1.txt', u'samples/zlib/dotzlib',
            u'samples/zlib/iostream2', u'samples/zlib/infback9',
            u'samples/zlib/gcc_gvmat64', u'samples/zlib/ada',
            u'samples/zlib/deflate.h', u'samples/zlib/zutil.c',
            u'samples/zlib/zlib.h', u'samples/zlib/deflate.c',
            u'samples/zlib/zutil.h', u'samples/zlib/adler32.c',
            u'samples/zlib/dotzlib/AssemblyInfo.cs',
            u'samples/zlib/dotzlib/LICENSE_1_0.txt',
            u'samples/zlib/dotzlib/readme.txt',
            u'samples/zlib/dotzlib/ChecksumImpl.cs',
            u'samples/zlib/iostream2/zstream_test.cpp',
            u'samples/zlib/iostream2/zstream.h',
            u'samples/zlib/infback9/infback9.c',
            u'samples/zlib/infback9/infback9.h',
            u'samples/zlib/gcc_gvmat64/gvmat64.S', u'samples/zlib/ada/zlib.ads',
            u'samples/arch/zlib.tar.gz']

        default = sorted(get_path(root_location, loc) for loc in locations)
        assert sorted(expected_default) == default

        expected_strip_root = [
            u'JGroups', u'zlib', u'arch', u'README', u'screenshot.png',
            u'JGroups/src', u'JGroups/licenses', u'JGroups/LICENSE',
            u'JGroups/EULA', u'JGroups/src/GuardedBy.java',
            u'JGroups/src/ImmutableReference.java',
            u'JGroups/src/RouterStub.java', u'JGroups/src/S3_PING.java',
            u'JGroups/src/FixedMembershipToken.java',
            u'JGroups/src/RouterStubManager.java',
            u'JGroups/src/RATE_LIMITER.java', u'JGroups/licenses/cpl-1.0.txt',
            u'JGroups/licenses/bouncycastle.txt', u'JGroups/licenses/lgpl.txt',
            u'JGroups/licenses/apache-2.0.txt',
            u'JGroups/licenses/apache-1.1.txt', u'zlib/dotzlib',
            u'zlib/iostream2', u'zlib/infback9', u'zlib/gcc_gvmat64',
            u'zlib/ada', u'zlib/deflate.h', u'zlib/zutil.c', u'zlib/zlib.h',
            u'zlib/deflate.c', u'zlib/zutil.h', u'zlib/adler32.c',
            u'zlib/dotzlib/AssemblyInfo.cs', u'zlib/dotzlib/LICENSE_1_0.txt',
            u'zlib/dotzlib/readme.txt', u'zlib/dotzlib/ChecksumImpl.cs',
            u'zlib/iostream2/zstream_test.cpp', u'zlib/iostream2/zstream.h',
            u'zlib/infback9/infback9.c', u'zlib/infback9/infback9.h',
            u'zlib/gcc_gvmat64/gvmat64.S', u'zlib/ada/zlib.ads',
            u'arch/zlib.tar.gz']

        skipped = sorted(get_path(root_location, loc, strip_root=True) for loc in locations)
        assert sorted(expected_strip_root) == skipped

        expected_full_ends = sorted(expected_default)
        full = sorted(get_path(root_location, loc, full_root=True) for loc in locations)
        for full_loc, ending in zip(full, expected_full_ends):
            assert full_loc.endswith((ending))

        full_skipped = sorted(get_path(root_location, loc, full_root=True, strip_root=True) for loc in locations)
        assert full == full_skipped


class TestCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_codebase_cache_memory(self):
        test_codebase = self.get_test_loc('resource/cache/package')
        codebase = Codebase(test_codebase)
        assert codebase.temp_dir
        assert codebase.cache_dir
        codebase.cache_dir
        root = codebase.root

        cp = codebase._get_resource_cache_location(root.rid, create=False)
        assert not exists(cp)
        cp = codebase._get_resource_cache_location(root.rid, create=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))

        child = codebase.create_resource('child', root, is_file=True)
        child.size = 12
        codebase.save_resource(child)
        child_2 = codebase.get_resource(child.rid)
        assert child == child_2

    def test_codebase_cache_disk(self):
        test_codebase = self.get_test_loc('resource/cache/package')
        codebase = Codebase(test_codebase, max_in_memory=-1)
        assert codebase.temp_dir
        assert codebase.cache_dir
        codebase.cache_dir
        root = codebase.root
        cp = codebase._get_resource_cache_location(root.rid, create=False)
        assert not exists(cp)
        cp = codebase._get_resource_cache_location(root.rid, create=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))
        child = codebase.create_resource('child', root, is_file=True)
        child.size = 12
        codebase.save_resource(child)
        child_2 = codebase.get_resource(child.rid)
        assert child == child_2
