#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packages_test_utils import PackageTester
from packagedcode import conda
from commoncode.resource import Codebase


class TestConda(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_get_varialble(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        results = conda.get_variables(test_file)
        assert results == dict([(u'version', u'0.45.0'), (u'sha256', u'bc7512f2eef785b037d836f4cc6faded457ac277f75c6e34eccd12da7c85258f')])

    def test_get_yaml_data(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        results = conda.get_yaml_data(test_file)
        assert  list(results.items())[0] == (u'package', dict([(u'name', u'abeona'), (u'version', u'0.45.0')]))

    def test_parse(self):
        test_file = self.get_test_loc('conda/meta.yaml')
        package = conda.parse(test_file)
        expected_loc = self.get_test_loc('conda/meta.yaml.expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_root_dir(self):
        test_file = self.get_test_loc('conda/requests-kerberos-0.8.0-py35_0.tar.bz2-extract/info/recipe.tar-extract/recipe/meta.yaml')
        test_dir = self.get_test_loc('conda/requests-kerberos-0.8.0-py35_0.tar.bz2-extract')
        codebase = Codebase(test_dir)
        manifest_resource = codebase.get_resource_from_path(test_file, absolute=True)
        proot = conda.CondaPackage.get_package_root(manifest_resource, codebase)
        assert proot.location == test_dir
