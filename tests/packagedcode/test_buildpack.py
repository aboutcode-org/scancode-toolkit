#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from packagedcode import buildpack
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

class TestBuildpack(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


    def test_parse_heroku_buildpack_java_toml(self):
        test_file = self.get_test_loc('buildpack/heroku-buildpacks/heroku-buildpack-java/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/heroku-buildpacks/heroku-buildpack-java/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_heroku_buildpack_php_toml(self):
        test_file = self.get_test_loc('buildpack/heroku-buildpacks/heroku-buildpack-php/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/heroku-buildpacks/heroku-buildpack-php/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_dotnet_execute_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/dotnet-execute/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/dotnet-execute/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_java_memory_assistant_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/java-memory-assistant/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/java-memory-assistant/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_git_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/git/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/git/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_opentelemetry_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/opentelemetry/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/opentelemetry/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_pipeline_builder_canary_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/pipeline-builder-canary/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/pipeline-builder-canary/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_paketo_source_removal_buildpack_toml(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/source-removal/buildpack.toml')
        expected_loc = self.get_test_loc('buildpack/paketo-buildpacks/source-removal/expectedoutput.json')
        packages_data = list(buildpack.BuildpackHandler.parse(test_file))
        self.check_packages_data(packages_data, expected_loc, regen=REGEN_TEST_FIXTURES)
    
    def test_scanworks_on_heroku_buildpack(self):
        test_file = self.get_test_loc('buildpack/heroku-buildpacks/heroku-buildpack-php/buildpack.toml')
        expected_file = self.get_test_loc('buildpack/heroku-buildpacks/heroku-results.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
    
    def test_scanworks_on_paketo_buildpack(self):
        test_file = self.get_test_loc('buildpack/paketo-buildpacks/pipeline-builder-canary/buildpack.toml')
        expected_file = self.get_test_loc('buildpack/paketo-buildpacks/paketo-results.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

