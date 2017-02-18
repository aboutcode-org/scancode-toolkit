#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

import os

import click
from click.testing import CliRunner

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_scan

from scancode import cli


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""

def test_json_pretty_print_option(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('json-option', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--format', 'json-pp', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10
    assert len(open(result_file).readlines()) > 1


def test_json_output_option_is_minified(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('json-option', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--format', 'json', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10
    assert len(open(result_file).readlines()) == 1


def test_paths_are_posix_paths_in_html_app_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file(extension='html', file_name='test_html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html-app', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    # the data we want to test is in the data.json file
    data_file = os.path.join(fileutils.parent_directory(result_file), 'test_html_files', 'data.json')
    assert 'copyright_acme_c-c.c' in open(data_file).read()


def test_paths_are_posix_in_html_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in open(result_file).read()


def test_paths_are_posix_in_json_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'json', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in open(result_file).read()


def test_format_with_custom_filename_fails_for_directory(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('html')
    result = runner.invoke(cli.scancode, [ '--format', test_dir, test_dir, result_file], catch_exceptions=True)
    assert result.exit_code != 0
    assert 'Invalid template file' in result.output


def test_format_with_custom_filename(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    template = test_env.get_test_loc('template/sample-template.html')
    result_file = test_env.get_temp_file('html')
    result = runner.invoke(cli.scancode, [ '--format', template, test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Custom Template' in open(result_file).read()


def test_scanned_path_is_present_in_html_app_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('html_app')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html-app', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    html_file = open(result_file).read()
    assert '<title>ScanCode scan results for: %(test_dir)s</title>' % locals() in html_file
    assert 'ScanCode</a> scan results for: %(test_dir)s</span>' % locals() in html_file


def test_scan_html_output_does_not_truncate_copyright(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('do_not_truncate_copyright/scan/')
    runner = CliRunner()
    json_result_file = test_env.get_temp_file('test.json')
    json_result = runner.invoke(cli.scancode, [ '-clip', '--format', 'json', test_dir, json_result_file], catch_exceptions=True)
    assert json_result.exit_code == 0
    assert 'Scanning done' in json_result.output
    expected_json = test_env.get_test_loc('do_not_truncate_copyright/expected.json')

    check_scan(test_env.get_test_loc(expected_json), json_result_file, strip_dates=True, regen=False)

    html_result_file = test_env.get_temp_file('test.html')
    html_result = runner.invoke(cli.scancode, [ '-clip', '--format', 'html', '-n', '3', test_dir, html_result_file], catch_exceptions=True)
    assert html_result.exit_code == 0
    assert 'Scanning done' in html_result.output

    with open(html_result_file) as hi:
        html_result_text = hi.read()
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

    # for this test we build regexes from a template so we can abstract whitespaces
    import re
    for scanned_file in expected_files:
        exp = expected_template % (scanned_file,)
        exp = r'\s*'.join(exp.split())
        check = re.findall(exp, html_result_text, re.MULTILINE)
        assert check
