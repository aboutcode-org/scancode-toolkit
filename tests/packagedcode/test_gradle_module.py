#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os.path

import pytest

from commoncode import fileutils
from commoncode import text
from commoncode import testcase

from packagedcode import gradle
from packagedcode import models
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


def parse_module(location=None):
    """
    Return a PackageData mapping from the Gradle module file at location.
    """
    packages = list(gradle.GradleModuleHandler.parse(location=location))
    if not packages:
        return {}
    package = packages[0]
    return package.to_dict()


class TestGradleModule(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_gradle_module_is_datafile(self):
        test_dir = self.get_test_loc('gradle/module')
        material_module = os.path.join(test_dir, 'material-1.9.0.module')
        simple_module = os.path.join(test_dir, 'simple.module')
        
        assert gradle.GradleModuleHandler.is_datafile(material_module)
        assert gradle.GradleModuleHandler.is_datafile(simple_module)
        
        # Create a fake JSON file
        fake_json = self.get_temp_file('json')
        with open(fake_json, 'w') as f:
            f.write('{"foo": "bar"}')
        assert not gradle.GradleModuleHandler.is_datafile(fake_json)

    def test_parse_material_module(self):
        test_loc = self.get_test_loc('gradle/module/material-1.9.0.module')
        result = parse_module(test_loc)
        
        assert result.get('type') == 'maven'
        assert result.get('namespace') == 'com.google.android.material'
        assert result.get('name') == 'material'
        assert result.get('version') == '1.9.0'
        
        deps = result.get('dependencies', [])
        assert len(deps) == 3
        
        purls = [d.get('purl') for d in deps]
        assert 'pkg:maven/androidx.annotation/annotation@1.2.0' in purls
        assert 'pkg:maven/androidx.appcompat/appcompat@1.5.0' in purls
        assert 'pkg:maven/com.google.errorprone/error_prone_annotations@2.15.0' in purls
        
        extra = result.get('extra_data', {})
        assert extra.get('gradle_version') == '7.3.3'
        assert extra.get('format_version') == '1.1'

    def test_parse_simple_module(self):
        test_loc = self.get_test_loc('gradle/module/simple.module')
        result = parse_module(test_loc)
        
        assert result.get('namespace') == 'com.example'
        assert result.get('name') == 'mylib'
        assert result.get('version') == '1.0.0'
        assert result.get('dependencies') == []

    def test_parse_no_deps_module(self):
        test_loc = self.get_test_loc('gradle/module/no-deps.module')
        # Does not crash
        result = parse_module(test_loc)
        
        assert result.get('namespace') == 'org.example'
        assert result.get('name') == 'standalone'
        assert result.get('dependencies') == []

    def test_parse_spring_module(self):
        test_loc = self.get_test_loc('gradle/module/dependency-management-plugin-1.1.3.module')
        result = parse_module(test_loc)
        
        assert result.get('namespace') == 'io.spring.gradle'
        assert result.get('name') == 'dependency-management-plugin'
        assert result.get('version') == '1.1.3'
        
        deps = result.get('dependencies', [])
        assert len(deps) == 1
        assert deps[0].get('purl') == 'pkg:maven/org.springframework.boot/spring-boot@3.1.0'

    def test_dependencies_deduplicated(self):
        test_loc = self.get_test_loc('gradle/module/material-1.9.0.module')
        result = parse_module(test_loc)
        
        deps = result.get('dependencies', [])
        purls = [d.get('purl') for d in deps]
        assert len(purls) == len(set(purls))
