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

import codecs
from collections import OrderedDict
import json
import os

import click
from click.testing import CliRunner

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows

from scancode import cli


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""


def check_scan(expected_file, result_file, regen=False):
    """
    Check the scan result_file JSON results against the expected_file expected JSON
    results. Removes references to test_dir for the comparison. If regen is True the
    expected_file WILL BE overwritten with the results. This is convenient for
    updating tests expectations. But use with caution.
    """
    result = _load_json_result(result_file)
    if regen:
        with open(expected_file, 'wb') as reg:
            json.dump(result, reg, indent=2)
    expected = _load_json_result(expected_file)
    # NOTE we redump the JSON as a string for a more efficient comparison of
    # failures
    expected = json.dumps(expected, indent=2, sort_keys=True)
    result = json.dumps(result, indent=2, sort_keys=True)
    assert expected == result


def _load_json_result(result_file):
    """
    Load the result file as utf-8 JSON and strip test_dir prefix from
    locations.
    Sort the results by location.
    """
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
    scan_result = _load_json_result(result_file)
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
    check_scan(test_env.get_test_loc('info/basic.expected.json'), result_file)


def test_scan_info_license_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/all.expected.json'), result_file)


def test_scan_email_url_info(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--email', '--url', '--info', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file)


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
    check_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file)
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
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output

    result_json = json.loads(open(result_file).read())
    expected = 'ERROR: copyrights: unpack requires a string argument of length 8'
    assert expected == result_json['files'][0]['scan_errors'][0]

    assert result_json['files'][0]['scan_errors'][1].startswith('ERROR: copyrights: Traceback (most recent call')


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
    # this contains test files with a lot of 100+ small licenses mentions that should
    # take more thant timeout to scan
    test_dir = test_env.get_test_loc('timeout', copy=True)
    # add some random bytes to the test files to ensure that the license results will
    # not be cached
    import time, random
    for tf in fileutils.file_iter(test_dir):
        with open(tf, 'ab') as tfh:
            tfh.write(str(time.time() + random.randint(0, 10 ** 6)))

    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    result = runner.invoke(
        cli.scancode,
        [ '--copyright', '--license', '--processes', '2', '--timeout', '1', '--format', 'json', test_dir, result_file],
        catch_exceptions=True)

    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = [
        {u'path': u'test1.txt', u'scan_errors': [u'ERROR: Processing interrupted: timeout after 1 seconds.']},
        {u'path': u'test2.txt', u'scan_errors': [u'ERROR: Processing interrupted: timeout after 1 seconds.']},
        {u'path': u'test3.txt', u'scan_errors': [u'ERROR: Processing interrupted: timeout after 1 seconds.']}
    ]

    result_json = json.loads(open(result_file).read())
    assert sorted(expected) == sorted(result_json['files'])


def test_scan_works_with_multiple_processes_and_memory_quota(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)
    # add some random bytes to the test files to ensure that the license results will
    # not be cached
    import time, random
    for tf in fileutils.file_iter(test_dir):
        with open(tf, 'ab') as tfh:
            tfh.write(str(time.time() + random.randint(0, 10 ** 6)))

    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    result = runner.invoke(
        cli.scancode,
        [ '--copyright', '--license', '--processes', '2', '--max-memory', '1', '--format', 'json', test_dir, result_file],
        catch_exceptions=True,
    )

    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = [
        {u'path': u'apache-1.1.txt', u'scan_errors': [u'ERROR: Processing interrupted: excessive memory usage of more than 1MB.']},
        {u'path': u'apache-1.0.txt', u'scan_errors': [u'ERROR: Processing interrupted: excessive memory usage of more than 1MB.']},
        {u'path': u'patchelf.pdf', u'scan_errors': [u'ERROR: Processing interrupted: excessive memory usage of more than 1MB.']}
    ]
    result_json = json.loads(open(result_file).read())
    assert sorted(expected) == sorted(result_json['files'])


def test_scan_does_not_fail_when_scanning_unicode_files_and_paths(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc(u'unicodepath/uc')

    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright',
                                          '--package', '--email', '--url', test_dir , result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    # the paths for each OS end up encoded differently.
    # See https://github.com/nexB/scancode-toolkit/issues/390 for details

    if on_linux:
        expected = 'unicodepath/unicodepath.expected-linux.json'
    elif on_mac:
        expected = 'unicodepath/unicodepath.expected-mac.json'
    elif on_windows:
        expected = 'unicodepath/unicodepath.expected-win.json'

    check_scan(test_env.get_test_loc(expected), result_file, regen=False)


def test_scan_can_handle_licenses_with_unicode_metadata(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('license_with_unicode_meta')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--license', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_quiet_to_file_does_not_echo_anything(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result1_file = test_env.get_temp_file('json')
    result1 = runner.invoke(cli.scancode, ['--quiet', '--info', test_dir, result1_file], catch_exceptions=True)
    assert result1.exit_code == 0
    assert not result1.output


def test_scan_quiet_to_stdout_only_echoes_json_results(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result1_file = test_env.get_temp_file('json')
    result1 = runner.invoke(cli.scancode, ['--quiet', '--info', test_dir, result1_file], catch_exceptions=True)
    assert result1.exit_code == 0
    assert not result1.output

    # also test with an output of JSON to stdout
    runner2 = CliRunner()
    result2 = runner2.invoke(cli.scancode, ['--quiet', '--info', test_dir], catch_exceptions=False)
    assert result2.exit_code == 0

    # outputs to file or stdout should be identical
    result1_output = open(result1_file).read()
    assert result1_output == result2.output


def test_scan_can_return_matched_license_text(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_file = test_env.get_test_loc('license_text/test.txt')
    expected_file = test_env.get_test_loc('license_text/test.expected')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    result = runner.invoke(cli.scancode, ['--license', '--license-text', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    check_scan(test_env.get_test_loc(expected_file), result_file, regen=False)


def test_scan_can_handle_weird_file_names(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('weird_file_name/weird_file_name.tar.gz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['-c', '-i', test_dir, result_file], catch_exceptions=False)
    assert result.exit_code == 0
    assert "KeyError: 'sha1'" not in result.output
    assert 'Scanning done' in result.output

    # Some info vary on each OS
    # See https://github.com/nexB/scancode-toolkit/issues/438 for details
    if on_linux:
        expected = 'weird_file_name/expected-linux.json'
    elif on_mac:
        expected = 'weird_file_name/expected-mac.json'
    elif on_windows:
        expected = 'weird_file_name/expected-win.json'

    check_scan(test_env.get_test_loc(expected), result_file, regen=False)
