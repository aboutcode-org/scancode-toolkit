
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import pytest

from packagedcode import cargo

from packages_test_utils import PackageTester


class TestCargo(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_cargo_toml_clap(self):
        test_file = self.get_test_loc('cargo/cargo_toml/clap/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/cargo_toml/clap/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_toml_clippy(self):
        test_file = self.get_test_loc('cargo/cargo_toml/clippy/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/cargo_toml/clippy/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_toml_mdbook(self):
        test_file = self.get_test_loc('cargo/cargo_toml/mdbook/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/cargo_toml/mdbook/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_toml_rustfmt(self):
        test_file = self.get_test_loc('cargo/cargo_toml/rustfmt/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/cargo_toml/rustfmt/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_toml_rustup(self):
        test_file = self.get_test_loc('cargo/cargo_toml/rustup/Cargo.toml')
        expected_loc = self.get_test_loc('cargo/cargo_toml/rustup/Cargo.toml.expected')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_lock_sample1(self):
        test_file = self.get_test_loc('cargo/cargo_lock/sample1/Cargo.lock')
        expected_loc = self.get_test_loc('cargo/cargo_lock/sample1/output.expected.json')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_lock_sample2(self):
        test_file = self.get_test_loc('cargo/cargo_lock/sample2/Cargo.lock')
        expected_loc = self.get_test_loc('cargo/cargo_lock/sample2/output.expected.json')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_lock_sample3(self):
        test_file = self.get_test_loc('cargo/cargo_lock/sample3/Cargo.lock')
        expected_loc = self.get_test_loc('cargo/cargo_lock/sample3/output.expected.json')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_lock_sample4(self):
        test_file = self.get_test_loc('cargo/cargo_lock/sample4/Cargo.lock')
        expected_loc = self.get_test_loc('cargo/cargo_lock/sample4/output.expected.json')
        package = cargo.parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_parse_cargo_lock_sample5(self):
        test_file = self.get_test_loc('cargo/cargo_lock/sample5/Cargo.lock')
        expected_loc = self.get_test_loc('cargo/cargo_lock/sample5/output.expected.json')
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
