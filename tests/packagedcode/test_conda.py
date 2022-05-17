#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.resource import Codebase

from packages_test_utils import PackageTester
from packagedcode import conda
from scancode_config import REGEN_TEST_FIXTURES



class TestConda(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_get_varialble(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        results = conda.get_variables(test_file)
        expected = {
            'version': '0.45.0', 
            'sha256': 'bc7512f2eef785b037d836f4cc6faded457ac277f75c6e34eccd12da7c85258f',
        }
        assert results == expected

    def test_get_meta_yaml_data(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        results = conda.get_meta_yaml_data(test_file)
        assert  list(results.items())[0] == (u'package', dict([(u'name', u'abeona'), (u'version', u'0.45.0')]))

    def test_condayml_is_package_data_file(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        assert conda.CondaMetaYamlHandler.is_datafile(test_file)

    def test_parse(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        package = conda.CondaMetaYamlHandler.parse(test_file)
        expected_loc = self.get_test_loc('conda/meta.yaml.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_root_dir(self):
        test_path = 'requests-kerberos-0.8.0-py35_0.tar.bz2-extract/info/recipe.tar-extract/recipe/meta.yaml'
        test_dir = self.get_test_loc('conda/requests-kerberos-0.8.0-py35_0.tar.bz2-extract')
        codebase = Codebase(test_dir)
        resource = codebase.get_resource(path=test_path)
        proot = conda.CondaMetaYamlHandler.get_conda_root(resource, codebase)
        assert proot.location == test_dir
