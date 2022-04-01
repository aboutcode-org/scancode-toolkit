# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import xmltodict
import os
import json
import pytest
import xml.etree.ElementTree as ET

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

def test_xml():
    test_dir = test_env.get_test_loc('xml/simple')
    result_file = test_env.get_temp_file('xml')
    run_scan_click(['-clip', test_dir, '--xml', result_file])
    expected = test_env.get_test_loc('xml/simple-expected.xml')
    check_xml_scan(expected, result_file, regen=REGEN_TEST_FIXTURES)

@pytest.mark.scanslow
def test_scan_output_does_not_truncate_copyright_xml():
    test_dir = test_env.get_test_loc('xml/tree/scan/')
    result_file = test_env.get_temp_file('test.xml')
    run_scan_click(['-clip', '--strip-root', test_dir, '--xml', result_file])
    expected = test_env.get_test_loc('xml/tree/expected.xml')
    check_xml_scan(expected, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_for_timestamp():
    test_dir = test_env.get_test_loc('xml/simple')
    result_file = test_env.get_temp_file('xml')
    run_scan_click(['-clip', test_dir, '--xml', result_file])
    result_xml = json.loads(json.dumps((xmltodict.parse(open(result_file).read()))))
    header = result_xml['all']['headers']['item']
    assert 'start_timestamp' in header
    assert 'end_timestamp' in header


def check_xml_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check the scan `result_file` xml results against the `expected_file`
    expected xml results.

    If `regen` is True the expected_file WILL BE overwritten with the new scan
    results from `results_file`. This is convenient for updating tests
    expectations. But use with caution.
    """
    results = load_xml_results(result_file) or {}
    if regen:
        with open(expected_file, 'w') as reg:
            reg.write(ET.dump(results))

    expected = load_xml_results(expected_file)

    results.pop('headers', None)
    expected.pop('headers', None)

    # NOTE we redump this as a string for a more efficient display of the
    # failures comparison/diff
    expected = json.dumps(expected)
    results = json.dumps(results)
    assert results == expected

def load_xml_results(location):
    """
    Load the xml scan results file at `location`.
    To help with test resilience against small changes some attributes are
    removed or streamlined such as the  "tool_version" and scan "errors".
    Also date attributes from "files" and "headers" entries are removed.
    """
    with open(location, encoding='utf-8') as res:
        scan_results = convert_xml_to_dict(res)
    return cleanup_scan(scan_results, remove_file_date=True)


def cleanup_scan(scan_results, remove_file_date=False):
    """
    Cleanup in place the ``scan_results`` mapping for dates, headers and
    other variable data that break tests otherwise.
    """
    # clean new headers attributes
    streamline_headers(scan_results)
    # clean file_level attributes
    for scanned_file in scan_results['all']['files']['item'][0]['scan_errors']:
        streamline_scanned_file(scanned_file, remove_file_date)
    return scan_results


def streamline_errors(errors):
    """
    Modify the `errors` list in place to make it easier to test
    """
    for i, error in enumerate(errors[:]):
        error_lines = error.splitlines(True)
        if len(error_lines) <= 1:
            continue
        # keep only first and last line
        cleaned_error = ''.join([error_lines[0] + error_lines[-1]])
        errors[i] = cleaned_error


def streamline_headers(scan_results):
    """
    Modify the `headers` list of mappings in place to make it easier to test.
    """
    del scan_results['all']['headers']['item']['start_timestamp']
    del scan_results['all']['headers']['item']['end_timestamp']
    del scan_results['all']['headers']['item']['duration']
    del scan_results['all']['headers']['item']['options']


def streamline_scanned_file(scanned_file, remove_file_date=False):
    """
    Modify the `scanned_file` mapping for a file in scan results in place to
    make it easier to test.
    """
    streamline_errors(scanned_file)

def convert_xml_to_dict(xml_file):
    tree = ET.parse(xml_file)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
    return dict(xmltodict.parse(xmlstr))