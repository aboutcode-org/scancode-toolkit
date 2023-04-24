#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


import os

from commoncode.testcase import FileBasedTesting
from licensedcode.index import LicenseIndex
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from licensedcode.query import build_query

from licensedcode.models import load_licenses
from licensedcode.models import get_rules
from licensedcode.models import get_all_spdx_key_tokens
from licensedcode.models import get_license_tokens

from licensedcode.match_unknown import match_unknowns
from licensedcode.match_unknown import MATCH_UNKNOWN
from licensedcode.detection import LicenseMatchFromResult

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestUnknownLicenses(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_unknowns_works(self):
        rule_dir = self.get_test_loc('match_unknown/index_mini/rules/')
        license_dir = self.get_test_loc('match_unknown/index_mini/licenses/')
        licenses_db = load_licenses(license_dir)
        rules = list(get_rules(licenses_db=licenses_db, rules_data_dir=rule_dir))
        spdx_tokens = set(get_all_spdx_key_tokens(licenses_db))
        license_tokens = set(get_license_tokens())
        idx = LicenseIndex(
            rules=rules,
            _spdx_tokens=spdx_tokens,
            _license_tokens=license_tokens,
        )

        query_loc = self.get_test_loc('match_unknown/apache-2.0.LICENSE')
        qry = build_query(location=query_loc, idx=idx)

        match = match_unknowns(
            idx=idx,
            query_run=qry.whole_query_run(),
            automaton=idx.unknown_automaton,
        )
        match.set_lines(qry.line_by_pos)

        assert match.matcher == MATCH_UNKNOWN
        assert match.matched_text()

        assert LicenseMatchFromResult.from_dict(match.to_dict())

    def test_unknown_licenses_works(self):
        test_dir = self.get_test_loc('match_unknown/unknown.txt', copy=True)
        result_file = self.get_temp_file('json')
        args = [
            '--license',
            '--unknown-licenses',
            '--strip-root',
            '--verbose',
            '--json', result_file,
            test_dir,
        ]
        run_scan_click(args)
        test_loc = self.get_test_loc('match_unknown/unknown-license-expected.json')
        check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

    def test_unknown_licenses_works_with_license_text(self):
        test_dir = self.get_test_loc('match_unknown/unknown.txt', copy=True)
        result_file = self.get_temp_file('json')
        args = [
            '--license',
            '--license-text',
            '--license-text-diagnostics',
            '--license-diagnostics',
            '--unknown-licenses',
            '--strip-root',
            '--verbose',
            '--json', result_file,
            test_dir,
        ]
        run_scan_click(args)
        test_loc = self.get_test_loc('match_unknown/unknown-license-text-expected.json')
        check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

