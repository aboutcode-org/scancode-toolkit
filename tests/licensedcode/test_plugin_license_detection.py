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

from licensedcode.detection import find_referenced_resources
from licensedcode.plugin_license import find_referenced_resource
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_complicated_license_text_from_ffmpeg():
    test_dir = test_env.get_test_loc('plugin_license/scan/ffmpeg-LICENSE.md')
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


def test_license_match_free_unknown_license_intro():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-free-unknown-intro/')
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
    test_loc = test_env.get_test_loc('plugin_license/unknown_intro/scan-free-unknown-intro.expected.json')
    check_json_scan(test_loc, result_file, regen=True)



def test_license_match_unknown_license_intro_with_imperfect_matches():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-with-imperfect-matches/')
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
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-dual-license/')
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
    test_dir = test_env.get_test_loc('plugin_license/clues/woodstox/')
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


def test_license_match_extra_words_3_seq():
    test_dir = test_env.get_test_loc('plugin_license/extra-words/scan-extra-words-3-seq-license/')
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
    test_loc = test_env.get_test_loc('plugin_license/extra-words/scan-extra-words-3-seq-license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_extra_words_2_aho():
    test_dir = test_env.get_test_loc('plugin_license/extra-words/scan-extra-words-2-aho-license/')
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
    test_loc = test_env.get_test_loc('plugin_license/extra-words/scan-extra-words-2-aho-license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_intro_eclipse_foundation():
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation/')
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
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-eclipse-foundation-tycho/')
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
    test_dir = test_env.get_test_loc('plugin_license/unknown_intro/scan-unknown-intro-long-gaps-between/')
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
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/unknown-ref-to-key-file-root')
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
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref')
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


def test_license_detection_with_ignorable_reference_different_expression():
    test_dir = test_env.get_test_loc('plugin_license/ignored_reference/or_and_problem/')
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
    test_loc = test_env.get_test_loc('plugin_license/ignored_reference/or_and_problem.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_match_unknown_license_without_license_reference():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/license-ref-see-copying')
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
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-without-ref')
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
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-unknown-reference-copyright')
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


def test_license_match_referenced_filename_generic():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/cairo-1.18.4/')
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
    test_loc = test_env.get_test_loc('plugin_license/license_reference/scan-unknown-reference-generic.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_find_referenced_resource():
    # Setup: Create a new scan to use for a virtual codebase
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref')
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
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref-dupe-name-suffix')
    scan_loc = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--license-text-diagnostics', test_dir, '--json', scan_loc]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource(path='scan-ref-dupe-name-suffix/license-notice.txt')
    result = find_referenced_resource(referenced_filename='LICENSE', resource=resource, codebase=codebase)
    assert result.path == 'scan-ref-dupe-name-suffix/LICENSE'


def test_find_referenced_resources_with_directory_glob():
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref-glob')
    scan_loc = test_env.get_temp_file('json')
    args = ['--license', '--json', scan_loc, test_dir]
    run_scan_click(args)

    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(scan_loc)
    resource = codebase.get_resource(path='scan-ref-glob/license-notice.txt')
    results = find_referenced_resources(
        referenced_filename='licenses/*',
        resource=resource,
        codebase=codebase,
        find_referenced_resource_func=find_referenced_resource,
    )

    assert [result.path for result in results] == [
        'scan-ref-glob/licenses/COPYING',
        'scan-ref-glob/licenses/LICENSE',
    ]


def test_match_reference_license():
    # Setup: Create a new scan to use for a virtual codebase
    test_dir = test_env.get_test_loc('plugin_license/license_reference/scan/scan-ref')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)

    # test proper
    from commoncode.resource import VirtualCodebase
    codebase = VirtualCodebase(result_file)
    resource = codebase.get_resource(path='scan-ref/license-notice.txt')
    assert len(resource.license_detections[0]["matches"]) == 1

    expected_loc = test_env.get_test_loc(
        'plugin_license/license_reference/scan/scan-ref.expected.json',
        must_exist=False,
    )
    check_json_scan(expected_loc, result_file, regen=REGEN_TEST_FIXTURES)
