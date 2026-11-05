#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import mock

from commoncode.fetch import ping_url


def test_ping_url_returns_true_when_url_is_reachable():
    with mock.patch("urllib.request.urlopen") as mock_urlopen:
        assert ping_url("http://example.com") is True
        mock_urlopen.assert_called_once_with("http://example.com")


def test_ping_url_returns_false_when_url_is_unreachable():
    with mock.patch("urllib.request.urlopen", side_effect=OSError):
        assert ping_url("http://example.com") is False
