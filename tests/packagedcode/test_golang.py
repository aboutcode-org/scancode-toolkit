
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest

from packagedcode import golang

from packages_test_utils import PackageTester


class TestGolang(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_gomod_kingpin(self):
        test_file = self.get_test_loc('golang/gomod/kingpin/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/kingpin/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gomod_opencensus(self):
        test_file = self.get_test_loc('golang/gomod/opencensus-service/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/opencensus-service/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gomod_participle(self):
        test_file = self.get_test_loc('golang/gomod/participle/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/participle/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gomod_sample(self):
        test_file = self.get_test_loc('golang/gomod/sample/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/sample/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gomod_uap_go(self):
        test_file = self.get_test_loc('golang/gomod/uap-go/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/uap-go/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gomod_user_agent(self):
        test_file = self.get_test_loc('golang/gomod/user_agent/go.mod')
        expected_loc = self.get_test_loc('golang/gomod/user_agent/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample1(self):
        test_file = self.get_test_loc('golang/gosum/sample1/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample1/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample2(self):
        test_file = self.get_test_loc('golang/gosum/sample2/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample2/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample3(self):
        test_file = self.get_test_loc('golang/gosum/sample3/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample3/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample4(self):
        test_file = self.get_test_loc('golang/gosum/sample4/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample4/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample5(self):
        test_file = self.get_test_loc('golang/gosum/sample5/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample5/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_parse_gosum_sample6(self):
        test_file = self.get_test_loc('golang/gosum/sample6/go.sum')
        expected_loc = self.get_test_loc('golang/gosum/sample6/output.expected.json')
        package = golang.GolangPackage.recognize(test_file)
        self.check_packages(package, expected_loc, regen=False)