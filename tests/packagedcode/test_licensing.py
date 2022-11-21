#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import TestCase

from packagedcode.licensing import get_only_expression_from_extracted_license


class TestLicensing(TestCase):
    def test_get_only_expression_from_extracted_license(self):
        assert get_only_expression_from_extracted_license('mit') == 'mit'
        assert get_only_expression_from_extracted_license('mit or Apache-2.0') == 'mit OR apache-2.0'
        # TODO: Fix this
        assert get_only_expression_from_extracted_license('mit or asasa or Apache-2.0') == 'apache-2.0'
        assert get_only_expression_from_extracted_license('mit asasa or Apache-2.0') == 'mit OR apache-2.0'
        assert get_only_expression_from_extracted_license('') is None
        assert get_only_expression_from_extracted_license(None) is None
