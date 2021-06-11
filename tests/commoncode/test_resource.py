#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os

from os.path import dirname
from os.path import exists
from os.path import join

from commoncode.fileutils import parent_directory
from commoncode.testcase import FileBasedTesting
from commoncode.resource import Codebase
from commoncode.resource import get_path
from commoncode.resource import VirtualCodebase
from commoncode.resource import depth_walk


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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_Codebase_do_not_ignore_by_default_older_sccs_and_rcs_dirs(self):
        # See https://github.com/nexB/scancode-toolkit/issues/1422
        from commoncode.fileutils import create_dir
        test_codebase = self.get_temp_dir()
        create_dir(join(test_codebase, 'sccs', 'a'))
        create_dir(join(test_codebase, 'rcs', 'b'))
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(topdown=True, skip_root=True))
        expected = ['rcs', 'b', 'sccs', 'a']
        assert [r.name for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_all_filtered(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)

        results = list(codebase.walk_filtered())
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_compute_counts_filtered_None(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_None_with_size(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.size = 10
                codebase.save_resource(res)

        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert results == expected

    def test_compute_counts_filtered_None_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_all(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_compute_counts_filtered_all_with_cache(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_compute_counts_filtered_files(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_dirs(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 0)
        assert results == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_all_skip_root(self):
        test_codebase = self.get_test_loc('resource/codebase')
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered__with_skip_root_and_filtered_single_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        codebase.save_resource(codebase.root)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase._create_resource('some child', parent=codebase.root, is_file=True)
        _c2 = codebase._create_resource('some child2', parent=c1, is_file=False)
        results = list(codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_skip_root_and_single_file_with_children(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase._create_resource('some child', parent=codebase.root, is_file=True)
        c2 = codebase._create_resource('some child2', parent=c1, is_file=False)
        c2.is_filtered = True
        codebase.save_resource(c2)

        results = list(codebase.walk_filtered(skip_root=True))
        expected = [(u'some child', True)]
        assert [(r.name, r.is_file) for r in results] == expected

        c1.is_filtered = True
        codebase.save_resource(c1)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_dir(self):
        test_codebase = self.get_temp_dir('walk')
        codebase = Codebase(test_codebase, strip_root=True)

        results = list(codebase.walk(skip_root=True))
        expected = [
            ('walk', False)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skipped_directories_should_not_be_yielded(self):
        # Resources that we continue past should not be added to the result list
        test_codebase = self.get_test_loc('resource/skip_directories_during_walk')
        codebase = Codebase(test_codebase)
        result = []

        def _ignored(_resource, _codebase):
            return _resource.is_dir and _resource.name == 'skip-this-directory'

        for resource in codebase.walk(topdown=True, ignored=_ignored,):
            result.append(resource.name)

        expected = ['skip_directories_during_walk', 'this-should-be-returned']
        assert result == expected

    def test__create_resource_can_add_child_to_file(self):
        test_codebase = self.get_test_loc('resource/codebase/et131x.h')
        codebase = Codebase(test_codebase)
        codebase._create_resource('some child', codebase.root, is_file=True)
        results = list(codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test__create_resource_can_add_child_to_dir(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        codebase._create_resource('some child', codebase.root, is_file=False)
        results = list(codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_get_resource(self):
        test_codebase = self.get_temp_dir('resource')
        codebase = Codebase(test_codebase)
        assert not (codebase.root is codebase.get_resource(0))
        assert codebase.get_resource(0) == codebase.root

    def test_get_path(self):
        test_dir = self.get_test_loc('resource/samples')
        locations = []
        for top, dirs, files in os.walk(test_dir):
            for x in dirs:
                locations.append(os.path.join(top, x))
            for x in files:
                locations.append(os.path.join(top, x))

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

        default = sorted(get_path(test_dir, loc) for loc in locations)
        assert default == sorted(expected_default)

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

        skipped = sorted(get_path(test_dir, loc, strip_root=True) for loc in locations)
        assert skipped == sorted(expected_strip_root)

        expected_full_ends = sorted(expected_default)
        full = sorted(get_path(test_dir, loc, full_root=True) for loc in locations)
        for full_loc, ending in zip(full, expected_full_ends):
            assert full_loc.endswith((ending))

        full_skipped = sorted(get_path(test_dir, loc, full_root=True, strip_root=True) for loc in locations)
        assert full_skipped == full

    def test_compute_counts_when_using_disk_cache(self):
        test_codebase = self.get_test_loc('resource/samples')
        codebase = Codebase(test_codebase, strip_root=True, max_in_memory=-1)
        files_count, dirs_count, size_count = codebase.compute_counts()
        assert 33 == files_count
        assert 11 == dirs_count
        assert 0 == size_count

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
        assert lcp.path == 'test1'
        assert lcp.name == 'test1'

    def test_lowest_common_parent_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == ''
        assert lcp.name == 'test1'

    def test_lowest_common_parent_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.name == 'test1'

    def test_lowest_common_parent_2(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/zlib')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'zlib'
        assert lcp.name == 'zlib'

    def test_lowest_common_parent_3(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'simple'
        assert lcp.name == 'simple'

    def test_lowest_common_parent_deep(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple/org')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'org/jvnet/glassfish/comms/sipagent'
        assert lcp.name == 'sipagent'

    def test_lowest_common_parent_solo_file(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'screenshot.png'
        assert lcp.name == 'screenshot.png'

    def test_lowest_common_parent_solo_file_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'screenshot.png'
        assert lcp.name == 'screenshot.png'

    def test_lowest_common_parent_solo_file_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.name == 'screenshot.png'

    def test_distance(self):
        test_dir = self.get_test_loc('resource/dist')
        codebase = Codebase(test_dir)
        assert codebase.root.distance(test_dir) == 0

        res = codebase.get_resource(1)
        assert res.name == 'JGroups'
        assert res.distance(codebase) == 1

        res = codebase.get_resource(10)
        assert res.name == 'MANIFEST.MF'
        assert res.distance(codebase) == 3

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

    def test_depth_negative_fails(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        with self.assertRaises(Exception):
            next(depth_walk(test_codebase, -1))

    def test_depth_walk_with_depth_0(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        results_zero = list(depth_walk(test_codebase, 0))
        results_neg = list(depth_walk(test_codebase, float("inf")))
        result_zero_dirs = [i for j in results_zero for i in j[1]]
        result_zero_files = [i for j in results_zero for i in j[2]]
        result_neg_dirs = [i for j in results_neg for i in j[1]]
        result_neg_files = [i for j in results_neg for i in j[2]]
        self.assertEqual(result_neg_dirs, result_zero_dirs)
        self.assertEqual(result_neg_files, result_zero_files)

    def test_depth_walk_with_depth_1(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        results = list(depth_walk(test_codebase, 1))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = ['level1_file1', 'level1_file2'].sort()
        expected_dirs = ['level1_dir1', 'level1_dir2'].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_depth_walk_with_depth_2(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        results = list(depth_walk(test_codebase, 2))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = ['level1_file1', 'level1_file2', 'level2_file2',
                          'level2_file1', 'level2_file3', 'level2_file4',
                          'level2_file5'].sort()
        expected_dirs = ['level1_dir1', 'level1_dir2', 'level2_dir1',
                         'level2_dir3'].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_depth_walk_with_depth_3(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        results = list(depth_walk(test_codebase, 3))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = ['level1_file1', 'level1_file2', 'level2_file2',
                          'level2_file1', 'level3_file2', 'level3_file1',
                          'level2_file3', 'level2_file4', 'level2_file5',
                          'level3_file4', 'level3_file3'].sort()
        expected_dirs = ['level1_dir1', 'level1_dir2', 'level2_dir1',
                         'level3_dir1', 'level2_dir3'].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_specify_depth_1(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        codebase = Codebase(test_codebase, max_depth=1)
        results = list(codebase.walk())
        expected = [
            ('deeply_nested', False),
                ('level1_dir1', False),
                ('level1_dir2', False),
                ('level1_file1', True),
                ('level1_file2', True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_specify_depth_2(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        codebase = Codebase(test_codebase, max_depth=2)
        results = list(codebase.walk())

        expected = [
            ('deeply_nested', False),
                ('level1_file1', True),
                ('level1_file2', True),
                ('level1_dir1', False),
                    ('level2_dir1', False),
                    ('level2_file1', True),
                    ('level2_file2', True),
                ('level1_dir2', False),
                    ('level2_dir3', False),
                    ('level2_file3', True),
                    ('level2_file4', True),
                    ('level2_file5', True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_specify_depth_3(self):
        test_codebase = self.get_test_loc('resource/deeply_nested')
        codebase = Codebase(test_codebase, max_depth=3)
        results = list(codebase.walk())

        expected = [
            ('deeply_nested', False),
                ('level1_file1', True),
                ('level1_file2', True),
                ('level1_dir1', False),
                    ('level2_file1', True),
                    ('level2_file2', True),
                    ('level2_dir1', False),
                        ('level3_dir1', False),
                        ('level3_file1', True),
                        ('level3_file2', True),
                ('level1_dir2', False),
                    ('level2_file3', True),
                    ('level2_file4', True),
                    ('level2_file5', True),
                    ('level2_dir3', False),
                        ('level3_file3', True),
                        ('level3_file4', True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected


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
        assert child_2 == child

    def test_codebase_cache_all_in_memory(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=0)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.get_resource(rid) == codebase.root
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)

        assert len(list(codebase.walk())) == len(codebase.resource_ids)

    def test_codebase_cache_all_on_disk(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=-1)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.get_resource(rid) == codebase.root
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert not codebase._exists_in_memory(rid)
                assert codebase._exists_on_disk(rid)

        assert len(list(codebase.walk())) == len(codebase.resource_ids)

    def test_codebase_cache_mixed_two_in_memory(self):
        test_codebase = self.get_test_loc('resource/cache2')
        codebase = Codebase(test_codebase, max_in_memory=2)
        for rid in codebase.resource_ids:
            if rid == 0:
                assert codebase.get_resource(rid) == codebase.root
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            elif rid < 2:
                assert codebase._exists_in_memory(rid)
                assert not codebase._exists_on_disk(rid)
            else:
                assert not codebase._exists_in_memory(rid)
                assert codebase._exists_on_disk(rid)

        assert len(list(codebase.walk())) == len(codebase.resource_ids)


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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_get_path_with_strip_root_and_walk_with_skip_root(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/stripped-and-skipped-root.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = [r.get_path(strip_root=True) for r in virtual_codebase.walk(skip_root=True)]
        expected = ['README', 'screenshot.png']
        assert expected == results

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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_all_filtered(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered())
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_compute_counts_filtered_None(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_None_with_size(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.size = 10
                virtual_codebase.save_resource(res)

        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_None_with_cache(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_all(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_all_with_cache(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_files(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_dirs(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 2228)
        assert results == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

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
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_all_skip_root(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/virtual_codebase.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_skip_root_single_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [
            ('et131x.h', True)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered__with_skip_root_and_filtered_single_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_skip_root_single_file_with_children(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        c1 = virtual_codebase._create_resource('some child', parent=virtual_codebase.root, is_file=True)
        _c2 = virtual_codebase._create_resource('some child2', parent=c1, is_file=False)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [
            (u'some child', True), (u'some child2', False)
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_with_children(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        c1 = virtual_codebase._create_resource('some child', parent=virtual_codebase.root, is_file=True)
        c2 = virtual_codebase._create_resource('some child2', parent=c1, is_file=False)
        c2.is_filtered = True
        virtual_codebase.save_resource(c2)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [(u'some child', True)]
        assert [(r.name, r.is_file) for r in results] == expected

        c1.is_filtered = True
        virtual_codebase.save_resource(c1)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase__create_resource_can_add_child_to_file(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/et131x.h.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._create_resource('some child', virtual_codebase.root, is_file=True)
        results = list(virtual_codebase.walk())
        expected = [('et131x.h', True), (u'some child', True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase__create_resource_can_add_child_to_dir(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/resource.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._create_resource('some child', virtual_codebase.root, is_file=False)
        results = list(virtual_codebase.walk())
        expected = [('resource', False), (u'some child', False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_get_resource(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/resource.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        assert not (virtual_codebase.root is virtual_codebase.get_resource(0))
        assert virtual_codebase.get_resource(0) == virtual_codebase.root

    def test_virtual_codebase_can_process_minimal_resources_without_info(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/noinfo.json')
        codebase = VirtualCodebase(location=scan_data)
        expected = [
            dict([
                (u'path', u'NOTICE'),
                (u'type', u'file'),
                (u'copyrights', [
                    dict([
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
        assert [r.to_dict() for r in codebase.walk()] == expected

    def test_virtual_codebase_can_process_minimal_resources_with_only_path(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/only-path.json')
        codebase = VirtualCodebase(location=scan_data)
        expected = [
                dict([
                (u'path', u'samples'),
                (u'type', u'directory'),
                (u'scan_errors', [])
            ]),
            dict([
                (u'path', u'samples/NOTICE'),
                (u'type', u'file'),
                (u'scan_errors', [])
            ])
        ]
        assert [r.to_dict() for r in codebase.walk()] == expected

    def test_VirtualCodebase_account_fingerprint_attribute(self):
        test_file = self.get_test_loc("resource/virtual_codebase/fingerprint_attribute.json")
        codebase = VirtualCodebase(test_file)
        resources_fingerprint = [resource.fingerprint for resource in codebase.walk()]
        assert "e30cf09443e7878dfed3288886e97542" in resources_fingerprint
        assert None in resources_fingerprint
        assert codebase.get_resource(0) == codebase.root
        assert resources_fingerprint.count(None) == 2


class TestCodebaseLowestCommonParent(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_lowest_common_parent_on_virtual_codebase(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/lcp.json')
        virtual_codebase = VirtualCodebase(location=scan_data)
        lcp = virtual_codebase.lowest_common_parent()
        assert lcp.path == 'lcp/test1'
        assert lcp.name == 'test1'

    def test_virtual_codebase_has_default_for_plugin_attributes(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/only-path.json')
        VirtualCodebase(location=scan_data)

    def test_lowest_common_parent_1(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'test1'
        assert lcp.name == 'test1'

    def test_lowest_common_parent_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == ''
        assert lcp.name == 'test1'

    def test_lowest_common_parent_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.name == 'test1'

    def test_lowest_common_parent_2(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/zlib')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'zlib'
        assert lcp.name == 'zlib'

    def test_lowest_common_parent_3(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'simple'
        assert lcp.name == 'simple'

    def test_lowest_common_parent_deep(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/simple/org')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'org/jvnet/glassfish/comms/sipagent'
        assert lcp.name == 'sipagent'

    def test_lowest_common_parent_solo_file(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'screenshot.png'
        assert lcp.name == 'screenshot.png'

    def test_lowest_common_parent_solo_file_strip(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, strip_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == 'screenshot.png'
        assert lcp.name == 'screenshot.png'

    def test_lowest_common_parent_solo_file_full(self):
        test_codebase = self.get_test_loc('resource/lcp/test1/screenshot.png')
        codebase = Codebase(test_codebase, full_root=True)
        lcp = codebase.lowest_common_parent()
        assert lcp.name == 'screenshot.png'


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
        assert child_2 == child

    def test_virtual_codebase_cache_all_in_memory(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=0)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.get_resource(rid) == virtual_codebase.root
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)

        assert len(list(virtual_codebase.walk())) == len(virtual_codebase.resource_ids)

    def test_virtual_codebase_cache_all_on_disk(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=-1)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.get_resource(rid) == virtual_codebase.root
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert not virtual_codebase._exists_in_memory(rid)
                assert virtual_codebase._exists_on_disk(rid)

        assert len(list(virtual_codebase.walk())) == len(virtual_codebase.resource_ids)

    def test_virtual_codebase_cache_mixed_two_in_memory(self):
        scan_data = self.get_test_loc('resource/virtual_codebase/cache2.json')
        virtual_codebase = VirtualCodebase(location=scan_data,
                                           max_in_memory=2)
        for rid in virtual_codebase.resource_ids:
            if rid == 0:
                assert virtual_codebase.get_resource(rid) == virtual_codebase.root
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            elif rid < 2:
                assert virtual_codebase._exists_in_memory(rid)
                assert not virtual_codebase._exists_on_disk(rid)
            else:
                assert not virtual_codebase._exists_in_memory(rid)
                assert virtual_codebase._exists_on_disk(rid)

        assert len(list(virtual_codebase.walk())) == len(virtual_codebase.resource_ids)


class TestVirtualCodebaseCreation(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_VirtualCodebase_can_be_created_from_json_file(self):
        test_file = self.get_test_loc('resource/virtual_codebase/from_file.json')
        codebase = VirtualCodebase(test_file)
        results = sorted(r.name for r in codebase.walk())
        expected = ['bar.svg', 'han']
        assert results == expected

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
        assert results == expected

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
        assert results == expected

    def test_VirtualCodebase_create_from_scan_with_no_root_and_missing_parents(self):
        test_file = self.get_test_loc('resource/virtual_codebase/samples-only-findings.json')
        result_file = self.get_test_loc('resource/virtual_codebase/samples-only-findings-expected.json')
        codebase = VirtualCodebase(test_file)
        expected_scan = json.load(open(result_file))
        results = sorted(r.path for r in codebase.walk())
        expected = sorted(r.get('path') for r in expected_scan['files'])
        assert results == expected

    def test_VirtualCodebase_check_that_already_existing_parent_is_updated_properly(self):
        test_file = self.get_test_loc('resource/virtual_codebase/root-is-not-first-resource.json')
        codebase = VirtualCodebase(test_file)
        results = sorted((r.to_dict() for r in codebase.walk()), key=lambda x: tuple(x.items()))
        expected = [
            dict([
                (u'path', u'samples'),
                (u'type', u'directory'),
                (u'summary', [u'asd']),
                (u'scan_errors', [])
            ]),
            dict([
                (u'path', u'samples/NOTICE'),
                (u'type', u'file'),
                (u'summary', []),
                (u'scan_errors', [])
            ])
        ]
        assert results == expected

    def test_VirtualCodebase_create_from_multiple_scans(self):
        test_file_1 = self.get_test_loc('resource/virtual_codebase/combine-1.json')
        test_file_2 = self.get_test_loc('resource/virtual_codebase/combine-2.json')
        vinput = (test_file_1, test_file_2)
        codebase = VirtualCodebase(vinput)
        results = sorted((r.to_dict() for r in codebase.walk()), key=lambda x: tuple(x.items()))
        expected = [
            dict([(u'path', u'virtual_root'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            dict([(u'path', u'virtual_root/samples'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            dict([(u'path', u'virtual_root/samples/NOTICE'), (u'type', u'file'), (u'summary', []), (u'scan_errors', [])]),
            dict([(u'path', u'virtual_root/thirdparty'), (u'type', u'directory'), (u'summary', []), (u'scan_errors', [])]),
            dict([(u'path', u'virtual_root/thirdparty/example.zip'), (u'type', u'file'), (u'summary', []), (u'scan_errors', [])])
        ]
        assert results == expected

    def test_VirtualCodebase_scanning_full_root(self):
        test_file = self.get_test_loc("resource/virtual_codebase/path_full_root.json")
        codebase = VirtualCodebase(test_file)
        resource = sorted(r for r in codebase.walk())[0]
        assert "/Users/sesser/code/nexb/scancode-toolkit/samples/README" == resource.path
        assert 1 == codebase.compute_counts()[0]

    def test_VirtualCodebase_can_compute_counts_with_null(self):
        # was failing with
        # size_count += child.size
        # TypeError: unsupported operand type(s) for +=: 'int' and 'NoneType'
        test_file = self.get_test_loc("resource/virtual_codebase/node-16-slim.json")
        codebase = VirtualCodebase(test_file)
        codebase.compute_counts()

    def test_VirtualCodebase_can_be_created_with_single_path(self):
        test_file = self.get_test_loc("resource/virtual_codebase/docker-hello-world.json")
        VirtualCodebase(test_file)

    def test_VirtualCodebase_can_be_created_without_RecursionError(self):
        # was failing with RecursionError: maximum recursion depth exceeded
        test_file = self.get_test_loc("resource/virtual_codebase/zephyr-binary.json")
        VirtualCodebase(test_file)


class TestResource(FileBasedTesting):
    test_data_dir = join(dirname(__file__), 'data')

    def test_Resource_extracted_to_extracted_from(self):
        test_file = self.get_test_loc('resource/resource/test-extracted-from-to.json')
        codebase = VirtualCodebase(location=test_file)
        results = []
        for r in codebase.walk(topdown=True):
            extracted_to = r.extracted_to(codebase)
            extracted_from = r.extracted_from(codebase)

            extracted_to_path = ''
            if extracted_to:
                extracted_to_path = extracted_to.path

            extracted_from_path = ''
            if extracted_from:
                extracted_from_path = extracted_from.path
            results.append((r.path, extracted_to_path, extracted_from_path))

        expected = [
            ('test', '', ''),
            ('test/c', '', ''),
            ('test/foo.tar.gz', 'test/foo.tar.gz-extract', ''),
            ('test/foo.tar.gz-extract', '', 'test/foo.tar.gz'),
            ('test/foo.tar.gz-extract/foo', '', 'test/foo.tar.gz'),
            ('test/foo.tar.gz-extract/foo/a', '', 'test/foo.tar.gz'),
            ('test/foo.tar.gz-extract/foo/bar.tar.gz', 'test/foo.tar.gz-extract/foo/bar.tar.gz-extract', 'test/foo.tar.gz'),
            ('test/foo.tar.gz-extract/foo/bar.tar.gz-extract', '', 'test/foo.tar.gz-extract/foo/bar.tar.gz'),
            ('test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar', '', 'test/foo.tar.gz-extract/foo/bar.tar.gz'),
            ('test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar/b', '', 'test/foo.tar.gz-extract/foo/bar.tar.gz')
        ]
        assert results == expected
