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

import pytest

from commoncode.fileutils import parent_directory
from commoncode.system import py2
from commoncode.system import py3
from commoncode.testcase import FileBasedTesting

from scancode.cli_test_utils import load_json_result
from scancode.cli_test_utils import run_scan_click

from scancode.resource import Codebase
from scancode.resource import get_path
from scancode.resource import VirtualCodebase


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


    @pytest.mark.xfail(reason='FIXME: a fie for ticket #1422 is needed')
    def test_Codebase_with_only_ignores_should_not_faild_to_create(self):
        from commoncode.fileutils import create_dir
        test_codebase = self.get_temp_dir()
        create_dir(join(test_codebase, 'sccs', 'a'))
        create_dir(join(test_codebase, 'rcs', 'b'))
        Codebase(test_codebase)

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
        codebase.save_resource(codebase.root)
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
            codebase.save_resource(res)

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
                codebase.save_resource(res)

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
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_compute_counts_filtered_all_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_compute_counts_filtered_files(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert expected == results

    def test_compute_counts_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 0)
        assert expected == results

    def test_walk_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)

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
        codebase.save_resource(codebase.root)
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
            codebase.save_resource(res)
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
        codebase.save_resource(codebase.root)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_skip_root_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase._create_resource('some child', parent=codebase.root, is_file=True)
        _c2 = codebase._create_resource('some child2', parent=c1, is_file=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_walk_filtered_with_skip_root_and_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase._create_resource('some child', parent=codebase.root, is_file=True)
        c2 = codebase._create_resource('some child2', parent=c1, is_file=False)
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

    def test_walk_skipped_directories_should_not_be_yielded(self):
        # Resources that we continue past should not be added to the result list
        test_codebase = self.get_test_loc('resource/skip_directories_during_walk')
        codebase = Codebase(test_codebase)
        result = []
        def _ignored(resource, codebase):
            return resource.is_dir and resource.name == 'skip-this-directory'
        for resource in codebase.walk(topdown=True, ignored=_ignored,):
            result.append(resource.name)
        expected = ['skip_directories_during_walk', 'this-should-be-returned']
        assert expected == result

    def test__create_resource_can_add_child_to_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        codebase._create_resource('some child', codebase.root, is_file=True)
        results = list(codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test__create_resource_can_add_child_to_dir(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        codebase._create_resource('some child', codebase.root, is_file=False)
        results = list(codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_get_resource(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        assert not (codebase.root is codebase.get_resource(0))
        assert codebase.root == codebase.get_resource(0)

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
        if py2:
            transcoder = fsencode if on_linux else fsdecode
        if py3:
            transcoder = lambda x: x
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

    def test_compute_counts_when_using_disk_cache(self):
        test_codebase = self.get_test_loc('resource/samples')
        codebase = Codebase(test_codebase, strip_root=True, max_in_memory=-1)
        files_count, dirs_count, size_count = codebase.compute_counts()
        assert files_count == 33
        assert dirs_count == 11
        assert size_count == 0

    def test_low_max_in_memory_does_not_raise_exception_when_ignoring_files(self):

        from commoncode.fileset import is_included

        test_codebase = self.get_test_loc('resource/client')
        codebase = Codebase(test_codebase, strip_root=True, max_in_memory=1)

        # Ignore GIFs, code taken from scancode/plugin_ignore.py
        ignores = {
            '*.gif': 'User ignore: Supplied by --ignore'
        }
        remove_resource = codebase.remove_resource

        for resource in codebase.walk(topdown=True):
            if not is_included(resource.path, excludes=ignores):
                for child in resource.children(codebase):
                    remove_resource(child)
                if not resource.is_root:
                    remove_resource(resource)

        # Walk through the codebase and save each Resource,
        # UnknownResource exception should not be raised
        save_resource = codebase.save_resource
        for resource in codebase.walk(topdown=True):
            save_resource(resource)

    def test_lowest_common_parent_1(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'test1' == lcp.path
        assert 'test1' == lcp.name

    def test_lowest_common_parent_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert '' == lcp.path
        assert 'test1' == lcp.name

    def test_lowest_common_parent_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'test1' == lcp.name

    def test_lowest_common_parent_2(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/zlib')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'zlib' == lcp.path
        assert 'zlib' == lcp.name

    def test_lowest_common_parent_3(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'simple' == lcp.path
        assert 'simple' == lcp.name

    def test_lowest_common_parent_deep(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple/org')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'org/jvnet/glassfish/comms/sipagent' == lcp.path
        assert 'sipagent' == lcp.name

    def test_lowest_common_parent_solo_file(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.path
        assert 'screenshot.png' == lcp.name

    def test_lowest_common_parent_solo_file_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.path
        assert 'screenshot.png' == lcp.name

    def test_lowest_common_parent_solo_file_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.name

    def test_distance(self):
        test_dir = self.get_test_loc('resource/dist')
        codebase = Codebase(test_dir)
        assert 0 == codebase.root.distance(test_dir)

        res = codebase.get_resource(1)
        assert 'JGroups' == res.name
        assert 1 == res.distance(codebase)

        res = codebase.get_resource(10)
        assert 'MANIFEST.MF' == res.name
        assert 3 == res.distance(codebase)

    def test_skip_files_and_subdirs_of_ignored_dirs(self):
        test_dir = self.get_test_loc('resource/ignore')
        codebase = Codebase(test_dir)
        # The `cvs` directory should not be visited
        expected = [
            'ignore',
            'ignore/file1'
        ]
        result = [r.path for r in codebase.walk(topdown=True)]
        self.assertEqual(expected, result)


class TestCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')


    def test_codebase_cache_default(self):
        test_codebase = self.get_test_loc('resource/cache2')
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

        child = codebase._create_resource('child', root, is_file=True)
        child.size = 12
        codebase.save_resource(child)
        child_2 = codebase.get_resource(child.rid)
        assert child == child_2

    def test_codebase_cache_all_in_memory(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=0)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.root == codebase.get_resource(rid)
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)

        assert len(codebase.resource_ids) == len(list(codebase.walk()))

    def test_codebase_cache_all_on_disk(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=-1)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.root == codebase.get_resource(rid)
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert not codebase._exists_in_memory(rid)
                assert codebase._exists_on_disk(rid)

        assert len(codebase.resource_ids) == len(list(codebase.walk()))

    def test_codebase_cache_mixed_two_in_memory(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=2)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.root == codebase.get_resource(rid)
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            elif rid < 2:
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert not codebase._exists_in_memory(rid)
                assert codebase._exists_on_disk(rid)

        assert len(codebase.resource_ids) == len(list(codebase.walk()))


class TestVirtualCodebase(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')


    def test_virtual_codebase_walk_defaults(self):
        test_file = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        codebase = VirtualCodebase(location=test_file)
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

    def test_virtual_codebase_walk_topdown(self):
        test_file = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        codebase = VirtualCodebase(location=test_file)
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

    def test_virtual_codebase_walk_bottomup(self):
        test_file = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        codebase = VirtualCodebase(location=test_file)
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

    def test_virtual_codebase_walk_skip_root_basic(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk(skip_root=True))
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

    def test_virtual_codebase_walk_filtered_with_filtered_root(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)

        results = list(virtual_codebase.walk_filtered())
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

    def test_virtual_codebase_walk_filtered_with_all_filtered(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered())
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_compute_counts_filtered_None(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_None_with_size(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.size = 10
                virtual_codebase.save_resource(res)

        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_None_with_cache(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_all(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_all_with_cache(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_files(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert expected == results

    def test_virtual_codebase_compute_counts_filtered_dirs(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 2228)
        assert expected == results

    def test_virtual_codebase_walk_filtered_dirs(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = list(virtual_codebase.walk_filtered(topdown=True))
        expected = [
              ('abc', True),
              ('et131x.h', True),
                ('that', True),
                ('this', True),
                ('file', True),
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_filtered_skip_root(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
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

    def test_virtual_codebase_walk_filtered_all_skip_root(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_skip_root_single_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_filtered__with_skip_root_and_filtered_single_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_skip_root_single_file_with_children(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        c1 = virtual_codebase._create_resource('some child', parent=virtual_codebase.root, is_file=True)
        _c2 = virtual_codebase._create_resource('some child2', parent=c1, is_file=False)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_with_children(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        c1 = virtual_codebase._create_resource('some child', parent=virtual_codebase.root, is_file=True)
        c2 = virtual_codebase._create_resource('some child2', parent=c1, is_file=False)
        c2.is_filtered = True
        virtual_codebase.save_resource(c2)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [(u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

        c1.is_filtered = True
        virtual_codebase.save_resource(c1)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase__create_resource_can_add_child_to_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._create_resource('some child', virtual_codebase.root, is_file=True)
        results = list(virtual_codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase__create_resource_can_add_child_to_dir(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/resource.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._create_resource('some child', virtual_codebase.root, is_file=False)
        results = list(virtual_codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert expected == [(r.name, r.is_file) for r in results]

    def test_virtual_codebase_get_resource(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/resource.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        assert not (virtual_codebase.root is virtual_codebase.get_resource(0))
        assert virtual_codebase.root == virtual_codebase.get_resource(0)

    def test_virtual_codebase_can_process_minimal_resources_without_info(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/noinfo.json')
        codebase = VirtualCodebase(location=scan_data)
        expected = [
            OrderedDict([
                (u'path', u'NOTICE'),
                (u'type', u'file'),
                (u'copyrights', [
                    OrderedDict([
                        (u'statements', [u'Copyright (c) 2017 nexB Inc. and others.']),
                        (u'holders', [u'nexB Inc. and others.']),
                        (u'authors', []),
                        (u'start_line', 4),
                        (u'end_line', 4)
                    ])
                ]),
                (u'scan_errors', [])
            ])
        ]
        assert expected == [r.to_dict() for r in codebase.walk()]

    def test_virtual_codebase_can_process_minimal_resources_with_only_path(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/only-path.json')
        codebase = VirtualCodebase(location=scan_data)
        expected = [
                OrderedDict([
                (u'path', u'samples'),
                (u'type', u'directory'),
                (u'scan_errors', [])
            ]),
            OrderedDict([
                (u'path', u'samples/NOTICE'),
                (u'type', u'file'),
                (u'scan_errors', [])
            ])
        ]
        assert expected == [r.to_dict() for r in codebase.walk()]


class TestCodebaseLowestCommonParent(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')


    def test_lowest_common_parent_on_virtual_codebase(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/lcp.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        lcp = virtual_codebase.lowest_common_parent()
        assert 'lcp/test1' == lcp.path
        assert 'test1' == lcp.name

    def test_virtual_codebase_has_default_for_plugin_attributes(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/only-path.json')
        VirtualCodebase(location=scan_data)

    def test_lowest_common_parent_1(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'test1' == lcp.path
        assert 'test1' == lcp.name

    def test_lowest_common_parent_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert '' == lcp.path
        assert 'test1' == lcp.name

    def test_lowest_common_parent_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'test1' == lcp.name

    def test_lowest_common_parent_2(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/zlib')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'zlib' == lcp.path
        assert 'zlib' == lcp.name

    def test_lowest_common_parent_3(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'simple' == lcp.path
        assert 'simple' == lcp.name

    def test_lowest_common_parent_deep(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple/org')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'org/jvnet/glassfish/comms/sipagent' == lcp.path
        assert 'sipagent' == lcp.name

    def test_lowest_common_parent_solo_file(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.path
        assert 'screenshot.png' == lcp.name

    def test_lowest_common_parent_solo_file_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.path
        assert 'screenshot.png' == lcp.name

    def test_lowest_common_parent_solo_file_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert 'screenshot.png' == lcp.name


class TestVirtualCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')


    def test_virtual_codebase_cache_default(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        assert virtual_codebase.temp_dir
        assert virtual_codebase.cache_dir
        virtual_codebase.cache_dir
        root = virtual_codebase.root

        cp = virtual_codebase._get_resource_cache_location(root.rid, create=False)
        assert not exists(cp)
        cp = virtual_codebase._get_resource_cache_location(root.rid, create=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))

        child = virtual_codebase._create_resource('child', root, is_file=True)
        child.size = 12
        virtual_codebase.save_resource(child)
        child_2 = virtual_codebase.get_resource(child.rid)
        assert child == child_2

    def test_virtual_codebase_cache_all_in_memory(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=0)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.root == virtual_codebase.get_resource(rid)
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)

        assert len(virtual_codebase.resource_ids) == len(list(virtual_codebase.walk()))

    def test_virtual_codebase_cache_all_on_disk(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=-1)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.root == virtual_codebase.get_resource(rid)
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert not virtual_codebase._exists_in_memory(rid)
                assert virtual_codebase._exists_on_disk(rid)

        assert len(virtual_codebase.resource_ids) == len(list(virtual_codebase.walk()))

    def test_virtual_codebase_cache_mixed_two_in_memory(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=2)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.root == virtual_codebase.get_resource(rid)
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            elif rid < 2:
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert not virtual_codebase._exists_in_memory(rid)
                assert virtual_codebase._exists_on_disk(rid)

        assert len(virtual_codebase.resource_ids) == len(list(virtual_codebase.walk()))


class TestVirtualCodebaseCreationFromCli(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_VirtualCodebase_output_with_from_json_is_same_as_original(self):
        import json

        test_file = self.get_test_loc('resource/virtual_idempotent/codebase.json')
        result_file = self.get_temp_file('json')
        args = ['--from-json', test_file, '--json-pp', result_file]
        run_scan_click(args)
        expected = load_json_result(test_file, remove_file_date=True)
        results = load_json_result(result_file, remove_file_date=True)

        expected.pop('summary', None)
        results.pop('summary', None)

        expected_headers = expected.pop('headers', [])
        results_headers = results.pop('headers', [])

        assert json.dumps(expected, indent=2) == json.dumps(results , indent=2)
        assert len(results_headers) == len(expected_headers) + 1


class TestVirtualCodebaseCreation(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_VirtualCodebase_can_be_created_from_json_file(self):
        test_file = self.get_test_loc('resource/virtual_codebase/from_file.json')
        codebase = VirtualCodebase(test_file)
        results = sorted(r.name for r in codebase.walk())
        expected = ['bar.svg', 'han']
        assert expected == results

    def test_VirtualCodebase_can_be_created_from_json_string(self):
        test_scan = '''
            {
              "scancode_notice": "Generated with ScanCode and provided on an ....",
              "scancode_version": "2.9.7.post137.2e29fe3.dirty.20181120225811",
              "scancode_options": {
                "input": "han/",
                "--json-pp": "-"
              },
              "scan_start": "2018-11-23T123252.191917",
              "files_count": 1,
              "files": [
                {
                  "path": "han",
                  "type": "directory",
                  "scan_errors": []
                },
                {
                  "path": "han/bar.svg",
                  "type": "file",
                  "scan_errors": []
                }
              ]
            }
            '''
        codebase = VirtualCodebase(test_scan)
        results = sorted(r.name for r in codebase.walk())
        expected = ['bar.svg', 'han']
        assert expected == results

    def test_VirtualCodebase_can_be_created_from_dict(self):
        test_scan = {
              "scancode_notice": "Generated with ScanCode and provided on an ....",
              "scancode_version": "2.9.7.post137.2e29fe3.dirty.20181120225811",
              "scancode_options": {
                "input": "han/",
                "--json-pp": "-"
              },
              "scan_start": "2018-11-23T123252.191917",
              "files_count": 1,
              "files": [
                {
                  "path": "han",
                  "type": "directory",
                  "scan_errors": []
                },
                {
                  "path": "han/bar.svg",
                  "type": "file",
                  "scan_errors": []
                }
              ]
            }
        codebase = VirtualCodebase(test_scan)

        results = sorted(r.name for r in codebase.walk())
        expected = ['bar.svg', 'han']
        assert expected == results

    def test_VirtualCodebase_create_from_scan_with_no_root_and_missing_parents(self):
        test_file = self.get_test_loc('resource/virtual_codebase/samples-only-findings.json')
        result_file = self.get_test_loc('resource/virtual_codebase/samples-only-findings-expected.json')
        codebase = VirtualCodebase(test_file)
        expected_scan = load_json_result(result_file, remove_file_date=True)
        results = sorted(r.path for r in codebase.walk())
        expected = sorted(r.get('path') for r in expected_scan['files'])
        assert expected == results

    def test_VirtualCodebase_check_that_already_existing_parent_is_updated_properly(self):
        test_file = self.get_test_loc('resource/virtual_codebase/root-is-not-first-resource.json')
        codebase = VirtualCodebase(test_file)
        results = sorted((r.to_dict() for r in codebase.walk()), key=lambda x: tuple(x.items()))
        expected = [
            OrderedDict([
                (u'path', u'samples'),
                (u'type', u'directory'),
                (u'summary', [u'asd']),
                (u'scan_errors', [])
            ]),
            OrderedDict([
                (u'path', u'samples/NOTICE'),
                (u'type', u'file'),
                (u'summary', []),
                (u'scan_errors', [])
            ])
        ]
        assert expected == results

    def test_VirtualCodebase_create_from_multiple_scans(self):
        test_file_1 = self.get_test_loc('resource/virtual_codebase/combine-1.json')
        test_file_2 = self.get_test_loc('resource/virtual_codebase/combine-2.json')
        vinput = (test_file_1, test_file_2)
        codebase = VirtualCodebase(vinput)
        results = sorted((r.to_dict() for r in codebase.walk()), key=lambda x: tuple(x.items()))
        expected = [
            OrderedDict([(u'path', u'virtual_root'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            OrderedDict([(u'path', u'virtual_root/samples'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            OrderedDict([(u'path', u'virtual_root/samples/NOTICE'), (u'type', u'file'), (u'summary', []), (u'scan_errors', [])]),
            OrderedDict([(u'path', u'virtual_root/thirdparty'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            OrderedDict([(u'path', u'virtual_root/thirdparty/example.zip'), (u'type', u'file'), (u'summary', []), (u'scan_errors', [])])
        ]
        assert expected == results
