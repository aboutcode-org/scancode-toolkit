
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Codebase
from licensedcode.detection import find_referenced_resource

class TestIssue4276(FileDrivenTesting):
    
    def test_find_referenced_resource_with_glob(self):
        test_dir = self.get_temp_dir()
        os.makedirs(os.path.join(test_dir, 'licenses'))
        with open(os.path.join(test_dir, 'README.txt'), 'w') as f:
            f.write('See licenses/*.txt')
        with open(os.path.join(test_dir, 'licenses', 'MIT.txt'), 'w') as f:
            f.write('MIT License')
        
        codebase = Codebase(test_dir)
        readme = None
        for res in codebase.walk():
            if res.name == 'README.txt':
                readme = res
                break
        assert readme is not None, "README.txt resource not found in codebase"
        
        # Test finding with glob
        # This currently expects a single return, but we want it to handle globs
        # For this test, we accept either a list or a single resource if we stick to single-return for now
        # But realistically we need a list.
        
        print(f"DEBUG: Root path: {codebase.root.path if codebase.root else 'None'}")
        print(f"DEBUG: Readme path: {readme.path}")
        print(f"DEBUG: Readme parent: {readme.parent_path()}")
        print(f"DEBUG: All resources: {[r.path for r in codebase.walk()]}")
        
        result = find_referenced_resource('licenses/*.txt', readme, codebase)
        print(f"DEBUG: Result: {result}")
        
        assert result is not None
        if isinstance(result, list):
            assert len(result) > 0
            assert result[0].path.endswith('licenses/MIT.txt')
        else:
            assert result.path.endswith('licenses/MIT.txt')

    def test_find_referenced_resource_with_directory(self):
        test_dir = self.get_temp_dir()
        os.makedirs(os.path.join(test_dir, 'licenses'))
        with open(os.path.join(test_dir, 'README.txt'), 'w') as f:
            f.write('See licenses/')
        with open(os.path.join(test_dir, 'licenses', 'MIT.txt'), 'w') as f:
            f.write('MIT License')
        
        codebase = Codebase(test_dir)
        readme = None
        for res in codebase.walk():
             if res.name == 'README.txt':
                 readme = res
                 break
        assert readme is not None

        # referencing a directory should return all files in it
        result = find_referenced_resource('licenses/', readme, codebase)
        
        assert result is not None
        assert isinstance(result, list)
        # We expect it to find the file inside the directory
        found_paths = [r.path for r in result]
        assert any(p.endswith('licenses/MIT.txt') for p in found_paths)
