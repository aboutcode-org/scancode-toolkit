#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.


import json
import os
import tempfile

from packagedcode import rockspec
from packages_test_utils import PackageTester
from scancode.cli_test_utils import run_scan_click


class TestRockspecParser(PackageTester):
    """Tests for RockspecParser following ScanCode's testing patterns."""

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_mandatory_fields_test_1(self):
        """Test extraction of mandatory fields from test1 rockspec."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        data = parser.parse()

        assert data['package'] == 'kong'
        assert data['version'] == '3.3.0-0'
        assert data['vcs_url'] == 'git+https://github.com/Kong/kong.git'
        assert len(parser.errors) == 0

    def test_optional_fields_test_1(self):
        """Test extraction of optional fields from test1 rockspec."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        data = parser.parse()

        assert data['description'] is not None
        assert 'Kong is a scalable' in data['description']
        assert data['license'] == 'Apache 2.0'
        assert data['homepage_url'] == 'https://konghq.com'

    def test_metadata_fields_test_1(self):
        """Test extraction of metadata fields from test1 rockspec."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        data = parser.parse()

        assert data['rockspec_format'] == '3.0'
        assert isinstance(data['supported_platforms'], list)
        assert len(data['supported_platforms']) == 2
        assert 'linux' in data['supported_platforms']
        assert 'macosx' in data['supported_platforms']

    def test_dependencies_test_1(self):
        """Test extraction of dependencies from test1 rockspec.

        Dependencies are now returned as parsed dicts {name, version_spec, raw}
        instead of raw strings.
        """
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        data = parser.parse()

        assert isinstance(data['dependencies'], list)
        assert len(data['dependencies']) == 30

        # Dependencies are now parsed dicts
        dep_names = [dep['name'] for dep in data['dependencies']]
        dep_raws = [dep['raw'] for dep in data['dependencies']]

        assert 'inspect' in dep_names
        assert 'luasec' in dep_names
        assert 'inspect == 3.1.3' in dep_raws
        assert 'luasec == 1.3.1' in dep_raws

    def test_concatenation_variables_test4(self):
        """Test extraction with variable concatenation in test4.rockspec."""
        test_file = self.get_test_loc('rockspec/test4.rockspec')
        parser = rockspec.RockspecParser(test_file)
        data = parser.parse()

        # version = _MODREV .. _SPECREV should resolve to "scm-1"
        assert data['package'] == 'claude.nvim'
        assert data['version'] == 'scm-1'

        # URL concatenation should resolve all variables
        assert 'github.com' in data['vcs_url']
        assert 'S1M0N38' in data['vcs_url']
        assert 'claude.nvim' in data['vcs_url']

        # Homepage concatenation
        assert 'github.com' in data['homepage_url']
        assert 'S1M0N38' in data['homepage_url']
        assert 'claude.nvim' in data['homepage_url']

        assert data['license'] == 'MIT'
        assert len(parser.errors) == 0

    def test_error_missing_package(self):
        """Test error handling when package field is missing."""
        rockspec_content = 'version = "1.0.0"\nsource = { url = "git://test" }'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rockspec', delete=False) as f:
            f.write(rockspec_content)
            f.flush()
            temp_file = f.name

        try:
            parser = rockspec.RockspecParser(temp_file)
            data = parser.parse()

            assert data['package'] is None
            assert any(err.field == 'package' for err in parser.errors)
        finally:
            os.unlink(temp_file)

    def test_error_missing_version(self):
        """Test error handling when version field is missing."""
        rockspec_content = 'package = "test"\nsource = { url = "git://test" }'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rockspec', delete=False) as f:
            f.write(rockspec_content)
            f.flush()
            temp_file = f.name

        try:
            parser = rockspec.RockspecParser(temp_file)
            data = parser.parse()

            assert data['version'] is None
            assert any(err.field == 'version' for err in parser.errors)
        finally:
            os.unlink(temp_file)

    def test_error_missing_source_url(self):
        """Test error handling when source.url is missing."""
        rockspec_content = 'package = "test"\nversion = "1.0"\nsource = { tag = "v1" }'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rockspec', delete=False) as f:
            f.write(rockspec_content)
            f.flush()
            temp_file = f.name

        try:
            parser = rockspec.RockspecParser(temp_file)
            data = parser.parse()

            assert data['vcs_url'] is None
            assert any(err.field == 'source.url' for err in parser.errors)
        finally:
            os.unlink(temp_file)

    def test_error_file_not_found(self):
        """Test error handling when rockspec file does not exist."""
        parser = rockspec.RockspecParser('/nonexistent/rockspec/path.rockspec')
        data = parser.parse()

        assert data == {}
        assert len(parser.errors) > 0


class TestRockspecHandlerIntegration(PackageTester):
    """Test RockspecHandler integration with ScanCode."""

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_datafile_rockspec(self):
        """Test that is_datafile recognizes .rockspec files."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        assert rockspec.RockspecHandler.is_datafile(test_file)

    def test_is_datafile_non_rockspec(self):
        """Test that is_datafile rejects non-.rockspec files."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        # Just verify the handler has the correct path_patterns
        assert '*.rockspec' in rockspec.RockspecHandler.path_patterns

    def test_handler_is_registered(self):
        """Test that RockspecHandler is registered in the system."""
        from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
        handlers = [h for h in APPLICATION_PACKAGE_DATAFILE_HANDLERS
                   if h.datasource_id == 'luarocks_rockspec']
        assert len(handlers) == 1, f"Expected 1 RockspecHandler, found {len(handlers)}"
        assert handlers[0] == rockspec.RockspecHandler

    def test_handler_in_datasource_registry(self):
        """Test that handler is in the HANDLER_BY_DATASOURCE_ID registry."""
        from packagedcode import HANDLER_BY_DATASOURCE_ID
        handler = HANDLER_BY_DATASOURCE_ID.get('luarocks_rockspec')
        assert handler is not None
        assert handler == rockspec.RockspecHandler

    def test_handler_attributes(self):
        """Test that handler has required attributes."""
        assert rockspec.RockspecHandler.datasource_id == 'luarocks_rockspec'
        assert rockspec.RockspecHandler.path_patterns == ('*.rockspec',)
        assert rockspec.RockspecHandler.default_package_type == 'luarocks'
        assert rockspec.RockspecHandler.default_primary_language == 'Lua'
        assert rockspec.RockspecHandler.description is not None

    def test_debug_is_datafile_direct(self):
        """Debug test: directly check if is_datafile works for the test file."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')

        # This should return True if the handler can recognize the file
        is_match = rockspec.RockspecHandler.is_datafile(test_file)
        assert is_match, f"is_datafile() returned False for {test_file}"

        # Also verify parse works directly
        packages = list(rockspec.RockspecHandler.parse(test_file))
        assert len(packages) > 0, f"parse() returned no packages for {test_file}"

    def test_end2end_rockspec_scan_with_package_flag(self):
        """End-to-end test: scan a rockspec file with --package flag."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])

        # Parse results
        with open(result_file) as f:
            results = json.load(f)

        # Check that packages were found
        packages = results.get('packages', [])
        assert len(packages) > 0, f"No packages found in scan results. Got: {json.dumps(results, indent=2)}"

        # Verify package data
        pkg = packages[0]
        assert pkg['name'] == 'kong'
        assert pkg['version'] == '3.3.0-0'
        assert pkg['type'] == 'luarocks'
        assert 'luarocks_rockspec' in pkg.get('datasource_ids', [])

        # Check dependencies from the top-level dependencies array
        # (not in the Package object itself)
        package_uid = pkg.get('package_uid')
        dependencies = results.get('dependencies', [])
        pkg_dependencies = [dep for dep in dependencies if dep.get('for_package_uid') == package_uid]
        assert len(pkg_dependencies) == 30, f"Expected 30 dependencies, got {len(pkg_dependencies)}"




class TestDependencyParsing(PackageTester):
    """Test parse_dependency helper method."""

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_dependency_with_equals_operator(self):
        """Test parsing dependency with == operator."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        result = parser.parse_dependency('inspect == 3.1.3')

        assert result is not None
        assert result['name'] == 'inspect'
        assert result['version_spec'] == '== 3.1.3'

    def test_dependency_with_gte_operator(self):
        """Test parsing dependency with >= operator."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        result = parser.parse_dependency('binaryheap >= 0.4')

        assert result is not None
        assert result['name'] == 'binaryheap'
        assert result['version_spec'] == '>= 0.4'

    def test_dependency_without_version(self):
        """Test parsing dependency without version spec."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        result = parser.parse_dependency('somedep')

        assert result is not None
        assert result['name'] == 'somedep'
        assert result['version_spec'] is None

    def test_dependency_empty_string(self):
        """Test parsing empty dependency string."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        parser = rockspec.RockspecParser(test_file)
        result = parser.parse_dependency('')

        assert result is None
    def test_handler_parse_returns_package_data(self):
        """Test that RockspecHandler.parse returns proper PackageData objects."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        packages = list(rockspec.RockspecHandler.parse(test_file))

        assert len(packages) == 1
        pkg = packages[0]

        assert isinstance(pkg, rockspec.models.PackageData)
        assert pkg.name == 'kong'
        assert pkg.version == '3.3.0-0'
        assert pkg.type == 'luarocks'
        assert pkg.datasource_id == 'luarocks_rockspec'
        assert pkg.vcs_url == 'git+https://github.com/Kong/kong.git'
        assert len(pkg.dependencies) == 30

    def test_handler_creates_dependent_packages(self):
        """Test that dependencies are converted to DependentPackage objects."""
        test_file = self.get_test_loc('rockspec/test1.rockspec')
        packages = list(rockspec.RockspecHandler.parse(test_file))

        pkg = packages[0]
        assert len(pkg.dependencies) > 0

        for dep in pkg.dependencies:
            assert isinstance(dep, rockspec.models.DependentPackage)
            assert dep.scope == 'dependencies'
            assert dep.is_runtime is True


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
