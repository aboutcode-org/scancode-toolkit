#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packages_test_utils import PackageTester
from packagedcode import citation
from scancode_config import REGEN_TEST_FIXTURES


class TestCitation(PackageTester):
    #test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_cff_data(self):
        test_file = self.get_test_loc('citation/CITATION.cff')
        results = citation.get_cff_data(test_file)
        assert  list(results.items())[0] == ((u'cff-version', u'1.2.0')) \
                and (list(results.items())[8]) == (u'doi',
                u'10.5281/zenodo.1184077')

    def test_citationcff_is_package_data_file(self):
        test_file = self.get_test_loc('citation/CITATION.cff')
        assert citation.CitationHandler.is_datafile(test_file)

    def test_parse(self):
        test_file = self.get_test_loc('citation/CITATION.cff')
        package = citation.CitationHandler.parse(test_file)
        expected_loc = self.get_test_loc('citation/citation.cff.expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)
