#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Tests for PEP 751 pylock.toml parsing.
"""

import os

from packagedcode.pylock import PyLockHandler
from packages_test_utils import PackageTester


class TestPyLockHandler(PackageTester):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_small_pylock(self):
        test_file = self.get_test_loc('pylock/pylock-small.toml')
        results = list(PyLockHandler.parse(test_file))

        assert len(results) == 1
        package = results[0]

        assert package.datasource_id == 'pylock'
        assert package.type == 'pypi'
        assert package.name == 'python-environment'
        assert package.version is None
        assert package.primary_language == 'Python'
        assert package.is_virtual

        assert len(package.dependencies) == 1
        dep = package.dependencies[0]

        assert dep.purl == 'pkg:pypi/attrs@25.1.0'
        assert dep.extracted_requirement == '25.1.0'
        assert dep.scope == 'runtime'
        assert dep.is_runtime
        assert dep.is_optional is False
        assert dep.is_pinned

        assert package.extra_data['lock_version'] == '1.0'
        assert package.extra_data['created_by'] == 'uv'
        assert package.extra_data['requires_python'] == '>=3.13'
        assert package.extra_data['package_count'] >= 1

    def test_parse_medium_pylock(self):
        test_file = self.get_test_loc('pylock/pylock-medium.toml')
        results = list(PyLockHandler.parse(test_file))

        assert len(results) == 1
        package = results[0]

        assert package.datasource_id == 'pylock'
        assert package.type == 'pypi'
        assert package.is_virtual
        assert package.extra_data['package_count'] >= 3

        purls = {dep.purl for dep in package.dependencies}
        assert {
            'pkg:pypi/attrs@25.1.0',
            'pkg:pypi/cattrs@24.1.2',
            'pkg:pypi/numpy@2.2.3',
        } == purls

        for dep in package.dependencies:
            assert dep.scope == 'runtime'
            assert dep.is_runtime
            assert dep.is_optional is False
            assert dep.is_pinned

        # Check optional fields are extracted
        assert package.extra_data['created_by'] == 'mousebender'
        assert package.extra_data['requires_python'] == '==3.12'

    def test_package_only_mode(self):
        test_file = self.get_test_loc('pylock/pylock-small.toml')
        results = list(PyLockHandler.parse(test_file, package_only=True))

        assert len(results) == 1
        package = results[0]

        assert package.datasource_id == 'pylock'
        assert package.type == 'pypi'
        assert package.is_virtual
        assert package.name == 'python-environment'
        assert package.dependencies == []

        assert package.extra_data['lock_version'] == '1.0'
        assert package.extra_data['package_count'] >= 1

    def test_large_pylock_invalid_toml(self):
        """
        pylock-large.toml contains invalid TOML syntax.
        Parsing should fail gracefully.
        """
        test_file = self.get_test_loc('pylock/pylock-large.toml')
        results = list(PyLockHandler.parse(test_file))

        assert results == []

    def test_malformed_packages_pylock(self):
        """
        Malformed pylock files should not crash parsing.
        Should skip packages with missing required fields but parse valid ones.
        """
        test_file = self.get_test_loc('pylock/pylock-malformed-packages.toml')
        results = list(PyLockHandler.parse(test_file))

        assert len(results) == 1
        package = results[0]
        assert package.is_virtual
        assert package.name == 'python-environment'
        
        # Should only have one valid dependency (attrs) and skip malformed ones
        assert len(package.dependencies) == 1
        dep = package.dependencies[0]
        assert dep.purl == 'pkg:pypi/attrs@25.1.0'
        assert dep.is_pinned
        
        assert package.extra_data['lock_version'] == '1.0'
        assert package.extra_data['package_count'] == 3 

    def test_missing_lock_version(self):
        test_file = self.get_test_loc('pylock/pylock-nolock-version.toml')
        results = list(PyLockHandler.parse(test_file))

        assert results == []

    def test_handler_metadata(self):
        assert PyLockHandler.datasource_id == 'pylock'
        assert PyLockHandler.path_patterns == ('*/pylock.toml',)
        assert PyLockHandler.default_package_type == 'pypi'
        assert PyLockHandler.default_primary_language == 'Python'
        assert PyLockHandler.is_lockfile is True
        assert 'PEP 751' in PyLockHandler.description
        assert PyLockHandler.documentation_url == 'https://peps.python.org/pep-0751/'

    def test_empty_packages_list(self):
        """
        Test pylock files with empty packages array.
        """
        test_file = self.get_test_loc('pylock/pylock-empty.toml')
        results = list(PyLockHandler.parse(test_file))
        assert results == []

    def test_file_not_found(self):
        results = list(PyLockHandler.parse('/non/existent/file.toml'))
        assert results == []

    def test_invalid_file_format(self):
        """
        Test files with invalid TOML format should fail gracefully.
        """
        test_file = self.get_test_loc('pylock/pylock-invalid-format.toml')
        results = list(PyLockHandler.parse(test_file))
        assert results == []
