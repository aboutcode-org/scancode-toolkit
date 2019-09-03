#
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
from __future__ import division
from __future__ import unicode_literals



import pytest

from commoncode.system import py3
from scancode import outdated


pytestmark = pytest.mark.skipif(not py3, reason='Mock is not available as a builtin on py2')


def test_get_latest_version():
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
        result = outdated.get_latest_version()
        assert '3.0.2' == result


def test_get_latest_version_fails_on_http_error():
    from unittest import mock
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = mock.Mock(status_code=400)
        with pytest.raises(Exception):
            outdated.get_latest_version()


def test_get_latest_version_ignore_rc_versions():
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
        result = outdated.get_latest_version()
        assert '2.2.1' == result


def test_check_scancode_version():
    from unittest import mock
    pypi_mock_releases = {
        'releases': {
            '2.0.0': [],
            '2.0.0rc3': [],
            '2.0.1': [],
            '2.1.0': [],
            '3.4.1': [],
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
        expected1 = 'You are using ScanCode Toolkit version'
        expected2 = 'however the newer version 3.4.1 is available'
        result = outdated.check_scancode_version(force=True)
        assert expected1 in result
        assert expected2 in result


def test_check_scancode_version_no_new_version():
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
        result = outdated.check_scancode_version(force=True)
        assert not result
