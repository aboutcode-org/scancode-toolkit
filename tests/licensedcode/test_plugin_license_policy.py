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
from licensedcode.plugin_license_policy import load_license_policy
from licensedcode.plugin_license_policy import get_duplicate_policies
from scancode.cli_test_utils import load_json_result
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_end_to_end_scan_with_license_policy():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_info_license_valid_policy_file.yml')
    result_file = test_env.get_temp_file('json')
    args = [
        '--info',
        '--license',
        '--license-policy',
        policy_file,
        test_dir,
        '--json-pp',
        result_file
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license_policy/policy-codebase.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)


def test_end_to_end_scan_with_license_policy_multiple_text():
    test_dir = test_env.get_test_loc('plugin_license_policy/file_with_multiple_licenses.txt')
    policy_file = test_env.get_test_loc('plugin_license_policy/sample_valid_policy_file.yml')
    result_file = test_env.get_temp_file('json')
    args = [
        '--info',
        '--license',
        '--license-policy',
        policy_file,
        test_dir,
        '--json-pp',
        result_file
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license_policy/file_with_multiple_licenses.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES, remove_file_date=True)


def test_process_codebase_info_license_duplicate_key_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_info_license_duplicate_key_policy_file.yml')

    result_file = test_env.get_temp_file('json')

    run_scan_click(['--info', '--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

    scan_result = load_json_result(result_file)

    for result in scan_result['files']:
        assert 'license_policy' in result.keys()
        assert result['license_policy'] == []


def test_process_codebase_info_license_valid_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_info_license_valid_policy_file.yml')

    result_file = test_env.get_temp_file('json')

    run_scan_click(['--info', '--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

    scan_result = load_json_result(result_file)

    for result in scan_result['files']:
        assert 'license_policy' in result.keys()

    approved, restricted = 0, 0
    for result in scan_result['files']:
        if result.get('license_policy') != []:
            if result.get('license_policy')[0].get('label') == "Approved License":
                approved += 1
            if result.get('license_policy')[0].get('label') == "Restricted License":
                restricted += 1

    assert approved == 1
    assert restricted == 4


def test_process_codebase_license_only_valid_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_license_only_valid_policy_file.yml')

    result_file = test_env.get_temp_file('json')

    run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

    scan_result = load_json_result(result_file)

    for result in scan_result['files']:
        assert 'license_policy' in result.keys()

    approved, restricted = 0, 0
    for result in scan_result['files']:
        if result.get('license_policy') != []:
            if result.get('license_policy')[0].get('label') == "Approved License":
                approved += 1
            if result.get('license_policy')[0].get('label') == "Restricted License":
                restricted += 1

    assert approved == 1
    assert restricted == 4


def test_process_codebase_info_only_valid_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_info_only_valid_policy_file.yml')

    result_file = test_env.get_temp_file('json')

    run_scan_click(['--info', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

    scan_result = load_json_result(result_file)

    for result in scan_result['files']:
        assert 'license_policy' in result.keys()

    for result in scan_result['files']:
        assert result.get('license_policy') == []


def test_process_codebase_empty_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_empty_policy_file.yml')

    result_file = test_env.get_temp_file('json')

    run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file])

    scan_result = load_json_result(result_file)

    for result in scan_result['files']:
        assert 'license_policy' in result.keys()

    for result in scan_result['files']:
        assert result.get('license_policy') == []


def test_process_codebase_invalid_policy_file():
    test_dir = test_env.extract_test_tar('plugin_license_policy/policy-codebase.tgz')
    policy_file = test_env.get_test_loc('plugin_license_policy/process_codebase_invalid_policy_file.yml')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['--license', '--license-policy', policy_file, test_dir, '--json-pp', result_file], expected_rc=2)


def test_get_duplicate_policies_with_dupes():
    test_file = test_env.get_test_loc('plugin_license_policy/get_duplicate_policies_invalid_dupes.yml')
    result = load_license_policy(test_file)
    policies = result.get('license_policies', [])
    expected = {
        'broadcom-commercial': [
            {'color_code': '#FFcc33',
             'icon': 'icon-warning-sign',
             'label': 'Restricted License',
             'license_key': 'broadcom-commercial'},
            {'color_code': '#008000',
             'icon': 'icon-ok-circle',
             'label': 'Approved License',
             'license_key': 'broadcom-commercial'},
        ],
    }
    assert get_duplicate_policies(policies) == expected


def test_get_duplicate_policies_with_no_dupes():
    test_file = test_env.get_test_loc('plugin_license_policy/get_duplicate_policies_valid.yml')
    result = load_license_policy(test_file)
    policies = result.get('license_policies', [])
    assert get_duplicate_policies(policies) == {}


def test_get_duplicate_policies_empty():
    test_file = test_env.get_test_loc('plugin_license_policy/get_duplicate_policies_empty.yml')
    result = load_license_policy(test_file)
    policies = result.get('license_policies', [])
    assert get_duplicate_policies(policies) == []


def test_load_license_policy_with_duplicate_keys():
    test_file = test_env.get_test_loc('plugin_license_policy/load_license_policy_duplicate_keys.yml')

    expected = dict([
        ('license_policies', [
            dict([
                ('license_key', 'broadcom-commercial'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'bsd-1988'),
                ('label', 'Approved License'),
                ('color_code', '#008000'),
                ('icon', 'icon-ok-circle'),
            ]),
            dict([
                ('license_key', 'esri-devkit'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'oracle-java-ee-sdk-2010'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'rh-eula'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'broadcom-commercial'),
                ('label', 'Approved License'),
                ('color_code', '#008000'),
                ('icon', 'icon-ok-circle'),
            ]),
        ])
    ])

    result = load_license_policy(test_file)
    assert result == expected


def test_load_license_policy_simple():
    test_file = test_env.get_test_loc('plugin_license_policy/load_license_policy_valid.yml')

    expected = dict([
        ('license_policies', [
            dict([
                ('license_key', 'broadcom-commercial'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'bsd-1988'),
                ('label', 'Approved License'),
                ('color_code', '#008000'),
                ('icon', 'icon-ok-circle'),
            ]),
            dict([
                ('license_key', 'esri-devkit'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'oracle-java-ee-sdk-2010'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
            dict([
                ('license_key', 'rh-eula'),
                ('label', 'Restricted License'),
                ('color_code', '#FFcc33'),
                ('icon', 'icon-warning-sign'),
            ]),
        ])
    ])

    result = load_license_policy(test_file)

    assert result == expected


def test_load_license_policy_empty():
    test_file = test_env.get_test_loc('plugin_license_policy/load_license_policy_empty.yml')
    result = load_license_policy(test_file)
    assert result == {'license_policies': []}


def test_load_license_policy_invalid():
    test_file = test_env.get_test_loc('plugin_license_policy/load_license_policy_invalid.yml')
    with pytest.raises(Exception):
        load_license_policy(test_file)


def test_load_license_policy_invalid2():
    test_file = test_env.get_test_loc('plugin_license_policy/get_duplicate_policies_invalid_no_dupes.yml')
    with pytest.raises(Exception):
        load_license_policy(test_file)


faulty_policy_yaml = [
    ('plugin_license_policy/various-inputs/not-a-json-but-png.json', 2, "Error: Invalid value for '--license-policy': policy file is not a well formed or readable YAML file:"),
    ('plugin_license_policy/various-inputs/not-a-yaml-but-png.yaml', 2, "Error: Invalid value for '--license-policy': policy file is not a well formed or readable YAML file:"),
    ('plugin_license_policy/various-inputs/png.png', 2, "Error: Invalid value for '--license-policy': policy file is not a well formed or readable YAML file:"),
    ('plugin_license_policy/various-inputs/true-json.json', 2, "Error: Invalid value for '--license-policy': policy file is missing a 'license_policies' attribute"),
    ('plugin_license_policy/various-inputs/true-yaml.yaml', 2, "Error: Invalid value for '--license-policy': policy file is missing a 'license_policies' attribute"),
    ('plugin_license_policy/various-inputs/true-yaml.yml', 2, "Error: Invalid value for '--license-policy': policy file is missing a 'license_policies' attribute"),
]


@pytest.mark.parametrize('test_policy, expected_rc, expected_message', faulty_policy_yaml)
def test_scan_does_validate_input_and_fails_on_faulty_policy_input(test_policy, expected_rc, expected_message):
    test_input = test_env.get_test_loc('plugin_license_policy/various-inputs/true-scan-json.json')
    test_policy = test_env.get_test_loc(test_policy)
    result = run_scan_click([
            '--from-json',
            test_input,
            '--json-pp',
            '-',
            '--license-policy',
            test_policy,
        ],
        expected_rc=expected_rc,
        retry=False,
    )
    assert expected_message in result.output


def test_scan_does_validate_input_and_does_not_fail_on_valid_policy_input():
    test_input = test_env.get_test_loc('plugin_license_policy/various-inputs/true-scan-json.json')
    test_policy = test_env.get_test_loc('plugin_license_policy/various-inputs/true-yaml-license-policy-yaml.yml')
    run_scan_click(
        [
            '--from-json',
            test_input,
            '--json-pp',
            '-',
            '--license-policy',
            test_policy,
        ],
        retry=False,
    )

