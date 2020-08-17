
# Copyright (c) nexB Inc. and others. All rights reserved.
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

from packagedcode import opam

from packages_test_utils import PackageTester


class TestOcaml(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_sample1(self):
        test_file = self.get_test_loc('opam/sample1/sample1.opam')
        expected_loc = self.get_test_loc('opam/sample1/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample2(self):
        test_file = self.get_test_loc('opam/sample2/sample2.opam')
        expected_loc = self.get_test_loc('opam/sample2/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample3(self):
        test_file = self.get_test_loc('opam/sample3/sample3.opam')
        expected_loc = self.get_test_loc('opam/sample3/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample4(self):
        test_file = self.get_test_loc('opam/sample4/opam')
        expected_loc = self.get_test_loc('opam/sample4/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample5(self):
        test_file = self.get_test_loc('opam/sample5/opam')
        expected_loc = self.get_test_loc('opam/sample5/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample6(self):
        test_file = self.get_test_loc('opam/sample6/sample6.opam')
        expected_loc = self.get_test_loc('opam/sample6/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample7(self):
        test_file = self.get_test_loc('opam/sample7/sample7.opam')
        expected_loc = self.get_test_loc('opam/sample7/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_sample8(self):
        test_file = self.get_test_loc('opam/sample8/opam')
        expected_loc = self.get_test_loc('opam/sample8/output.opam.expected')
        package = opam.parse(test_file)
        self.check_package(package, expected_loc, regen=False)


FILE_LINE = [
    ('authors: "BAP Team"', ('authors', '"BAP Team"')),
    ('homepage: "https://github.com/BinaryAnalysisPlatform/bap/"', ('homepage', '"https://github.com/BinaryAnalysisPlatform/bap/"'))
]

CHECKSUM_LINE = [
    ('md5=b7a7b7cce64eabf224d05ed9f2b9d471', ('md5', 'b7a7b7cce64eabf224d05ed9f2b9d471')),
    ('md5=86d48dc11dd66adac6daadbecb5f6888', ('md5', '86d48dc11dd66adac6daadbecb5f6888'))
]

DEP_LINE = [
    ('"ocaml"', ('ocaml', '')),
    ('"bap-std" {= "1.0.0"}', ('bap-std', '{= "1.0.0"}')),
    ('"camlp4"', ('camlp4', '')),
    ('"bitstring" {< "3.0.0"}', ('bitstring', '{< "3.0.0"}'))
]


class TestRegex(object):
    @pytest.mark.parametrize('line, expected_data', FILE_LINE)
    def test_parse_file_line(self, line, expected_data):
        parsed_line = opam.parse_file_line(line)
        line_information = parsed_line.groupdict()
        key, value = line_information.get('key'), line_information.get('value')
        assert (key, value) == expected_data

    @pytest.mark.parametrize('checksum, expected_data', CHECKSUM_LINE)
    def test_parse_checksum(self, checksum, expected_data):
        parsed_checksum = opam.parse_checksum(checksum)
        checksum_information = parsed_checksum.groupdict()
        key, value = checksum_information.get('key'), checksum_information.get('value')
        assert (key, value) == expected_data

    @pytest.mark.parametrize('dep, expected_data', DEP_LINE)
    def test_parse_dep(self, dep, expected_data):
        parsed_dep = opam.parse_dep(dep)
        dep_information = parsed_dep.groupdict()
        name, version = dep_information.get('name'), dep_information.get('version')
        assert (name, version) == expected_data


LINE = [
    ('"caml-list@inria.fr"', 'caml-list@inria.fr'),
    ('[make "install"]', 'make install')
]


class TestFunction(object):
    @pytest.mark.parametrize('line, expected_data', LINE)
    def test_parse_file_line(self, line, expected_data):
        stripped_line = opam.clean_data(line)
        assert stripped_line == expected_data
