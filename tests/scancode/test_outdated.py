#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest

from scancode import outdated


def test_fetch_latest_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '2.2.1': [],
            '2.9.0b1': [],
            '2.9.1': [],
            '3.0.2': [],
            '2.9.2': [],
            '2.9.3': [],
            '2.9.4': [],
            '3.0.0': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )
        result = outdated.fetch_latest_version()
        assert result == '3.0.2'


def test_fetch_latest_version_fails_on_http_error():
    from unittest import mock
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(status_code=400)
        with pytest.raises(Exception):
            outdated.fetch_latest_version()


def test_fetch_latest_version_ignore_rc_versions():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '2.2.1': [],
            '2.9.0rc3': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )
        result = outdated.fetch_latest_version()
        assert result == '2.2.1'


def test_fetch_newer_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '3.4.1': [],
            '22.1': [],
            '30.9.0rc3': [],
            '42.5.1': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )
        assert outdated.fetch_newer_version(force=True) == '42.5.1'


def test_check_scancode_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '3.4.1': [],
            '22.1': [],
            '30.9.0rc3': [],
            '42.5.1': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )

        result = outdated.check_scancode_version(force=True)
        assert result.startswith('WARNING: Outdated ScanCode')
        assert 'A new version 42.5.1 is available' in result


def test_fetch_newer_version_no_new_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '3.0.1': [],
            '3.9.0rc3': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )
        assert not outdated.fetch_newer_version(force=True)
        assert not outdated.check_scancode_version(force=True)


def test_fetch_newer_version_local_git_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '3.0.1': [],
            '3.1.2': [],
        }
    }

    def jget(*args, **kwargs):
        return pypi_mock_releases

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(
            json=jget,
            status_code=200
        )

        result = outdated.fetch_newer_version(
            installed_version='3.1.2.post351.850399bc3',
            force=True,
        )
        assert result == '3.1.2'

        result = outdated.check_scancode_version(
            installed_version='3.1.2.post351.850399bc3',
            force=True,
        )
        assert result
