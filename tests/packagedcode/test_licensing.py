#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import TestCase

from packagedcode.licensing import get_normalized_expression


class TestLicensing(TestCase):
    def test_get_normalized_expression(self):
        assert get_normalized_expression('mit') == 'mit'
        assert get_normalized_expression('mit or asasa or Apache-2.0') == 'apache-2.0 AND unknown'
        assert get_normalized_expression('mit or asasa or Apache-2.0') == 'apache-2.0 AND unknown'
        assert get_normalized_expression('mit asasa or Apache-2.0') == 'mit OR apache-2.0'
        assert get_normalized_expression('') is None
        assert get_normalized_expression(None) is None
