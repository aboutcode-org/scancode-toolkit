
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import pytest

from packagedcode import golang
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


@pytest.mark.parametrize('directive', ['require', 'exclude'])
@pytest.mark.parametrize('separator', ['', '\t ', '// Dependency group (comment)'])
def test_gomod_dependency_blocks_allow_empty_lines(directive, separator, tmp_path):
    location = tmp_path / 'go.mod'
    location.write_text(
        f'module example.com/main\n\n{directive} (\n'
        f'{separator}\n'
        'example.com/first v1.0.0 // First dependency\n'
        f'{separator}\n'
        'example.com/second v1.2.0\n'
        f'{separator}\n)\n'
        'require example.com/after v1.3.0\n',
        encoding='utf-8',
    )
    package = list(golang.GoModHandler.parse(str(location), package_only=True))[0]
    assert package.purl == 'pkg:golang/example.com/main'
    result = [(dep.purl, dep.scope) for dep in package.dependencies]
    expected = [
        ('pkg:golang/example.com/first@v1.0.0', directive),
        ('pkg:golang/example.com/second@v1.2.0', directive),
        ('pkg:golang/example.com/after@v1.3.0', 'require'),
    ]
    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize('directive', ['require', 'exclude'])
def test_gomod_dependency_blocks_allow_only_comments(directive, tmp_path):
    location = tmp_path / 'go.mod'
    location.write_text(
        f'module example.com/main\n{directive} (\n\n// No dependencies\n\t\n)\n',
        encoding='utf-8',
    )
    package = list(golang.GoModHandler.parse(str(location), package_only=True))[0]
    assert package.purl == 'pkg:golang/example.com/main'
    assert package.dependencies == []


class TestGolang(PackageTester):
    """
    Check go.mod and go.sum file tests.
    """

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_gomod_is_package_data_file(self):
        test_file = self.get_test_loc('golang/gomod/kingpin/go.mod')
        assert golang.GoModHandler.is_datafile(test_file)

    def test_parse_gomod_kingpin(self):
        test_file = self.get_test_loc('golang/gomod/kingpin/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/kingpin/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gomod_opencensus(self):
        test_file = self.get_test_loc('golang/gomod/opencensus-service/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/opencensus-service/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gomod_participle(self):
        test_file = self.get_test_loc('golang/gomod/participle/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/participle/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gomod_sample(self):
        test_file = self.get_test_loc('golang/gomod/sample/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/sample/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gomod_uap_go(self):
        test_file = self.get_test_loc('golang/gomod/uap-go/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/uap-go/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gomod_user_agent(self):
        test_file = self.get_test_loc('golang/gomod/user_agent/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/user_agent/output.expected.json')
        package = golang.GoModHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_gosum_is_package_data_file(self):
        test_file = self.get_test_loc('golang/gosum/sample1/go.sum')
        assert golang.GoSumHandler.is_datafile(test_file)

    def test_parse_gosum_sample1(self):
        test_file = self.get_test_loc('golang/gosum/sample1/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample1/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gosum_sample2(self):
        test_file = self.get_test_loc('golang/gosum/sample2/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample2/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gosum_sample3(self):
        test_file = self.get_test_loc('golang/gosum/sample3/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample3/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gosum_sample4(self):
        test_file = self.get_test_loc('golang/gosum/sample4/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample4/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gosum_sample5(self):
        test_file = self.get_test_loc('golang/gosum/sample5/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample5/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_gosum_sample6(self):
        test_file = self.get_test_loc('golang/gosum/sample6/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample6/output.expected.json')
        package = golang.GoSumHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)
