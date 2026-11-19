#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
#

import os

from packagedcode import srcinfo
from packages_test_utils import PackageTester


class TestSrcinfo(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_srcinfo_basic(self):
        test_file = self.get_test_loc('srcinfo/rust-basic/.SRCINFO')
        packages = list(srcinfo.SrcinfoHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        assert package.type == 'arch'
        assert package.name == 'rust-basic'
        assert '1.0.0' in package.version
        assert package.description
        
    def test_parse_srcinfo_with_dependencies(self):
        test_file = self.get_test_loc('srcinfo/with-deps/.SRCINFO')
        packages = list(srcinfo.SrcinfoHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        runtime_deps = [d for d in package.dependencies if d.is_runtime and not d.is_optional]
        build_deps = [d for d in package.dependencies if not d.is_runtime]
        opt_deps = [d for d in package.dependencies if d.is_optional]
        
        assert len(runtime_deps) > 0
        assert len(build_deps) > 0
        assert len(opt_deps) > 0

    def test_parse_srcinfo_arch_specific(self):
        test_file = self.get_test_loc('srcinfo/arch-specific/.SRCINFO')
        packages = list(srcinfo.SrcinfoHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        arch_specific = [d for d in package.dependencies if 'x86_64' in d.scope or 'aarch64' in d.scope]
        assert len(arch_specific) > 0

    def test_parse_srcinfo_split_package(self):
        test_file = self.get_test_loc('srcinfo/split-package/.SRCINFO')
        packages = list(srcinfo.SrcinfoHandler.parse(test_file))
        
        assert len(packages) > 1
        
        names = [p.name for p in packages]
        assert len(set(names)) == len(names) 

    def test_parse_srcinfo_with_checksums(self):
        test_file = self.get_test_loc('srcinfo/with-checksums/.SRCINFO')
        packages = list(srcinfo.SrcinfoHandler.parse(test_file))
        
        assert len(packages) == 1
        package = packages[0]
        
        assert 'sha256sums' in package.extra_data or 'md5sums' in package.extra_data