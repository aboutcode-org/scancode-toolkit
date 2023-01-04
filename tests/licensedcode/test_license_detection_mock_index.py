#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import shutil

from commoncode.testcase import FileBasedTesting

from licensedcode.index import LicenseIndex
from licensedcode.models import load_rules
from packagedcode.licensing import get_license_detection_mappings
from scancode.cli_test_utils import check_json
from scancode_config import REGEN_TEST_FIXTURES


class TestLicenseMatchBasic(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/plugin_license/mock_index/')

    def test_detection_with_mock_index_with_rule_folder(self):
        rule_dir = self.get_test_loc('scan-unknown-intro-eclipse-foundation-rules')
        index = LicenseIndex(load_rules(rule_dir))

        test_loc = self.get_test_loc('scan-unknown-intro-eclipse-foundation/README.md')
        results = get_license_detection_mappings(index=index, location=test_loc)

        expected = self.get_test_loc('scan-unknown-intro-eclipse-foundation.expected.json')
        check_json(expected, results, regen=REGEN_TEST_FIXTURES)
    

    def test_detection_with_mock_index_with_rule_name_list(self):
        rule_names = [
            "license-intro_29.RULE",
            "epl-2.0_30.RULE",
            "epl-2.0_2.RULE"
        ]
        temp_dir = self.get_temp_dir('mock_rules')
        index = LicenseIndex(get_rules_from_rule_names(rule_names, temp_dir))

        test_loc = self.get_test_loc('scan-unknown-intro-eclipse-foundation/README.md')
        results = get_license_detection_mappings(index=index, location=test_loc)

        expected = self.get_test_loc('scan-unknown-intro-eclipse-foundation.expected.json')
        check_json(expected, results, regen=REGEN_TEST_FIXTURES)


def get_rules_from_rule_names(rule_names, temp_dir):

    from licensedcode.models import rules_data_dir

    for rule_name in rule_names:
        rule_path = rules_data_dir + '/' + rule_name
        shutil.copy(rule_path, temp_dir)

    return load_rules(temp_dir)
