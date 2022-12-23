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
from licensedcode.cache import LicenseCache
from licensedcode.cache import build_index
from licensedcode.cache import build_spdx_symbols
from licensedcode.cache import build_unknown_spdx_symbol
from licensedcode.cache import build_licensing
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


def get_index_with_test_rules(test_rules_dir):
    """
    Return and eventually build and cache a LicenseIndex from a directory with
    a few test rules for a specific test.
    """
    return MockCacheFromTestRules.build_from_test_rules(test_rules_dir).index


class MockCacheFromTestRules(LicenseCache):

    @staticmethod
    def build_from_test_rules(test_rules_dir):

        from licensedcode.models import licenses_data_dir as ldd
        from licensedcode.models import load_licenses

        licenses_data_dir = licenses_data_dir or ldd
        rules_data_dir = test_rules_dir

        licenses_db = load_licenses(licenses_data_dir=licenses_data_dir)

        index = build_index(
            licenses_db=licenses_db,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        spdx_symbols = build_spdx_symbols(licenses_db=licenses_db)
        unknown_spdx_symbol = build_unknown_spdx_symbol(licenses_db=licenses_db)
        licensing = build_licensing(licenses_db=licenses_db)

        license_cache = LicenseCache(
            db=licenses_db,
            index=index,
            licensing=licensing,
            spdx_symbols=spdx_symbols,
            unknown_spdx_symbol=unknown_spdx_symbol,
        )

        return license_cache
