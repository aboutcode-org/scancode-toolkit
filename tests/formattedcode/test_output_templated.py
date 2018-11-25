# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import io
import os
import re

from scancode_config import __version__

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting
from formattedcode.output_html import HtmlOutput
from scancode.cli_test_utils import run_scan_click
from scancode.resource import VirtualCodebase


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_paths_are_posix_paths_in_html_app_format_output():
    test_dir = test_env.get_test_loc('templated/simple')
    result_file = test_env.get_temp_file(extension='html', file_name='test_html')
    run_scan_click(['--copyright', test_dir, '--html-app', result_file])
    # the data we want to test is in the data.js file
    data_file = os.path.join(fileutils.parent_directory(result_file), 'test_html_files', 'data.js')
    with io.open(data_file, encoding='utf-8') as res:
        results = res.read()
    assert '/copyright_acme_c-c.c' in results
    results = open(result_file).read()
    assert __version__ in results


def test_paths_are_posix_in_html_format_output():
    test_dir = test_env.get_test_loc('templated/simple')
    result_file = test_env.get_temp_file('html')
    run_scan_click(['--copyright', test_dir, '--html', result_file])
    results = open(result_file).read()
    assert '/copyright_acme_c-c.c' in results
    assert __version__ in results


def test_scanned_path_is_present_in_html_app_output():
    test_dir = test_env.get_test_loc('templated/html_app')
    result_file = test_env.get_temp_file('test.html')
    run_scan_click(['--copyright', '--html-app', result_file, test_dir])
    results = open(result_file).read()
    assert '<title>ScanCode scan results for: %(test_dir)s</title>' % locals() in results
    assert '<div class="row" id = "scan-result-header">' % locals() in results
    assert '<strong>scan results for:</strong>' % locals() in results
    assert '<p>%(test_dir)s</p>' % locals() in results
    assert __version__ in results


def test_scan_html_output_does_not_truncate_copyright_html():
    test_dir = test_env.get_test_loc('templated/tree/scan/')
    result_file = test_env.get_temp_file('test.html')

    args = ['-clip', '--strip-root', '--verbose', test_dir, '--html', result_file, '--verbose']

    run_scan_click(args)
    results = open(result_file).read()
    assert __version__ in results

    expected_template = r'''
        <tr>
          <td>%s</td>
          <td>1</td>
          <td>1</td>
          <td>copyright</td>
            <td>Copyright \(c\) 2000 ACME, Inc\.</td>
        </tr>
    '''

    expected_files = r'''
        copy1.c
        copy2.c
        subdir/copy1.c
        subdir/copy4.c
        subdir/copy2.c
        subdir/copy3.c
        copy3.c
    '''.split()

    # for this test we build regexes from a template so we can abstract
    # whitespaces
    for scanned_file in expected_files:
        exp = expected_template % (scanned_file,)
        exp = r'\s*'.join(exp.split())
        check = re.findall(exp, results, re.MULTILINE)
        assert check


def test_custom_format_with_custom_filename_fails_for_directory():
    test_dir = test_env.get_temp_dir('html')
    result_file = test_env.get_temp_file('html')
    args = ['--info', '--custom-template', test_dir, '--custom-output', result_file, test_dir]
    result = run_scan_click(args, expected_rc=2)
    assert 'Invalid value for "--custom-template": Path' in result.output


def test_custom_format_with_custom_filename():
    test_dir = test_env.get_test_loc('templated/simple')
    custom_template = test_env.get_test_loc('templated/sample-template.html')
    result_file = test_env.get_temp_file('html')
    args = ['--info', '--custom-template', custom_template, '--custom-output', result_file, test_dir]
    run_scan_click(args)
    results = open(result_file).read()
    assert 'Custom Template' in results
    assert __version__ in results


def test_HtmlOutput_process_codebase_fails_with_non_ascii_scanned_paths_and_file_opened_in_binary_mode():
    test_scan = '''{
          "scancode_notice": "Generated with ScanCode...",
          "scancode_version": "2.9.7.post137.2e29fe3.dirty.20181120225811",
          "scancode_options": {
            "input": "han/",
            "--json-pp": "-"
          },
          "scan_start": "2018-11-23T123252.191917",
          "files_count": 1,
          "files": [
            {
              "path": "han",
              "type": "directory",
              "scan_errors": []
            },
            {
              "path": "han/\u636e.svg",
              "type": "file",
              "scan_errors": []
            }
          ]
        }'''
    codebase = VirtualCodebase(test_scan)
    result_file = test_env.get_temp_file('html')
    ho = HtmlOutput()
    try:
        with open(result_file, 'wb') as html:
            ho.process_codebase(codebase, html)
        raise Exception('Exception not raised.')
    except Exception as e:
        assert 'UnicodeEncodeError' in str(e)


def test_HtmlOutput_process_codebase_does_not_fail_with_non_ascii_scanned_paths_and_file_opened_in_text_mode_with_utf():
    test_scan = '''{
          "scancode_notice": "Generated with ScanCode...",
          "scancode_version": "2.9.7.post137.2e29fe3.dirty.20181120225811",
          "scancode_options": {
            "input": "han/",
            "--json-pp": "-"
          },
          "scan_start": "2018-11-23T123252.191917",
          "files_count": 1,
          "files": [
            {
              "path": "han",
              "type": "directory",
              "scan_errors": []
            },
            {
              "path": "han/\u636e.svg",
              "type": "file",
              "scan_errors": []
            }
          ]
        }'''
    codebase = VirtualCodebase(test_scan)
    result_file = test_env.get_temp_file('html')
    ho = HtmlOutput()
    with io.open(result_file, 'w', encoding='utf-8') as html:
        ho.process_codebase(codebase, html)
    results = io.open(result_file, encoding='utf-8').read()
    assert '<td>han/据.svg</td>' in results


def test_html_output_can_handle_non_ascii_paths():
    test_file = test_env.get_test_loc('unicode.json')
    result_file = test_env.get_temp_file(extension='html', file_name='test_html')
    run_scan_click(['--from-json', test_file, '--html', result_file])

    with io.open(result_file) as res:
        results = res.read()

    assert '<td>han/据.svg</td>' in results


def test_custom_html_output_can_handle_non_ascii_paths():
    test_file = test_env.get_test_loc('unicode.json')
    result_file = test_env.get_temp_file(extension='html', file_name='test_html')
    custom_template = test_env.get_test_loc('templated/sample-template.html')

    args = [
        '--from-json', test_file, 
        '--custom-template', custom_template, 
        '--custom-output', result_file
    ]
    run_scan_click(args)

    with io.open(result_file) as res:
        results = res.read()

    assert '<td>han/据.svg</td>' in results
