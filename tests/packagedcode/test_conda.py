#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import os

from commoncode.resource import Codebase

from packages_test_utils import PackageTester
from packagedcode import conda
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan



class TestConda(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_get_variables(self):
        test_file = self.get_test_loc('conda/meta-yaml/abeona/meta.yaml')
        results = conda.get_variables(test_file)
        expected = {
            'version': '0.45.0', 
            'sha256': 'bc7512f2eef785b037d836f4cc6faded457ac277f75c6e34eccd12da7c85258f',
        }
        assert results == expected

    def test_parse_get_variables_2(self):
        test_file = self.get_test_loc('conda/meta-yaml/gcnvkernel/meta.yaml')
        results = conda.get_variables(test_file)
        expected = {
            'version': '0.9', 
            'name': 'gcnvkernel',
            'gatk_version': '4.6.1.0',
            'gatk_sha256': 'ac7015c3f0ef1852745ca0ef647adbf8ddef5db63ab485b00bc1ffe654814155',
        }
        assert results == expected

    def test_get_meta_yaml_data(self):
        test_file = self.get_test_loc('conda/meta-yaml/abeona/meta.yaml')
        results = conda.get_meta_yaml_data(test_file)
        assert  list(results.items())[0] == (u'package', dict([(u'name', u'abeona'), (u'version', u'0.45.0')]))

    def test_conda_meta_yml_is_package_data_file(self):
        test_file = self.get_test_loc('conda/meta-yaml/abeona/meta.yaml')
        assert conda.CondaMetaYamlHandler.is_datafile(test_file)

    def test_parse_conda_meta_yaml_with_templates_and_about(self):
        test_file = self.get_test_loc('conda/meta-yaml/abeona/meta.yaml')
        package = conda.CondaMetaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/meta-yaml/abeona/meta.yaml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_conda_meta_yaml_root_dir(self):
        test_path = 'requests-kerberos-0.8.0-py35_0.tar.bz2-extract/info/recipe.tar-extract/recipe/meta.yaml'
        test_dir = self.get_test_loc('conda/requests-kerberos-0.8.0-py35_0.tar.bz2-extract')
        codebase = Codebase(test_dir)
        resource = codebase.get_resource(path=test_path)
        proot = conda.CondaMetaYamlHandler.get_conda_root(resource, codebase)
        assert proot.location == test_dir

    def test_conda_yml_is_package_data_file_with_conda_dir(self):
        test_file = self.get_test_loc('misc/conda/scenicplus.yaml')
        assert conda.CondaYamlHandler.is_datafile(test_file)

    def test_conda_yml_is_package_data_file_environment(self):
        test_file = self.get_test_loc('conda/conda-yaml/phc-gnn/environment_gpu.yml')
        assert conda.CondaYamlHandler.is_datafile(test_file)

    def test_parse_conda_meta_yaml_package_from_non_default_channels(self):
        test_file = self.get_test_loc('conda/meta-yaml/pippy/meta.yaml')
        package = conda.CondaMetaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/meta-yaml/pippy/meta.yaml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_meta_yaml_package_and_assemble(self):
        test_file = self.get_test_loc('conda/meta-yaml/pippy/meta.yaml')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        expected_file = self.get_test_loc('conda/meta-yaml/pippy/meta.yaml-scancode.json')
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )

    def test_parse_simple_conda_yaml(self):
        test_file = self.get_test_loc('conda/conda-yaml/phc-gnn/environment_gpu.yml')
        assert conda.CondaYamlHandler.is_datafile(test_file)

        package = conda.CondaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/conda-yaml/phc-gnn/environment_gpu.yml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_yaml_with_pip_source_repos(self):
        test_file = self.get_test_loc('misc/conda/scenicplus.yaml')
        package = conda.CondaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('misc/conda/scenicplus.yaml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_meta_yaml_with_multiple_templates(self):
        test_file = self.get_test_loc('conda/meta-yaml/gcnvkernel/meta.yaml')
        package = conda.CondaMetaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/meta-yaml/gcnvkernel/meta.yaml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_yaml_simple_dependencies(self):
        test_file = self.get_test_loc('conda/conda-yaml/ringer/environment.yaml')
        package = conda.CondaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/conda-yaml/ringer/environment.yaml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_yaml_does_not_fail_on_test_files_with_port(self):
        test_file = self.get_test_loc('conda/conda-yaml/test/environment_host_port.yml')
        package = conda.CondaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/conda-yaml/test/environment_host_port.yml-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_conda_get_conda_meta_json(self):
        meta_yaml_path = 'conda/pkgs/requests-2.32.3-py312h06a4308_1/info/recipe/meta.yaml'
        conda_meta_json_path = 'conda/conda-meta/requests-2.32.3-py312h06a4308_1.json'

        test_dir = self.get_test_loc('conda/assembly/opt/conda/')
        resource_attributes = dict(package_data=attr.ib(default=attr.Factory(list), repr=False),)
        codebase = Codebase(location=test_dir, resource_attributes=resource_attributes)

        package_data = [{'name': 'requests', 'version':'2.32.3'}]
        meta_yaml_resource = codebase.get_resource(path=meta_yaml_path)
        setattr(meta_yaml_resource, 'package_data', package_data)
        codebase.save_resource(meta_yaml_resource)
        conda_meta_json_resource = codebase.get_resource(path=conda_meta_json_path)
        setattr(conda_meta_json_resource, 'package_data', package_data)
        codebase.save_resource(conda_meta_json_resource)

        meta_json = conda.CondaBaseHandler.find_conda_meta_json_resource(meta_yaml_resource, codebase)
        assert meta_json.path == conda_meta_json_path

        meta_yaml = conda.CondaBaseHandler.find_conda_meta_yaml_resource(conda_meta_json_resource, codebase)
        assert meta_yaml.path == meta_yaml_path

    def test_conda_pkgs_meta_yaml_root_dir(self):
        meta_yaml_path = 'conda/pkgs/requests-2.32.3-py312h06a4308_1/info/recipe/meta.yaml'
        root_path = 'conda/pkgs/requests-2.32.3-py312h06a4308_1'
        test_dir = self.get_test_loc('conda/assembly/opt/conda/')
        codebase = Codebase(test_dir)
        resource = codebase.get_resource(path=meta_yaml_path)
        proot = conda.CondaMetaYamlHandler.get_conda_root(resource, codebase)
        assert proot.path == root_path

    def test_parse_is_datafile_conda_meta_package_with_files(self):
        test_file = self.get_test_loc('conda/conda-meta/tzdata-2024b-h04d1e81_0.json')
        assert conda.CondaMetaJsonHandler.is_datafile(test_file)

    def test_parse_conda_meta_package_with_files(self):
        test_file = self.get_test_loc('conda/conda-meta/tzdata-2024b-h04d1e81_0.json')
        package = conda.CondaMetaJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/conda-meta/tzdata-expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_conda_meta_yaml_conda_meta_assemble_from_rootfs(self):
        test_location = self.get_test_loc('conda/assembly/')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_location, '--json', result_file])
        expected_file = self.get_test_loc('conda/assembly-conda-scan.json')
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )
