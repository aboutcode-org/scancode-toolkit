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

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_license_reference_detection_in_manifest_unknown():
    test_dir = test_env.get_test_loc('license_detection/reference-at-manifest/flutter_playtabs_bridge/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-at-manifest/flutter_playtabs_bridge.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_known():
    test_dir = test_env.get_test_loc('license_detection/reference-at-manifest/nanopb/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-at-manifest/nanopb.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_unknown_reference_nuget():
    test_dir = test_env.get_test_loc('license_detection/reference-at-manifest/fizzler/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-at-manifest/fizzler.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_licence_comment():
    test_dir = test_env.get_test_loc('license_detection/license-as-manifest-comment/activemq-camel/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/license-as-manifest-comment/activemq-camel.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_siblings():
    test_dir = test_env.get_test_loc('license_detection/license-beside-manifest/google-built-collection/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/license-beside-manifest/google-built-collection.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_unknown_without_license():
    test_dir = test_env.get_test_loc('license_detection/reference-at-manifest/flutter_playtabs_bridge/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-at-manifest/flutter_playtabs_bridge_without_license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_known_without_license():
    test_dir = test_env.get_test_loc('license_detection/reference-at-manifest/nanopb/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-at-manifest/nanopb_without_license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_licence_comment_without_license():
    test_dir = test_env.get_test_loc('license_detection/license-as-manifest-comment/activemq-camel/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/license-as-manifest-comment/activemq-camel_without_license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_detection_in_manifest_siblings_without_license():
    test_dir = test_env.get_test_loc('license_detection/license-beside-manifest/google-built-collection/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/license-beside-manifest/google-built-collection_without_license.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

def test_license_reference_to_unknown_package_complex_package():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/google_appengine_sdk/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/google_appengine_sdk.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

def test_license_reference_to_unknown_package_simple():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/base-example/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/base.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

def test_license_reference_to_unknown_package_with_detected_package():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/samba/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/samba.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_to_unknown_package_paddlenlp():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/paddlenlp/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/paddlenlp.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_reference_to_unknown_package_without_detected_package():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/physics/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/physics.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

# ToDo: include licenses from parsing debian copyright files and derefernce this
def test_license_reference_to_unknown_package_special_case_debian():
    test_dir = test_env.get_test_loc('license_detection/reference-to-package/fusiondirectory/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/reference-to-package/fusiondirectory.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_package_multi_flavored():
    test_dir = test_env.get_test_loc('license_detection/multi-flavor/jquery-form-3.51.0/')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--package',
        '--strip-root',
        '--verbose',
        '--summary',
        '--classify',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('license_detection/multi-flavor/jquery-form-3.51.0.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)
