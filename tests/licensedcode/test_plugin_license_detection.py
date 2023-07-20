#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileDrivenTesting

from licensedcode.plugin_license import find_referenced_resource
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_complicated_license_text_from_ffmpeg():
    test_dir = test_env.get_test_loc('plugin_license/scan/ffmpeg-LICENSE.md', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/scan/ffmpeg-license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_with_imperfect_matches():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-with-imperfect-matches/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-with-imperfect-matches.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_with_dual_license():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-dual-license/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-dual-license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_clues_is_not_in_expression():
    test_dir = test_env.get_test_loc('plugin_license/clues/woodstox/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--license-references',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/clues/woodstox.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_eclipse_foundation():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_eclipse_foundation_tycho():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation-tycho/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation-tycho.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_with_long_gaps_between():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-long-gaps-between/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-long-gaps-between.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_with_license_ref_to_key_file_at_root():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/unknown-ref-to-key-file-root', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/unknown-ref-to-key-file-root.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_with_license_reference():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-ref.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_without_license_reference():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/license-ref-see-copying', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
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
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-wref.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_referenced_filename_unknown_ref():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-unknown-reference-copyright', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-unknown-reference-copyright.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_find_referenced_resource():
    # Setup: Create a new scan to use for a virtual codebase
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref', copy=True)
    scan_loc = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--json', scan_loc,
        test_dir,
    ]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource(path='scan-ref/license-notice.txt')
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
    resource = codebase.get_resource(path='scan-ref-dupe-name-suffix/license-notice.txt')
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
        '--license-diagnostics',
        '--json', scan_loc,
        test_dir,
    ]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource(path='scan-ref/license-notice.txt')
    assert len(resource.license_detections[0]["matches"]) == 2
