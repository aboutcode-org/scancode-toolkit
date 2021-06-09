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
from docx import Document

from commoncode.testcase import FileDrivenTesting
#from formattedcode.output_ccsv import flatten_scan
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

def check_docs(result_file, expected_file,
               regen=False):
    """
    Load and compare two DOCs.
    """
    result_fields, results = load_doc(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_doc(expected_file)
    assert result_fields == expected_fields
    assert res == exp

        
def load_doc(location):
    """
    Load a DOC file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    document = Document(location)
    for table in document.tables:
        count = 0
        for row in table.rows:
            for cell in row.cells:
                if count==0:
                    fields.append(cell.text)
                else:
                    values.append(cell.text)
            count=count+1
    return fields, values

        

def test_can_process_live_scan_with_all_options():
    test_dir = test_env.get_test_loc('doc/livescan/scan')
    result_file = test_env.get_temp_file('doc')
    args = ['-lcpu', test_dir, '--doc', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('doc/livescan/expected.doc')
    check_docs(result_file, expected_file, regen=False)
