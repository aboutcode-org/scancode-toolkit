#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packagedcode.pip_cache import parse_pip_cache


def test_parse_pip_cache():
    """Test parsing a pip cache directory with origin.json."""
    result = parse_pip_cache("tests/data/pip_cache_sample")

    assert result is not None
    assert result["type"] == "pypi"
    assert "pythonhosted" in result["download_url"]