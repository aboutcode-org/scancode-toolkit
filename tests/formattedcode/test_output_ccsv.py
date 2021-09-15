# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import csv
import io
import json
import os

import pytest

from commoncode.testcase import FileDrivenTesting
#from formattedcode.output_ccsv import flatten_scan
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

def check_csvs(result_file, expected_file,
               ignore_keys=('date', 'file_type', 'mime_type',),
               regen=False):
    """
    Load and compare two CSVs.
    `ignore_keys` is a tuple of keys that will be ignored in the comparisons.
    """
    result_fields, results = load_csv(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_csv(expected_file)
    assert result_fields == expected_fields
    # then check results line by line for more compact results
    for exp, res in zip(sorted(expected , key=lambda d: d.items()), sorted(results , key=lambda d: d.items())):
        for ign in ignore_keys:
            exp.pop(ign, None)
            res.pop(ign, None)
        assert res == exp

        
def load_csv(location):
    """
    Load a CSV file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    with io.open(location) as csvin:
        reader = csv.DictReader(csvin)
        fields = reader.fieldnames
        values = sorted(reader, key=lambda d: d.items())
        return fields, values

        

def test_can_process_live_scan_with_all_options():
    test_dir = test_env.get_test_loc('ccsv/livescan/scan')
    result_file = test_env.get_temp_file('csv')
    args = ['-lcpu', test_dir, '--ccsv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('ccsv/livescan/expected.csv')
    check_csvs(result_file, expected_file, regen=False)
