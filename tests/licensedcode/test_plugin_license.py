#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest
from commoncode.testcase import FileDrivenTesting

from licensedcode.plugin_license import add_referenced_filenames_license_matches
from licensedcode.plugin_license import find_referenced_resource
from licensedcode.plugin_license import get_referenced_filenames
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

"""
These tests spawn new process as if launched from the command line.
"""


def test_license_option_reports_license_expressions():
    test_dir = test_env.get_test_loc('plugin_license/license-expression/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license-expression/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]

    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_diag():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_diag_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_with_license_reference():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--strip-root',
        '--verbose',
        '--unknown-licenses',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-ref.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.xfail(reason="Set as failing until we have proper LicenseDetection support")
def test_license_match_unknown_license_without_license_reference():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/license-ref-see-copying', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--strip-root',
        '--verbose',
        '--unknown-licenses',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/license-ref-see-copying.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_referenced_filename():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-without-ref', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--strip-root',
        '--verbose',
        '--unknown-licenses',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-wref.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_get_referenced_filenames():
    license_matches = [
        {'matched_rule': {'referenced_filenames' : ['LICENSE.txt', 'COPYING']}},
        {'matched_rule': {'referenced_filenames' : ['COPYING', 'LICENSE.txt']}},
        {'matched_rule': {'referenced_filenames' : ['copying']}},
        {'matched_rule': {'referenced_filenames' : []}},
    ]
    expected = ['LICENSE.txt', 'COPYING', 'copying']
    assert get_referenced_filenames(license_matches) == expected


def test_find_referenced_resource():
    # Setup: Create a new scan to use for a virtual codebase
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref', copy=True)
    scan_loc = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--unknown-licenses',
        '--json', scan_loc,
        test_dir,
    ]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource('scan-ref/license-notice.txt')
    result = find_referenced_resource(referenced_filename='LICENSE', resource=resource, codebase=codebase)
    assert result.path == 'scan-ref/LICENSE'


def test_find_referenced_resource_does_not_find_based_file_name_suffix():
    # Setup: Create a new scan to use for a virtual codebase. This directory has
    # two test file with the same name suffix which is also a referenced
    # filename
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref-dupe-name-suffix', copy=True)
    scan_loc = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--license-text-diagnostics', test_dir, '--json', scan_loc]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource('scan-ref-dupe-name-suffix/license-notice.txt')
    result = find_referenced_resource(referenced_filename='LICENSE', resource=resource, codebase=codebase)
    assert result.path == 'scan-ref-dupe-name-suffix/LICENSE'


def test_match_reference_license():
    # Setup: Create a new scan to use for a virtual codebase
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref', copy=True)
    scan_loc = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--unknown-licenses',
        '--json', scan_loc,
        test_dir,
    ]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource('scan-ref/license-notice.txt')
    assert len(resource.licenses) == 2
    result = add_referenced_filenames_license_matches(resource=resource, codebase=codebase)
    assert len(result.licenses) == 3


def test_reindex_licenses_works():
    from licensedcode.cache import get_index
    get_index(force=True)
    get_index(force=True, index_all_languages=True)


@pytest.mark.scanslow
def test_scan_license_with_url_template():
    test_dir = test_env.get_test_loc('plugin_license/license_url/scan/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-url-template', 'https://example.com/urn:{}',
        '--unknown-licenses',
        '--json-pp', result_file,
        test_dir,
    ]
    test_loc = test_env.get_test_loc('plugin_license/license_url/license_url.expected.json')
    run_scan_click(args)
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_detection_does_not_timeout_on_sqlite3_amalgamation():
    test_dir = test_env.extract_test_tar('plugin_license/sqlite/sqlite.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/sqlite/sqlite.expected.json')
    # we use the default 120 seconds timeout
    run_scan_click(['-l', '--license-text', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_detection_is_correct_in_legacy_npm_package_json():
    test_dir = test_env.get_test_loc('plugin_license/package/package.json')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/package/package.expected.json')
    run_scan_click(['-lp', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
