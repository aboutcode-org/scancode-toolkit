
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import golang
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


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
