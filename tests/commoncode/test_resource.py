#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
from os.path import dirname
from os.path import exists
from os.path import join

import attr

from commoncode.fileutils import parent_directory
from commoncode.resource import Codebase
from commoncode.resource import Resource
from commoncode.resource import VirtualCodebase
from commoncode.resource import depth_walk
from commoncode.testcase import FileBasedTesting
from commoncode.testcase import check_against_expected_json_file


class TestCodebase(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_walk_defaults(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk())
        expected = [
            ("codebase", False),
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_Codebase_do_not_ignore_by_default_older_sccs_and_rcs_dirs(self):
        # See https://github.com/nexB/scancode-toolkit/issues/1422
        from commoncode.fileutils import create_dir

        test_codebase = self.get_temp_dir()
        create_dir(join(test_codebase, "sccs", "a"))
        create_dir(join(test_codebase, "rcs", "b"))
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(topdown=True, skip_root=True))
        expected = ["rcs", "b", "sccs", "a"]
        assert [r.name for r in results] == expected

    def test_walk_topdown(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(topdown=True))
        expected = [
            ("codebase", False),
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_bottomup(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(topdown=False))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("that", True),
            ("this", True),
            ("dir", False),
            ("file", True),
            ("other dir", False),
            ("codebase", False),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_basic(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(skip_root=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_filtered_root(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        codebase.save_resource(codebase.root)
        results = list(codebase.walk_filtered())
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_all_filtered(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)

        results = list(codebase.walk_filtered())
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_compute_counts_filtered_None(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_None_with_size(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.size = 10
                codebase.save_resource(res)

        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert results == expected

    def test_compute_counts_filtered_None_with_cache(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_all(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_compute_counts_filtered_all_with_cache(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_compute_counts_filtered_files(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert results == expected

    def test_compute_counts_filtered_dirs(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)
        results = codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 0)
        assert results == expected

    def test_walk_filtered_dirs(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                codebase.save_resource(res)

        results = list(codebase.walk_filtered(topdown=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("that", True),
            ("this", True),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_skip_root(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        codebase.save_resource(codebase.root)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_all_skip_root(self):
        test_codebase = self.get_test_loc("resource/codebase")
        codebase = Codebase(test_codebase)
        for res in codebase.walk():
            res.is_filtered = True
            codebase.save_resource(res)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_file(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered__with_skip_root_and_filtered_single_file(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase)
        codebase.root.is_filtered = True
        codebase.save_resource(codebase.root)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_file_with_children(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase, strip_root=True)
        root = codebase.root

        c1 = codebase._get_or_create_resource("child1", parent=root, is_file=True)
        codebase._get_or_create_resource("child2", parent=c1, is_file=False)

        results = list(codebase.walk(skip_root=True))
        expected = [("et131x.h", True), ("child1", True), ("child2", False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_filtered_with_skip_root_and_single_file_with_children(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase, strip_root=True)

        c1 = codebase._get_or_create_resource("some child", parent=codebase.root, is_file=True)
        c2 = codebase._get_or_create_resource("some child2", parent=c1, is_file=False)
        c2.is_filtered = True
        codebase.save_resource(c2)

        results = list(codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True), ("some child", True)]
        assert [(r.name, r.is_file) for r in results] == expected

        c1.is_filtered = True
        codebase.save_resource(c1)
        results = list(codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skip_root_single_dir(self):
        test_codebase = self.get_temp_dir("walk")
        codebase = Codebase(test_codebase, strip_root=True)

        results = list(codebase.walk(skip_root=True))
        expected = [("walk", False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_walk_skipped_directories_should_not_be_yielded(self):
        # Resources that we continue past should not be added to the result list
        test_codebase = self.get_test_loc("resource/skip_directories_during_walk")
        cdbs = Codebase(test_codebase)

        def _ignored(resource, codebase):
            return resource.is_dir and resource.name == "skip-this-directory"

        result = [
            res.name
            for res in cdbs.walk(
                topdown=True,
                ignored=_ignored,
            )
        ]

        expected = ["skip_directories_during_walk", "this-should-be-returned"]
        assert result == expected

    def test__create_resource_can_add_child_to_file(self):
        test_codebase = self.get_test_loc("resource/codebase/et131x.h")
        codebase = Codebase(test_codebase)
        codebase._get_or_create_resource("some child", codebase.root, is_file=True)
        results = list(codebase.walk())
        expected = [("et131x.h", True), ("some child", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test__create_resource_can_add_child_to_dir(self):
        test_codebase = self.get_temp_dir("resource")
        codebase = Codebase(test_codebase)
        codebase._get_or_create_resource("some child", codebase.root, is_file=False)
        results = list(codebase.walk())
        expected = [("resource", False), ("some child", False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_get_resource_for_single_resource_codebase(self):
        test_codebase = self.get_temp_dir("resource")
        codebase = Codebase(test_codebase)
        assert not (codebase.root is codebase.get_resource("resource"))
        assert codebase.get_resource("resource") == codebase.root

    def test_get_resource_for_multiple_resource_codebase(self):
        test_codebase = self.get_temp_dir("resource")
        for name in ("a", "b", "c"):
            with open(os.path.join(test_codebase, name), "w") as o:
                o.write("\n")

        codebase = Codebase(test_codebase)
        assert codebase.get_resource("resource/a").path == "resource/a"
        assert codebase.get_resource("/resource/c").path == "resource/c"
        assert codebase.get_resource("resource/dsasda/../b/").path == "resource/b"

    def test_Resource_build_path(self):
        test_dir = self.get_test_loc("resource/samples")
        locations = []
        for top, dirs, files in os.walk(test_dir):
            for x in dirs:
                locations.append(os.path.join(top, x))
            for x in files:
                locations.append(os.path.join(top, x))

        codebase = Codebase(location=test_dir)
        resources_no_root = list(codebase.walk(skip_root=True))

        expected_default = [
            "samples/JGroups",
            "samples/zlib",
            "samples/arch",
            "samples/README",
            "samples/screenshot.png",
            "samples/JGroups/src",
            "samples/JGroups/licenses",
            "samples/JGroups/LICENSE",
            "samples/JGroups/EULA",
            "samples/JGroups/src/GuardedBy.java",
            "samples/JGroups/src/ImmutableReference.java",
            "samples/JGroups/src/RouterStub.java",
            "samples/JGroups/src/S3_PING.java",
            "samples/JGroups/src/FixedMembershipToken.java",
            "samples/JGroups/src/RouterStubManager.java",
            "samples/JGroups/src/RATE_LIMITER.java",
            "samples/JGroups/licenses/cpl-1.0.txt",
            "samples/JGroups/licenses/bouncycastle.txt",
            "samples/JGroups/licenses/lgpl.txt",
            "samples/JGroups/licenses/apache-2.0.txt",
            "samples/JGroups/licenses/apache-1.1.txt",
            "samples/zlib/dotzlib",
            "samples/zlib/iostream2",
            "samples/zlib/infback9",
            "samples/zlib/gcc_gvmat64",
            "samples/zlib/ada",
            "samples/zlib/deflate.h",
            "samples/zlib/zutil.c",
            "samples/zlib/zlib.h",
            "samples/zlib/deflate.c",
            "samples/zlib/zutil.h",
            "samples/zlib/adler32.c",
            "samples/zlib/dotzlib/AssemblyInfo.cs",
            "samples/zlib/dotzlib/LICENSE_1_0.txt",
            "samples/zlib/dotzlib/readme.txt",
            "samples/zlib/dotzlib/ChecksumImpl.cs",
            "samples/zlib/iostream2/zstream_test.cpp",
            "samples/zlib/iostream2/zstream.h",
            "samples/zlib/infback9/infback9.c",
            "samples/zlib/infback9/infback9.h",
            "samples/zlib/gcc_gvmat64/gvmat64.S",
            "samples/zlib/ada/zlib.ads",
            "samples/arch/zlib.tar.gz",
        ]

        default = sorted(
            Resource.build_path(root_location=test_dir, location=loc) for loc in locations
        )
        assert default == sorted(expected_default)

        expected_strip_root = [
            "JGroups",
            "zlib",
            "arch",
            "README",
            "screenshot.png",
            "JGroups/src",
            "JGroups/licenses",
            "JGroups/LICENSE",
            "JGroups/EULA",
            "JGroups/src/GuardedBy.java",
            "JGroups/src/ImmutableReference.java",
            "JGroups/src/RouterStub.java",
            "JGroups/src/S3_PING.java",
            "JGroups/src/FixedMembershipToken.java",
            "JGroups/src/RouterStubManager.java",
            "JGroups/src/RATE_LIMITER.java",
            "JGroups/licenses/cpl-1.0.txt",
            "JGroups/licenses/bouncycastle.txt",
            "JGroups/licenses/lgpl.txt",
            "JGroups/licenses/apache-2.0.txt",
            "JGroups/licenses/apache-1.1.txt",
            "zlib/dotzlib",
            "zlib/iostream2",
            "zlib/infback9",
            "zlib/gcc_gvmat64",
            "zlib/ada",
            "zlib/deflate.h",
            "zlib/zutil.c",
            "zlib/zlib.h",
            "zlib/deflate.c",
            "zlib/zutil.h",
            "zlib/adler32.c",
            "zlib/dotzlib/AssemblyInfo.cs",
            "zlib/dotzlib/LICENSE_1_0.txt",
            "zlib/dotzlib/readme.txt",
            "zlib/dotzlib/ChecksumImpl.cs",
            "zlib/iostream2/zstream_test.cpp",
            "zlib/iostream2/zstream.h",
            "zlib/infback9/infback9.c",
            "zlib/infback9/infback9.h",
            "zlib/gcc_gvmat64/gvmat64.S",
            "zlib/ada/zlib.ads",
            "arch/zlib.tar.gz",
        ]
        stripped = sorted(r.strip_root_path for r in resources_no_root)
        assert stripped == sorted(expected_strip_root)

        expected_full_ends = sorted(expected_default)
        full = sorted(r.full_root_path for r in resources_no_root)
        for full_loc, ending in zip(full, expected_full_ends):
            assert full_loc.endswith((ending))

    def test_compute_counts_when_using_disk_cache(self):
        test_codebase = self.get_test_loc("resource/samples")
        codebase = Codebase(test_codebase, strip_root=True, max_in_memory=-1)
        files_count, dirs_count, size_count = codebase.compute_counts()
        assert 33 == files_count
        assert 11 == dirs_count
        assert 0 == size_count

    def test_distance(self):
        test_dir = self.get_test_loc("resource/dist")
        codebase = Codebase(test_dir)
        assert codebase.root.distance(test_dir) == 0

        res = codebase.get_resource("dist/JGroups")
        assert res.name == "JGroups"
        assert res.distance(codebase) == 1

        res = codebase.get_resource("dist/simple/META-INF/MANIFEST.MF")
        assert res.name == "MANIFEST.MF"
        assert res.full_root_path.endswith("resource/dist/simple/META-INF/MANIFEST.MF")
        assert res.distance(codebase) == 3

    def test_skip_files_and_subdirs_of_ignored_dirs(self):
        test_dir = self.get_test_loc("resource/ignore")
        codebase = Codebase(test_dir)
        # The `cvs` directory should not be visited
        expected = ["ignore", "ignore/file1"]
        result = [r.path for r in codebase.walk(topdown=True)]
        self.assertEqual(expected, result)

    def test_depth_negative_fails(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        with self.assertRaises(Exception):
            next(depth_walk(test_codebase, -1))

    def test_depth_walk_with_depth_0(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        results_zero = list(depth_walk(test_codebase, 0))
        results_neg = list(depth_walk(test_codebase, float("inf")))
        result_zero_dirs = [i for j in results_zero for i in j[1]]
        result_zero_files = [i for j in results_zero for i in j[2]]
        result_neg_dirs = [i for j in results_neg for i in j[1]]
        result_neg_files = [i for j in results_neg for i in j[2]]
        self.assertEqual(result_neg_dirs, result_zero_dirs)
        self.assertEqual(result_neg_files, result_zero_files)

    def test_depth_walk_with_depth_1(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        results = list(depth_walk(test_codebase, 1))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = ["level1_file1", "level1_file2"].sort()
        expected_dirs = ["level1_dir1", "level1_dir2"].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_depth_walk_with_depth_2(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        results = list(depth_walk(test_codebase, 2))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = [
            "level1_file1",
            "level1_file2",
            "level2_file2",
            "level2_file1",
            "level2_file3",
            "level2_file4",
            "level2_file5",
        ].sort()
        expected_dirs = ["level1_dir1", "level1_dir2", "level2_dir1", "level2_dir3"].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_depth_walk_with_depth_3(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        results = list(depth_walk(test_codebase, 3))
        result_dirs = [i for j in results for i in j[1]].sort()
        result_files = [i for j in results for i in j[2]].sort()
        expected_files = [
            "level1_file1",
            "level1_file2",
            "level2_file2",
            "level2_file1",
            "level3_file2",
            "level3_file1",
            "level2_file3",
            "level2_file4",
            "level2_file5",
            "level3_file4",
            "level3_file3",
        ].sort()
        expected_dirs = [
            "level1_dir1",
            "level1_dir2",
            "level2_dir1",
            "level3_dir1",
            "level2_dir3",
        ].sort()
        self.assertEqual(result_dirs, expected_dirs)
        self.assertEqual(result_files, expected_files)

    def test_specify_depth_1(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        codebase = Codebase(test_codebase, max_depth=1)
        results = list(codebase.walk())
        expected = [
            ("deeply_nested", False),
            ("level1_dir1", False),
            ("level1_dir2", False),
            ("level1_file1", True),
            ("level1_file2", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_specify_depth_2(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        codebase = Codebase(test_codebase, max_depth=2)
        results = list(codebase.walk())

        expected = [
            ("deeply_nested", False),
            ("level1_file1", True),
            ("level1_file2", True),
            ("level1_dir1", False),
            ("level2_dir1", False),
            ("level2_file1", True),
            ("level2_file2", True),
            ("level1_dir2", False),
            ("level2_dir3", False),
            ("level2_file3", True),
            ("level2_file4", True),
            ("level2_file5", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_specify_depth_3(self):
        test_codebase = self.get_test_loc("resource/deeply_nested")
        codebase = Codebase(test_codebase, max_depth=3)
        results = list(codebase.walk())

        expected = [
            ("deeply_nested", False),
            ("level1_file1", True),
            ("level1_file2", True),
            ("level1_dir1", False),
            ("level2_file1", True),
            ("level2_file2", True),
            ("level2_dir1", False),
            ("level3_dir1", False),
            ("level3_file1", True),
            ("level3_file2", True),
            ("level1_dir2", False),
            ("level2_file3", True),
            ("level2_file4", True),
            ("level2_file5", True),
            ("level2_dir3", False),
            ("level3_file3", True),
            ("level3_file4", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected


class TestCodebaseWithPath(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_Codebase_with_paths_works(self):
        test_codebase = self.get_test_loc("resource/with_path/codebase")
        paths = ["codebase/other dir/file"]
        codebase = Codebase(location=test_codebase, paths=paths)
        assert not codebase.errors
        results = [r.to_dict() for r in codebase.walk()]
        print(r.path for r in codebase.walk())
        expected_file = self.get_test_loc(
            "resource/with_path/codebase-expected.json",
            must_exist=False,
        )
        check_against_expected_json_file(results, expected_file, regen=False)

    def test_VirtualCodebase_with_paths_works(self):
        test_codebase = self.get_test_loc("resource/with_path/virtual-codebase.json")
        paths = ["codebase/other dir/file"]
        codebase = VirtualCodebase(location=test_codebase, paths=paths)
        assert not codebase.errors
        results = [r.to_dict() for r in codebase.walk()]
        expected_file = self.get_test_loc(
            "resource/with_path/virtual-codebase-expected.json",
            must_exist=False,
        )
        check_against_expected_json_file(results, expected_file, regen=False)

    def test_VirtualCodebase_codebase_attributes_assignment(self):
        test_codebase = self.get_test_loc("resource/with_path/virtual-codebase.json")
        vc = VirtualCodebase(
            location=test_codebase,
            codebase_attributes=dict(packages=attr.ib(default=attr.Factory(list))),
        )
        self.assertNotEqual(vc.attributes.packages, None)
        self.assertEqual(vc.attributes.packages, [])


class TestCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_codebase_cache_default(self):
        test_codebase = self.get_test_loc("resource/cache2")
        codebase = Codebase(test_codebase)

        assert codebase.temp_dir
        assert codebase.cache_dir

        root = codebase.root

        cp = codebase._get_resource_cache_location(root.path, create_dirs=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))

        child = codebase._get_or_create_resource(name="child", parent=root, is_file=True)
        child.size = 12
        codebase.save_resource(child)
        child_2 = codebase.get_resource(path=child.path)
        assert child_2 == child

    def test_codebase_cache_all_in_memory(self):
        test_codebase = self.get_test_loc("resource/cache2")
        codebase = Codebase(test_codebase, max_in_memory=0)
        for path, res in codebase.resources_by_path.items():
            if res is Codebase.CACHED_RESOURCE:
                res = codebase.get_resource(path)
            if res.is_root:
                assert codebase.get_resource(path) == codebase.root == res
                assert codebase._exists_in_memory(path)
                assert not codebase._exists_on_disk(path)
            else:
                assert codebase._exists_in_memory(path)
                assert not codebase._exists_on_disk(path)

        assert (
            len(list(codebase.walk()))
            == len(codebase.resources_by_path)
            == codebase.resources_count
        )

    def test_codebase_cache_all_on_disk(self):
        test_codebase = self.get_test_loc("resource/cache2")
        codebase = Codebase(test_codebase, max_in_memory=-1)
        for path, res in codebase.resources_by_path.items():
            if res is Codebase.CACHED_RESOURCE:
                res = codebase.get_resource(path)
            if res.is_root:
                assert codebase.get_resource(path) == codebase.root == res
                assert codebase._exists_in_memory(path)
                assert not codebase._exists_on_disk(path)
            else:
                assert not codebase._exists_in_memory(path)
                assert codebase._exists_on_disk(path)

        assert (
            len(list(codebase.walk()))
            == len(codebase.resources_by_path)
            == codebase.resources_count
        )

    def test_codebase_cache_mixed_two_in_memory(self):
        test_codebase = self.get_test_loc("resource/cache2")
        codebase = Codebase(test_codebase, max_in_memory=2)
        counter = 0
        for path, res in codebase.resources_by_path.items():
            if res is Codebase.CACHED_RESOURCE:
                res = codebase.get_resource(path)

            if res.is_root:
                assert codebase.get_resource(path) == codebase.root == res
                assert codebase._exists_in_memory(path)
                assert not codebase._exists_on_disk(path)
                counter += 1
            elif counter < 2:
                assert codebase._exists_in_memory(path)
                assert not codebase._exists_on_disk(path)
                counter += 1
            else:
                assert not codebase._exists_in_memory(path)
                assert codebase._exists_on_disk(path)

        assert (
            len(list(codebase.walk()))
            == len(codebase.resources_by_path)
            == codebase.resources_count
        )


class TestVirtualCodebase(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_virtual_codebase_walk_defaults(self):
        test_file = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        codebase = VirtualCodebase(location=test_file)
        results = list(codebase.walk())
        expected = [
            ("codebase", False),
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_topdown(self):
        test_file = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        codebase = VirtualCodebase(location=test_file)
        results = list(codebase.walk(topdown=True))
        expected = [
            ("codebase", False),
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_bottomup(self):
        test_file = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        codebase = VirtualCodebase(location=test_file)
        results = list(codebase.walk(topdown=False))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("that", True),
            ("this", True),
            ("dir", False),
            ("file", True),
            ("other dir", False),
            ("codebase", False),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_skip_root_basic(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_get_path_with_strip_root_and_walk_with_skip_root(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/stripped-and-skipped-root.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = [r.get_path(strip_root=True) for r in virtual_codebase.walk(skip_root=True)]
        expected = ["README", "screenshot.png"]
        assert expected == results

    def test_virtual_codebase_to_list_with_strip_root_and_walk_with_skip_root(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/stripped-and-skipped-root.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.to_list(strip_root=True, skinny=True)
        expected = [{"path": "README", "type": "file"}, {"path": "screenshot.png", "type": "file"}]
        assert expected == results

    def test_virtual_codebase_walk_filtered_with_filtered_root(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)

        results = list(virtual_codebase.walk_filtered())
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_all_filtered(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered())
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_compute_counts_filtered_None(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_None_with_size(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.size = 10
                virtual_codebase.save_resource(res)

        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 50)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_None_with_cache(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 3, 2228)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_all(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_all_with_cache(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 0, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_files(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (0, 3, 0)
        assert results == expected

    def test_virtual_codebase_compute_counts_filtered_dirs(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = virtual_codebase.compute_counts(skip_filtered=True)
        expected = (5, 0, 2228)
        assert results == expected

    def test_virtual_codebase_walk_filtered_dirs(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            if not res.is_file:
                res.is_filtered = True
                virtual_codebase.save_resource(res)
        results = list(virtual_codebase.walk_filtered(topdown=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("that", True),
            ("this", True),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_skip_root(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [
            ("abc", True),
            ("et131x.h", True),
            ("dir", False),
            ("that", True),
            ("this", True),
            ("other dir", False),
            ("file", True),
        ]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_all_skip_root(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/virtual_codebase.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        for res in virtual_codebase.walk():
            res.is_filtered = True
            virtual_codebase.save_resource(res)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_skip_root_single_file(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_not_filtered(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered__with_skip_root_and_filtered_single_file(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase.root.is_filtered = True
        virtual_codebase.save_resource(virtual_codebase.root)
        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = []
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_skip_root_single_file_with_children(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)

        c1 = virtual_codebase._get_or_create_resource(
            "some child",
            parent=virtual_codebase.root,
            is_file=True,
        )
        _c2 = virtual_codebase._get_or_create_resource(
            "some child2",
            parent=c1,
            is_file=False,
        )
        results = list(virtual_codebase.walk(skip_root=True))
        expected = [("et131x.h", True), ("some child", True), ("some child2", False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_walk_filtered_with_skip_root_and_single_file_with_children(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)

        c1 = virtual_codebase._get_or_create_resource(
            "some child",
            parent=virtual_codebase.root,
            is_file=True,
        )

        c2 = virtual_codebase._get_or_create_resource(
            "some child2",
            parent=c1,
            is_file=False,
        )
        c2.is_filtered = True
        c2.save(virtual_codebase)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True), ("some child", True)]
        assert [(r.name, r.is_file) for r in results] == expected

        c1.is_filtered = True
        c1.save(virtual_codebase)

        results = list(virtual_codebase.walk_filtered(skip_root=True))
        expected = [("et131x.h", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase__create_resource_can_add_child_to_file(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/et131x.h.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._get_or_create_resource(
            "some child",
            virtual_codebase.root,
            is_file=True,
        )
        results = list(virtual_codebase.walk())
        expected = [("et131x.h", True), ("some child", True)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase__create_resource_can_add_child_to_dir(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/resource.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        virtual_codebase._get_or_create_resource(
            "some child",
            virtual_codebase.root,
            is_file=False,
        )
        results = list(virtual_codebase.walk())
        expected = [("resource", False), ("some child", False)]
        assert [(r.name, r.is_file) for r in results] == expected

    def test_virtual_codebase_get_resource(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/resource.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        assert not (virtual_codebase.root is virtual_codebase.get_resource("resource"))
        assert virtual_codebase.get_resource("resource") == virtual_codebase.root

    def test_virtual_codebase_can_process_minimal_resources_without_info(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/noinfo.json")
        codebase = VirtualCodebase(location=scan_data)
        expected = [
            {
                "path": "NOTICE",
                "type": "file",
                "copyrights": [
                    {
                        "statements": ["Copyright (c) 2017 nexB Inc. and others."],
                        "holders": ["nexB Inc. and others."],
                        "authors": [],
                        "start_line": 4,
                        "end_line": 4,
                    }
                ],
                "scan_errors": [],
            }
        ]
        assert [r.to_dict() for r in codebase.walk()] == expected

    def test_virtual_codebase_can_process_minimal_resources_with_only_path(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/only-path.json")
        codebase = VirtualCodebase(location=scan_data)
        expected = [
            {"path": "samples", "type": "directory", "scan_errors": []},
            {"path": "samples/NOTICE", "type": "file", "scan_errors": []},
        ]
        assert [r.to_dict() for r in codebase.walk()] == expected

    def test_VirtualCodebase_account_fingerprint_attribute(self):
        test_file = self.get_test_loc("resource/virtual_codebase/fingerprint_attribute.json")
        codebase = VirtualCodebase(test_file)
        resources_fingerprint = [resource.fingerprint for resource in codebase.walk()]
        assert "e30cf09443e7878dfed3288886e97542" in resources_fingerprint
        assert None in resources_fingerprint
        assert codebase.get_resource("apache_to_all_notable_lic_new") == codebase.root
        assert resources_fingerprint.count(None) == 2

    def test_VirtualCodebase_works_with_mapping_backed_codebase(self):
        test_file = self.get_test_loc("resource/virtual_codebase/license-scan.json")
        codebase = VirtualCodebase(test_file)
        resource = codebase.get_resource("scan-ref/license-notice.txt")
        assert resource
        assert len(resource.license_expressions) == 1


class TestCodebaseLowestCommonParent(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_lowest_common_parent_on_virtual_codebase(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/lcp.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        lcp = virtual_codebase.lowest_common_parent()
        assert lcp.path == "lcp/test1"
        assert lcp.name == "test1"

    def test_virtual_codebase_has_default_for_plugin_attributes(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/only-path.json")
        VirtualCodebase(location=scan_data)

    def test_lowest_common_parent_strip(self):
        test_codebase = self.get_test_loc("resource/lcp/test1")
        codebase = Codebase(test_codebase)
        assert len(list(codebase.walk())) == 75
        lcp = codebase.lowest_common_parent()
        assert lcp.path == "test1"
        assert lcp.name == "test1"
        assert lcp.strip_root_path == ""
        assert lcp.full_root_path.endswith("resource/lcp/test1")

    def test_lowest_common_parent_2(self):
        test_codebase = self.get_test_loc("resource/lcp/test1/zlib")
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == "zlib"
        assert lcp.name == "zlib"
        assert lcp.strip_root_path == ""
        assert lcp.full_root_path.endswith("resource/lcp/test1/zlib")

    def test_lowest_common_parent_3(self):
        test_codebase = self.get_test_loc("resource/lcp/test1/simple")
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == "simple"
        assert lcp.name == "simple"
        assert lcp.strip_root_path == ""

    def test_lowest_common_parent_deep(self):
        test_codebase = self.get_test_loc("resource/lcp/test1/simple/org")
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == "org/jvnet/glassfish/comms/sipagent"
        assert lcp.name == "sipagent"
        assert lcp.strip_root_path == "jvnet/glassfish/comms/sipagent"
        assert lcp.full_root_path.endswith(
            "resource/lcp/test1/simple/org/jvnet/glassfish/comms/sipagent"
        )

    def test_lowest_common_parent_solo_file(self):
        test_codebase = self.get_test_loc("resource/lcp/test1/screenshot.png")
        codebase = Codebase(test_codebase)
        lcp = codebase.lowest_common_parent()
        assert lcp.path == "screenshot.png"
        assert lcp.name == "screenshot.png"
        assert lcp.strip_root_path == ""
        assert lcp.full_root_path.endswith("resource/lcp/test1/screenshot.png")


class TestVirtualCodebaseCache(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_virtual_codebase_cache_default(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/codebase-for-cache-tests.json")
        virtual_codebase = VirtualCodebase(location=scan_data)
        assert virtual_codebase.temp_dir
        assert virtual_codebase.cache_dir
        virtual_codebase.cache_dir
        root = virtual_codebase.root

        cp = virtual_codebase._get_resource_cache_location(root.path, create_dirs=False)
        assert not exists(cp)

        cp = virtual_codebase._get_resource_cache_location(root.path, create_dirs=True)
        assert not exists(cp)
        assert exists(parent_directory(cp))

        child = virtual_codebase._get_or_create_resource("child", root, is_file=True)
        child.size = 12
        virtual_codebase.save_resource(child)
        child_2 = virtual_codebase.get_resource(child.path)
        assert child_2 == child

    def test_virtual_codebase_cache_all_in_memory(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/codebase-for-cache-tests.json")
        virtual_codebase = VirtualCodebase(location=scan_data, max_in_memory=0)
        for path, res in virtual_codebase.resources_by_path.items():
            assert res != Codebase.CACHED_RESOURCE
            if res.is_root:
                assert virtual_codebase.get_resource(path).to_dict(
                    with_info=True
                ) == virtual_codebase.root.to_dict(with_info=True)
                assert virtual_codebase._exists_in_memory(path)
                assert not virtual_codebase._exists_on_disk(path)
            else:
                assert virtual_codebase._exists_in_memory(path)
                assert not virtual_codebase._exists_on_disk(path)

        assert (
            len(list(virtual_codebase.walk()))
            == len(virtual_codebase.resources_by_path)
            == virtual_codebase.resources_count
        )

    def test_virtual_codebase_cache_all_on_disk(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/codebase-for-cache-tests.json")
        virtual_codebase = VirtualCodebase(location=scan_data, max_in_memory=-1)
        for path, res in virtual_codebase.resources_by_path.items():
            if res != Codebase.CACHED_RESOURCE:
                assert res.is_root
            else:
                res = virtual_codebase.get_resource(path)

            if res.is_root:
                assert virtual_codebase.get_resource(path) == virtual_codebase.root
                assert virtual_codebase._exists_in_memory(path)
                assert not virtual_codebase._exists_on_disk(path)
            else:
                assert not virtual_codebase._exists_in_memory(path)
                assert virtual_codebase._exists_on_disk(path)

        assert (
            len(list(virtual_codebase.walk()))
            == len(virtual_codebase.resources_by_path)
            == virtual_codebase.resources_count
        )

    def test_virtual_codebase_cache_mixed_two_in_memory(self):
        scan_data = self.get_test_loc("resource/virtual_codebase/codebase-for-cache-tests.json")
        virtual_codebase = VirtualCodebase(location=scan_data, max_in_memory=2)
        counter = 0

        for path, res in virtual_codebase.resources_by_path.items():
            if res is Codebase.CACHED_RESOURCE:
                res = virtual_codebase.get_resource(path)

            if res.is_root:
                assert (
                    virtual_codebase.get_resource(path).to_dict() == virtual_codebase.root.to_dict()
                )
                assert virtual_codebase._exists_in_memory(path)
                assert not virtual_codebase._exists_on_disk(path)
                counter += 1

            elif counter < 2:
                assert virtual_codebase._exists_in_memory(path)
                assert not virtual_codebase._exists_on_disk(path)
                counter += 1

            else:
                assert not virtual_codebase._exists_in_memory(path)
                assert virtual_codebase._exists_on_disk(path)

        assert (
            len(list(virtual_codebase.walk()))
            == len(virtual_codebase.resources_by_path)
            == virtual_codebase.resources_count
        )


class TestVirtualCodebaseCreation(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_VirtualCodebase_can_be_created_from_json_file(self):
        test_file = self.get_test_loc("resource/virtual_codebase/from_file.json")
        codebase = VirtualCodebase(test_file)
        results = sorted(r.name for r in codebase.walk())
        expected = ["bar.svg", "han"]
        assert results == expected

    def test_VirtualCodebase_can_be_created_from_json_string(self):
        test_scan = """
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
            """
        codebase = VirtualCodebase(test_scan)
        results = sorted(r.name for r in codebase.walk())
        expected = ["bar.svg", "han"]
        assert results == expected

    def test_VirtualCodebase_can_be_created_from_dict(self):
        test_scan = {
            "scancode_notice": "Generated with ScanCode and provided on an ....",
            "scancode_version": "2.9.7.post137.2e29fe3.dirty.20181120225811",
            "scancode_options": {"input": "han/", "--json-pp": "-"},
            "scan_start": "2018-11-23T123252.191917",
            "files_count": 1,
            "files": [
                {"path": "han", "type": "directory", "scan_errors": []},
                {"path": "han/bar.svg", "type": "file", "scan_errors": []},
            ],
        }
        codebase = VirtualCodebase(test_scan)

        results = sorted(r.name for r in codebase.walk())
        expected = ["bar.svg", "han"]
        assert results == expected

    def test_VirtualCodebase_create_from_scan_with_no_root_and_missing_parents(self):
        test_file = self.get_test_loc("resource/virtual_codebase/samples-only-findings.json")
        result_file = self.get_test_loc(
            "resource/virtual_codebase/samples-only-findings-expected.json"
        )
        codebase = VirtualCodebase(test_file)
        expected_scan = json.load(open(result_file))
        results = sorted(r.path for r in codebase.walk())
        expected = sorted(r.get("path") for r in expected_scan["files"])
        assert results == expected

    def test_VirtualCodebase_check_that_already_existing_parent_is_updated_properly(self):
        test_file = self.get_test_loc("resource/virtual_codebase/root-is-not-first-resource.json")
        codebase = VirtualCodebase(test_file)
        results = sorted((r.to_dict() for r in codebase.walk()), key=lambda x: tuple(x.items()))
        expected = [
            {"path": "samples", "type": "directory", "summary": ["asd"], "scan_errors": []},
            {"path": "samples/NOTICE", "type": "file", "summary": [], "scan_errors": []},
        ]
        assert results == expected

    def test_VirtualCodebase_create_from_multiple_scans(self):
        test_file_1 = self.get_test_loc("resource/virtual_codebase/combine-1.json")
        test_file_2 = self.get_test_loc("resource/virtual_codebase/combine-2.json")
        vinput = (test_file_1, test_file_2)
        codebase = VirtualCodebase(vinput)
        results = [r.to_dict(with_info=False) for r in codebase.walk()]
        expected_file = self.get_test_loc(
            "resource/virtual_codebase/combine-expected.json",
            must_exist=False,
        )
        check_against_expected_json_file(results, expected_file, regen=False)

    def test_VirtualCodebase_create_from_multiple_scans_shared_directory_names(self):
        test_file_1 = self.get_test_loc(
            "resource/virtual_codebase/combine-shared-directory-name-1.json"
        )
        test_file_2 = self.get_test_loc(
            "resource/virtual_codebase/combine-shared-directory-name-2.json"
        )
        vinput = (test_file_1, test_file_2)
        codebase = VirtualCodebase(location=vinput)

        results = [r.to_dict(with_info=False) for r in codebase.walk()]
        expected_file = self.get_test_loc(
            "resource/virtual_codebase/combine-shared-directory-name-expected.json",
            must_exist=False,
        )
        check_against_expected_json_file(results, expected_file, regen=False)

    def test_VirtualCodebase_compute_counts_with_full_root_info_one(self):
        test_file = self.get_test_loc("resource/virtual_codebase/full-root-info-one.json")
        codebase = VirtualCodebase(test_file)
        resource = [r for r in codebase.walk() if r.is_file][0]
        assert resource.path == "home/foobar/scancode-toolkit/samples/README"
        files_count, dirs_count, size_count = codebase.compute_counts()
        assert files_count == 1
        assert dirs_count == 0
        assert size_count == 236

    def test_VirtualCodebase_with_full_root_info_one(self):
        test_file = self.get_test_loc("resource/virtual_codebase/full-root-info-one.json")
        codebase = VirtualCodebase(test_file)
        results = [r.to_dict(with_info=True) for r in codebase.walk()]
        expected_file = self.get_test_loc(
            "resource/virtual_codebase/full-root-info-one-expected.json", must_exist=False
        )
        check_against_expected_json_file(results, expected_file, regen=False)

    def test_VirtualCodebase_with_full_root_info_many(self):
        test_file = self.get_test_loc("resource/virtual_codebase/full-root-info-many.json")
        codebase = VirtualCodebase(test_file)
        results = [r.to_dict(with_info=True) for r in codebase.walk()]
        expected_file = self.get_test_loc(
            "resource/virtual_codebase/full-root-info-many-expected.json", must_exist=False
        )
        check_against_expected_json_file(results, expected_file, regen=False)

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

    def test_VirtualCodebase_can_be_created_with_repeated_root_directory(self):
        paths = [
            "to",
            "to/to",
            "to/to/to",
            "to/to/to/to",
        ]
        resources = [{"path": path} for path in paths]
        vc = VirtualCodebase(location={"files": resources})
        walked_paths = [r.path for r in vc.walk()]
        assert paths == walked_paths


class TestResource(FileBasedTesting):
    test_data_dir = join(dirname(__file__), "data")

    def test_Resource_extracted_to_extracted_from(self):
        test_file = self.get_test_loc("resource/resource/test-extracted-from-to.json")
        codebase = VirtualCodebase(location=test_file)
        results = []
        for r in codebase.walk(topdown=True):
            extracted_to = r.extracted_to(codebase)
            extracted_from = r.extracted_from(codebase)

            extracted_to_path = extracted_to and extracted_to.path
            extracted_from_path = extracted_from and extracted_from.path
            results.append((r.path, extracted_to_path, extracted_from_path))

        expected = [
            (
                "test",
                None,
                None,
            ),
            (
                "test/c",
                None,
                None,
            ),
            (
                "test/foo.tar.gz",
                "test/foo.tar.gz-extract",
                None,
            ),
            (
                "test/foo.tar.gz-extract",
                None,
                "test/foo.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo",
                None,
                "test/foo.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo/a",
                None,
                "test/foo.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo/bar.tar.gz",
                "test/foo.tar.gz-extract/foo/bar.tar.gz-extract",
                "test/foo.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo/bar.tar.gz-extract",
                None,
                "test/foo.tar.gz-extract/foo/bar.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar",
                None,
                "test/foo.tar.gz-extract/foo/bar.tar.gz",
            ),
            (
                "test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar/b",
                None,
                "test/foo.tar.gz-extract/foo/bar.tar.gz",
            ),
        ]
        assert results == expected

    def test_virtualcode_Resource_can_walk(self):
        test_file = self.get_test_loc("resource/resource/test-extracted-from-to.json")
        codebase = VirtualCodebase(location=test_file)
        results = [r.path for r in codebase.walk(topdown=True)]

        expected = [
            "test",
            "test/c",
            "test/foo.tar.gz",
            "test/foo.tar.gz-extract",
            "test/foo.tar.gz-extract/foo",
            "test/foo.tar.gz-extract/foo/a",
            "test/foo.tar.gz-extract/foo/bar.tar.gz",
            "test/foo.tar.gz-extract/foo/bar.tar.gz-extract",
            "test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar",
            "test/foo.tar.gz-extract/foo/bar.tar.gz-extract/bar/b",
        ]

        assert results == expected
