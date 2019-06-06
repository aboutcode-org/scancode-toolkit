
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

from packagedcode import cargo

from packages_test_utils import PackageTester


class TestCargo(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_clap(self):
        test_file = self.get_test_loc('cargo/clap/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/clap/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_clippy(self):
        test_file = self.get_test_loc('cargo/clippy/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/clippy/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_mdbook(self):
        test_file = self.get_test_loc('cargo/mdbook/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/mdbook/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_rustfmt(self):
        test_file = self.get_test_loc('cargo/rustfmt/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/rustfmt/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_rustup(self):
        test_file = self.get_test_loc('cargo/rustup/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/rustup/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)


PERSON_PARSER_TEST_TABLE = [
    ('Barney Rubble <b@rubble.com>', ('Barney Rubble ', '<b@rubble.com>')),
    ('Barney Rubble', ('Barney Rubble', None)),
    ('Some Good Guy <hisgoodmail@email.com>', ('Some Good Guy ', '<hisgoodmail@email.com>')),
    ('Some Good Guy', ('Some Good Guy', None)),
]

PERSON_NO_NAME_PARSER_TEST_TABLE = [
    ('<b@rubble.com>', (None, '<b@rubble.com>')),
    ('<anotherguy@email.com>', (None, '<anotherguy@email.com>')),
]

class TestRegex(object):
    @pytest.mark.parametrize('person, expected_person', PERSON_PARSER_TEST_TABLE)
    def test_person_parser(self, person, expected_person):
        parsed_person = cargo.person_parser(person)
        person_information = parsed_person.groupdict()
        name, email = person_information.get('name'), person_information.get('email')
        assert (name, email) == expected_person

    def test_person_parser_no_name_failure(self):
        person = '<emailwithoutname@email.com>'
        parsed_person = cargo.person_parser(person)
        assert parsed_person is None

    @pytest.mark.parametrize('person, expected_person', PERSON_NO_NAME_PARSER_TEST_TABLE)
    def test_person_parser_no_name(self, person, expected_person):
        parsed_person = cargo.person_parser_no_name(person)
        person_information = parsed_person.groupdict()
        name, email = person_information.get('name'), person_information.get('email')
        assert (name, email) == expected_person
