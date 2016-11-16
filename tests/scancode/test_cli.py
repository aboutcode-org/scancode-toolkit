#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import codecs
from collections import OrderedDict
import json
import os

import click
from click.testing import CliRunner

from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.testcase import FileDrivenTesting

from scancode import cli


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""


def check_scan(expected_file, result_file, test_dir, regen=False):
    """
    Check the scan result_file JSON results against the expected_file expected JSON
    results. Removes references to test_dir for the comparison. If regen is True the
    expected_file WILL BE overwritten with the results. This is convenient for
    updating tests expectations. But use with caution.
    """
    result = _load_json_result(result_file, test_dir)
    if regen:
        with open(expected_file, 'wb') as reg:
            json.dump(result, reg, indent=2)
    expected = _load_json_result(expected_file, test_dir)
    # NOTE we redump the JSON as a string for a more efficient comparison of
    # failures
    expected = json.dumps(expected, indent=2, sort_keys=True)
    result = json.dumps(result, indent=2, sort_keys=True)
    assert expected == result


def _load_json_result(result_file, test_dir):
    """
    Load the result file as utf-8 JSON and strip test_dir prefix from
    locations.
    Sort the results by location.
    """
    test_dir = as_posixpath(test_dir)
    with codecs.open(result_file, encoding='utf-8') as res:
        scan_result = json.load(res, object_pairs_hook=OrderedDict)

    if scan_result.get('scancode_version'):
        del scan_result['scancode_version']

    scan_result['files'].sort(key=lambda x: x['path'])
    return scan_result


def test_package_option_detects_packages(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('package', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--package', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'package.json' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_packages(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('package', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--package', '--verbose', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'package.json' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_copyright_option_detects_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--verbose', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_license_option_detects_licenses(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('license', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--license', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_scancode_skip_vcs_files_and_dirs_by_default(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('ignore/vcs.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file, test_dir)
    # a single test.tst file and its directory that is not a VCS file should be listed
    assert 2 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'vcs', u'vcs/test.txt'] == scan_locs


def test_usage_and_help_return_a_correct_script_name_on_all_platforms(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.scancode, ['--help'])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = runner.invoke(cli.scancode, [], catch_exceptions=True)
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = runner.invoke(cli.scancode, ['-xyz'], catch_exceptions=True)
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output


def test_scan_info_does_collect_infos(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/basic.expected.json'), result_file, test_dir)


def test_scan_info_license_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/all.expected.json'), result_file, test_dir)


def test_scan_email_url_info(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--email', '--url', '--info', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file, test_dir)


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


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_json(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.json')
    result = runner.invoke(cli.scancode, [ '--copyright', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file, test_file)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output


def test_scan_with_errors_and_diag_option_includes_full_traceback(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.json')
    result = runner.invoke(cli.scancode, [ '--copyright', '--diag', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file, test_file)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output

def test_failing_scan_return_proper_exit_code(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.json')
    result = runner.invoke(cli.scancode, [ '--copyright', test_file, result_file], catch_exceptions=True)
    # this will start failing when the proper return code is there, e.g. 1.
    assert result.exit_code != 1


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html_app(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.app.html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html-app', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_works_with_multiple_processes(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)
    runner = CliRunner()
    # run the same scan with one or three processes
    result_file_1 = test_env.get_temp_file('json')
    result1 = runner.invoke(cli.scancode, [ '--copyright', '--processes', '1', '--format', 'json', test_dir, result_file_1], catch_exceptions=True)
    assert result1.exit_code == 0
    result_file_3 = test_env.get_temp_file('json')
    result3 = runner.invoke(cli.scancode, [ '--copyright', '--processes', '3', '--format', 'json', test_dir, result_file_3], catch_exceptions=True)
    assert result3.exit_code == 0
    res1 = json.loads(open(result_file_1).read())
    res3 = json.loads(open(result_file_3).read())
    assert sorted(res1['files']) == sorted(res3['files'])


def test_scan_works_with_multiple_processes_and_timeouts(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    patched_environ = dict(
        # set small memory quota for test
        SCANCODE_TEST_MAX_MEMORY='0',  # use default
        SCANCODE_TEST_TIMEOUT='0.01',
    )

    result = runner.invoke(
        cli.scancode,
        [ '--copyright', '--processes', '2', '--format', 'json', test_dir, result_file],
        catch_exceptions=True,
        env=patched_environ)

    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = [
        {u'path': u'apache-1.0.txt', u'scan_errors': [{u'scan': [u'Processing interrupted: timeout after 0 seconds.']}]},
        {u'path': u'patchelf.pdf', u'scan_errors': [{u'scan': [u'Processing interrupted: timeout after 0 seconds.']}]},
        {u'path': u'apache-1.1.txt', u'scan_errors': [{u'scan': [u'Processing interrupted: timeout after 0 seconds.']}]}
    ]

    result_json = json.loads(open(result_file).read())
    assert sorted(expected) == sorted(result_json['files'])


def test_scan_works_with_multiple_processes_and_memory_quota(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    patched_environ = dict(
        # set small memory quota for test
        SCANCODE_TEST_MAX_MEMORY=str(1 * 1024 * 1024),
        SCANCODE_TEST_TIMEOUT='0',  # use default
    )

    result = runner.invoke(
        cli.scancode,
        [ '--copyright', '--license', '--processes', '2', '--format', 'json', test_dir, result_file],
        catch_exceptions=True,
        env=patched_environ
    )

    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = [
        {u'path': u'apache-1.1.txt', u'scan_errors': [{u'scan': [u'Processing interrupted: excessive memory usage of more than 1MB.']}]},
        {u'path': u'apache-1.0.txt', u'scan_errors': [{u'scan': [u'Processing interrupted: excessive memory usage of more than 1MB.']}]},
        {u'path': u'patchelf.pdf', u'scan_errors': [{u'scan': [u'Processing interrupted: excessive memory usage of more than 1MB.']}]}
    ]
    result_json = json.loads(open(result_file).read())
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: False)
    assert sorted(expected) == sorted(result_json['files'])
