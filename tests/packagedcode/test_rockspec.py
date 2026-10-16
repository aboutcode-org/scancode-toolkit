#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.


import os
import tempfile

from packagedcode import rockspec
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestRockspecHandler(PackageTester):
    """
    Tests for RockspecHandler following ScanCode's testing patterns.

    Tests use the comprehensive JSON snapshot approach with check_packages_data()
    to compare entire handler output against expected JSON files. This provides
    better visibility into the complete output and makes it easier to detect
    any changes.
    """

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_lua_cjson_rockspec(self):
        """Test parsing lua-cjson.rockspec."""
        test_file = self.get_test_loc('rockspec/lua-cjson.rockspec')
        packages = rockspec.RockspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('rockspec/lua-cjson.rockspec-expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_kong_rockspec(self):
        """Test parsing kong.rockspec with mandatory and optional fields."""
        test_file = self.get_test_loc('rockspec/kong.rockspec')
        packages = rockspec.RockspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('rockspec/kong.rockspec-expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_luasocket_rockspec(self):
        """Test parsing luasocket.rockspec."""
        test_file = self.get_test_loc('rockspec/luasocket.rockspec')
        packages = rockspec.RockspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('rockspec/luasocket.rockspec-expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_vdsl_rockspec(self):
        """Test parsing vdsl.rockspec."""
        test_file = self.get_test_loc('rockspec/vdsl.rockspec')
        packages = rockspec.RockspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('rockspec/vdsl.rockspec-expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_claude_nvim_rockspec(self):
        """Test parsing claude.nvim.rockspec with variable concatenation."""
        test_file = self.get_test_loc('rockspec/claude.nvim.rockspec')
        packages = rockspec.RockspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('rockspec/claude.nvim.rockspec-expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_handler_is_registered(self):
        """Test that RockspecHandler is registered in the application handlers."""
        from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
        handlers = [h for h in APPLICATION_PACKAGE_DATAFILE_HANDLERS
                   if h.datasource_id == 'luarocks_rockspec']
        assert len(handlers) == 1, f"Expected 1 RockspecHandler, found {len(handlers)}"
        assert handlers[0] == rockspec.RockspecHandler

    def test_handler_attributes(self):
        """Test that handler has required attributes."""
        assert rockspec.RockspecHandler.datasource_id == 'luarocks_rockspec'
        assert rockspec.RockspecHandler.path_patterns == ('*.rockspec',)
        assert rockspec.RockspecHandler.default_package_type == 'luarocks'
        assert rockspec.RockspecHandler.default_primary_language == 'Lua'
        assert rockspec.RockspecHandler.description is not None

    def test_is_datafile_rockspec(self):
        """Test that is_datafile recognizes .rockspec files."""
        test_file = self.get_test_loc('rockspec/kong.rockspec')
        assert rockspec.RockspecHandler.is_datafile(test_file)

    def test_is_datafile_non_rockspec(self):
        """Test that is_datafile rejects non-.rockspec files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        try:
            assert not rockspec.RockspecHandler.is_datafile(temp_file)
        finally:
            os.unlink(temp_file)
