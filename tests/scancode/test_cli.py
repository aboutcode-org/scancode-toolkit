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

from collections import OrderedDict
import json
import os
from unittest.case import skipIf

import click
click.disable_unicode_literals_warning = True

from commoncode import fileutils
from commoncode.fileutils import fsencode
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import load_json_result
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

"""
Most of these tests spawn new process as if launched from the command line. Some
of these CLI tests are dependent on py.test monkeypatch to ensure we are testing
the actual command outputs as if using a real command line call. Some are using
a plain subprocess to the same effect.
"""


def test_package_option_detects_packages(monkeypatch):
    test_dir = test_env.get_test_loc('package', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--package', test_dir, '--json', result_file]
    run_scan_click(args, monkeypatch=monkeypatch)
    assert os.path.exists(result_file)
    result = open(result_file).read()
    assert 'package.json' in result


def test_verbose_option_with_packages(monkeypatch):
    test_dir = test_env.get_test_loc('package', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--package', '--verbose', test_dir, '--json', result_file]
    result = run_scan_click(args, monkeypatch=monkeypatch)
    assert 'package.json' in result.output
    assert os.path.exists(result_file)
    result = open(result_file).read()
    assert 'package.json' in result


def test_copyright_option_detects_copyrights():
    test_dir = test_env.get_test_loc('copyright', copy=True)
    result_file = test_env.get_temp_file('json')
    run_scan_click(['--copyright', test_dir, '--json', result_file])
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_copyrights(monkeypatch):
    test_dir = test_env.get_test_loc('copyright', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--copyright', '--verbose', test_dir, '--json', result_file]
    result = run_scan_click(args, monkeypatch=monkeypatch)
    assert os.path.exists(result_file)
    assert 'copyright_acme_c-c.c' in result.output
    assert len(open(result_file).read()) > 10


def test_license_option_detects_licenses():
    test_dir = test_env.get_test_loc('license', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_usage_and_help_return_a_correct_script_name_on_all_platforms():
    result = run_scan_click(['--help'])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = run_scan_click([], expected_rc=2)
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = run_scan_click(['-xyz'], expected_rc=2)
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output


def test_scan_info_does_collect_info():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/basic.expected.json'), result_file)


def test_scan_info_does_collect_info_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['--info', test_dir, '--json', result_file])
    check_json_scan(test_env.get_test_loc('info/basic.rooted.expected.json'), result_file)


def test_scan_info_returns_full_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--full-root', test_dir, '--json', result_file]
    run_scan_click(args)
    result_data = json.loads(open(result_file, 'rb').read())
    file_paths = [f['path'] for f in result_data['files']]
    assert 12 == len(file_paths)
    root = fileutils.as_posixpath(test_dir)
    assert all(p.startswith(root) for p in file_paths)


def test_scan_info_returns_correct_full_root_with_single_file():
    test_file = test_env.get_test_loc('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--full-root', test_file, '--json', result_file]
    run_scan_click(args)
    result_data = json.loads(open(result_file, 'rb').read())
    files = result_data['files']
    # we have a single file
    assert len(files) == 1
    scanned_file = files[0]
    # and we check that the path is the full path without repeating the file name
    assert fileutils.as_posixpath(test_file) == scanned_file['path']


def test_scan_info_returns_does_not_strip_root_with_single_file():
    test_file = test_env.get_test_loc('single/iproute.c')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--strip-root', test_file, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('single/iproute.expected.json'), result_file, strip_dates=True)


def test_scan_info_license_copyrights():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--license', '--copyright', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/all.expected.json'), result_file)


def test_scan_license_with_url_template():
    test_dir = test_env.get_test_loc('plugin_license/license_url', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-url-template', 'https://example.com/urn:{}',
             test_dir, '--json-pp', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_license/license_url.expected.json'), result_file)


def test_scan_noinfo_license_copyrights_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--license', '--copyright', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/all.rooted.expected.json'), result_file)


def test_scan_email_url_info():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--info', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_json():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', '--strip-root', test_file, '--json', result_file]
    result = run_scan_click(args, expected_rc=1)
    check_json_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output


def test_scan_with_errors_always_includes_full_traceback():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', test_file, '--json', result_file]
    result = run_scan_click(args, expected_rc=1)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output
    result_json = json.loads(open(result_file).read())
    expected = 'error: unpack requires a string argument of length 8'
    assert expected in result_json['files'][0]['scan_errors'][-1]
    assert result_json['files'][0]['scan_errors'][0].startswith('ERROR: for scanner: copyrights')


def test_failing_scan_return_proper_exit_code():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', test_file, '--json', result_file]
    run_scan_click(args, expected_rc=1)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.html')
    args = ['--copyright', test_file, '--output-html', result_file]
    run_scan_click(args, expected_rc=1)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html_app():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.app.html')
    args = ['--copyright', test_file, '--output-html-app', result_file]
    run_scan_click(args, expected_rc=1)


def test_scan_works_with_multiple_processes():
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)

    # run the same scan with one or three processes
    result_file_1 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '1', test_dir, '--json', result_file_1]
    run_scan_click(args)

    result_file_3 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '3', test_dir, '--json', result_file_3]
    run_scan_click(args)
    res1 = json.loads(open(result_file_1).read())
    res3 = json.loads(open(result_file_3).read())
    assert sorted(res1['files']) == sorted(res3['files'])


def test_scan_works_with_no_processes_in_threaded_mode():
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)

    # run the same scan with zero or one process
    result_file_0 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '0', test_dir, '--json', result_file_0]
    result0 = run_scan_click(args)
    assert 'Disabling multi-processing' in result0.output

    result_file_1 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '1', test_dir, '--json', result_file_1]
    run_scan_click(args)
    res0 = json.loads(open(result_file_0).read())
    res1 = json.loads(open(result_file_1).read())
    assert sorted(res0['files']) == sorted(res1['files'])


def test_scan_works_with_no_processes_non_threaded_mode():
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)

    # run the same scan with zero or one process
    result_file_0 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '-1', test_dir, '--json', result_file_0]
    result0 = run_scan_click(args)
    assert 'Disabling multi-processing and multi-threading' in result0.output

    result_file_1 = test_env.get_temp_file('json')
    args = ['--copyright', '--processes', '1', test_dir, '--json', result_file_1]
    run_scan_click(args)
    res0 = json.loads(open(result_file_0).read())
    res1 = json.loads(open(result_file_1).read())
    assert sorted(res0['files']) == sorted(res1['files'])


def test_scan_works_with_multiple_processes_and_timeouts():
    # this contains test files with a lot of copyrights that should
    # take more thant timeout to scan
    test_dir = test_env.get_test_loc('timeout', copy=True)
    # add some random bytes to the test files to ensure that the license results will
    # not be cached
    import time, random
    for tf in fileutils.resource_iter(test_dir, with_dirs=False):
        with open(tf, 'ab') as tfh:
            tfh.write(
                '(c)' + str(time.time()) + repr([random.randint(0, 10 ** 6) for _ in range(10000)]) + '(c)')

    result_file = test_env.get_temp_file('json')

    args = ['--copyright', '--processes', '2', '--timeout', '0.000001',
            '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args, expected_rc=1)

    expected = [
        [(u'path', u'test1.txt'),
         (u'copyrights', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test2.txt'),
         (u'copyrights', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test3.txt'),
         (u'copyrights', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])]
    ]

    result_json = json.loads(open(result_file).read(), object_pairs_hook=OrderedDict)
    assert sorted(expected) == sorted(x.items() for x in result_json['files'])


def check_scan_does_not_fail_when_scanning_unicode_files_and_paths(verbosity):
    test_dir = test_env.get_test_loc(u'unicodepath/uc')
    result_file = test_env.get_temp_file('json')

    if on_linux:
        test_dir = fsencode(test_dir)
        result_file = fsencode(result_file)

    args = ['--info', '--license', '--copyright', '--package',
            '--email', '--url', '--strip-root', test_dir , '--json',
            result_file] + ([verbosity] if verbosity else [])
    results = run_scan_click(args)

    # the paths for each OS end up encoded differently.
    # See for details:
    # https://github.com/nexB/scancode-toolkit/issues/390
    # https://github.com/nexB/scancode-toolkit/issues/688

    if on_linux:
        expected = 'unicodepath/unicodepath.expected-linux.json' + verbosity
    elif on_mac:
        expected = 'unicodepath/unicodepath.expected-mac.json' + verbosity
    elif on_windows:
        expected = 'unicodepath/unicodepath.expected-win.json' + verbosity

    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True)
    return results


def test_scan_does_not_fail_when_scanning_unicode_files_and_paths_default():
    result = check_scan_does_not_fail_when_scanning_unicode_files_and_paths('')
    assert result.output


def test_scan_does_not_fail_when_scanning_unicode_files_and_paths_verbose():
    result = check_scan_does_not_fail_when_scanning_unicode_files_and_paths('--verbose')
    assert result.output


def test_scan_does_not_fail_when_scanning_unicode_files_and_paths_quiet():
    result = check_scan_does_not_fail_when_scanning_unicode_files_and_paths('--quiet')
    assert not result.output


@skipIf(on_windows, 'Python tar cannot extract these files on Windows')
def test_scan_does_not_fail_when_scanning_unicode_test_files_from_express():

    # On Windows, Python tar cannot extract these files. Other
    # extractors either fail or change the file name, making the test
    # moot. Git cannot check these files. So for now it makes no sense
    # to test this on Windows at all. Extractcode works fine, but does
    # rename the problematic files.

    test_dir = test_env.extract_test_tar_raw(b'unicode_fixtures.tar.gz')
    test_dir = fsencode(test_dir)

    args = ['-n0', '--info', '--license', '--copyright', '--package', '--email',
            '--url', '--strip-root', '--json', '-', test_dir]
    run_scan_click(args)


def test_scan_can_handle_licenses_with_unicode_metadata():
    test_dir = test_env.get_test_loc('license_with_unicode_meta')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['--license', test_dir, '--json', result_file])


def test_scan_quiet_to_file_does_not_echo_anything():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--quiet', '--info', test_dir, '--json', result_file]
    result = run_scan_click(args)
    assert not result.output


def test_scan_quiet_to_stdout_only_echoes_json_results():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--quiet', '--info', test_dir, '--json-pp', result_file]
    result_to_file = run_scan_click(args)
    assert not result_to_file.output

    # also test with an output of JSON to stdout
    args = ['--quiet', '--info', test_dir, '--json-pp', '-']
    result_to_stdout = run_scan_click(args)

    # outputs to file or stdout should be identical
    result1_output = open(result_file).read()
    assert result1_output == result_to_stdout.output


def test_scan_verbose_to_stdout_does_not_echo_ansi_escapes():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    args = ['--verbose', '--info', test_dir, '--json', '-']
    result = run_scan_click(args)
    assert '[?' not in result.output


def test_scan_can_return_matched_license_text():
    test_file = test_env.get_test_loc('license_text/test.txt')
    expected_file = test_env.get_test_loc('license_text/test.expected')
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--strip-root', test_file, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc(expected_file), result_file)


@skipIf(on_windows, 'This test cannot run on windows as these are not legal file names.')
def test_scan_can_handle_weird_file_names():
    test_dir = test_env.extract_test_tar('weird_file_name/weird_file_name.tar.gz')
    result_file = test_env.get_temp_file('json')
    args = ['-c', '-i', '--strip-root', test_dir, '--json', result_file]
    result = run_scan_click(args)
    assert "KeyError: 'sha1'" not in result.output

    # Some info vary on each OS
    # See https://github.com/nexB/scancode-toolkit/issues/438 for details
    if on_linux:
        expected = 'weird_file_name/expected-linux.json'
    elif on_mac:
        expected = 'weird_file_name/expected-mac.json'
    else:
        raise Exception('Not a supported OS?')
    check_json_scan(test_env.get_test_loc(expected), result_file, regen=False)


def test_scan_can_handle_non_utf8_file_names_on_posix():
    test_dir = test_env.extract_test_tar_raw('non_utf8/non_unicode.tgz')
    result_file = test_env.get_temp_file('json')

    if on_linux:
        test_dir = fsencode(test_dir)
        result_file = fsencode(result_file)

    args = ['-i', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)

    # the paths for each OS end up encoded differently.
    # See for details:
    # https://github.com/nexB/scancode-toolkit/issues/390
    # https://github.com/nexB/scancode-toolkit/issues/688

    if on_linux:
        expected = 'non_utf8/expected-linux.json'
    elif on_mac:
        expected = 'non_utf8/expected-mac.json'
    elif on_windows:
        expected = 'non_utf8/expected-win.json'

    check_json_scan(test_env.get_test_loc(expected), result_file, regen=False)


def test_scan_can_run_from_other_directory():
    test_file = test_env.get_test_loc('altpath/copyright.c')
    expected_file = test_env.get_test_loc('altpath/copyright.expected.json')
    result_file = test_env.get_temp_file('json')
    work_dir = os.path.dirname(result_file)
    args = ['-ci', '--strip-root', test_file, '--json', result_file]
    run_scan_plain(args, cwd=work_dir)
    check_json_scan(test_env.get_test_loc(expected_file), result_file, strip_dates=True)


def test_scan_logs_errors_messages_not_verbosely_on_stderr():
    test_file = test_env.get_test_loc('errors', copy=True)
    args = ['-pi', '-n', '0', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Path: errors/package.json' in stderr
    assert "Expecting ':' delimiter: line 5 column 12 (char 143)" in stdout
    assert "Expecting ':' delimiter: line 5 column 12 (char 143)" not in stderr


def test_scan_logs_errors_messages_not_verbosely_on_stderr_with_multiprocessing():
    test_file = test_env.get_test_loc('errors', copy=True)
    args = ['-pi', '-n', '2', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Path: errors/package.json' in stderr
    assert "Expecting ':' delimiter: line 5 column 12 (char 143)" in stdout
    assert "Expecting ':' delimiter: line 5 column 12 (char 143)" not in stderr


def test_scan_logs_errors_messages_verbosely_with_verbose():
    test_file = test_env.get_test_loc('errors', copy=True)
    args = ['-pi', '--verbose', '-n', '0', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'package.json' in stderr
    assert 'delimiter: line 5 column 12' in stdout
    assert 'delimiter: line 5 column 12' in stderr
    assert 'ValueError: Expecting' in stdout


def test_scan_logs_errors_messages_verbosely_with_verbose_and_multiprocessing():
    test_file = test_env.get_test_loc('errors', copy=True)
    args = ['-pi', '--verbose', '-n', '2', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'package.json' in stderr
    assert 'delimiter: line 5 column 12' in stdout
    assert 'delimiter: line 5 column 12' in stderr
    assert 'ValueError: Expecting' in stdout


def test_scan_progress_display_is_not_damaged_with_long_file_names_plain():
    test_dir = test_env.get_test_loc('long_file_name')
    result_file = test_env.get_temp_file('json')
    args = ['--copyright', test_dir, '--json', result_file]
    _rc, stdout, stderr = run_scan_plain(args)
    expected1 = 'Scanned: abcdefghijklmnopqr...234567890123456789.c'
    expected2 = 'Scanned: 0123456789012345678901234567890123456789.c'
    expected3 = 'abcdefghijklmnopqrtu0123456789012345678901234567890123456789abcdefghijklmnopqrtu0123456789012345678901234567890123456789.c'
    assert expected1 not in stdout
    assert expected2 not in stdout
    assert expected3 not in stdout
    assert expected1 not in stderr
    assert expected2 not in stderr
    assert expected3 not in stderr


def test_scan_progress_display_is_not_damaged_with_long_file_names(monkeypatch):
    test_dir = test_env.get_test_loc('long_file_name')
    result_file = test_env.get_temp_file('json')
    args = ['--copyright', test_dir, '--json', result_file]
    result = run_scan_click(args, monkeypatch=monkeypatch)
    if on_windows:
        expected1 = 'Scanned: 0123456789012345678901234567890123456789.c'
        expected2 = 'Scanned: abcdefghijklmnopqrt...0123456789012345678'
        expected3 = 'abcdefghijklmnopqrtu0123456789012345678901234567890123456789abcdefghijklmnopqrtu0123456789012345678901234567890123456789.c'
        try:
            assert expected1 in result.output
            assert expected2 not in result.output
            assert expected3 not in result.output
        except:
            print()
            print('output:')
            print(result.output)
            print()
            raise
    else:
        expected1 = 'Scanned: abcdefghijklmnopqr...234567890123456789.c'
        expected2 = 'Scanned: 0123456789012345678901234567890123456789.c'
        expected3 = 'abcdefghijklmnopqrtu0123456789012345678901234567890123456789abcdefghijklmnopqrtu0123456789012345678901234567890123456789.c'
        assert expected1 in result.output
        assert expected2 in result.output
        assert expected3 not in result.output


def test_scan_does_scan_php_composer():
    test_file = test_env.get_test_loc('composer/composer.json')
    expected_file = test_env.get_test_loc('composer/composer.expected.json')
    result_file = test_env.get_temp_file('results.json')
    run_scan_click(['--package', test_file, '--json', result_file])
    check_json_scan(expected_file, result_file)


def test_scan_does_scan_rpm():
    test_file = test_env.get_test_loc('rpm/fping-2.4-0.b2.rhfc1.dag.i386.rpm')
    expected_file = test_env.get_test_loc('rpm/fping-2.4-0.b2.rhfc1.dag.i386.rpm.expected.json')
    result_file = test_env.get_temp_file('results.json')
    run_scan_click(['--package', test_file, '--json', result_file])
    check_json_scan(expected_file, result_file, regen=False)


def test_scan_cli_help(regen=False):
    expected_file = test_env.get_test_loc('help/help.txt')
    result = run_scan_click(['--help'])
    if regen:
        with open(expected_file, 'wb') as ef:
            ef.write(result.output)
    assert open(expected_file).read() == result.output


def test_scan_errors_out_with_unknown_option():
    test_file = test_env.get_test_loc('license_text/test.txt')
    args = ['--json--info', test_file]
    result = run_scan_click(args, expected_rc=2)
    assert 'Error: no such option: --json--info' in result.output


def test_scan_to_json_without_FILE_does_not_write_to_next_option():
    test_file = test_env.get_test_loc('license_text/test.txt')
    args = ['--json', '--info', test_file]
    result = run_scan_click(args, expected_rc=2)
    assert ('Error: Invalid value for "--json": Illegal file name '
            'conflicting with an option name: --info.') in result.output


def test_scan_errors_out_with_conflicting_root_options():
    test_file = test_env.get_test_loc('license_text/test.txt')
    result_file = test_env.get_temp_file('results.json')
    args = ['--strip-root', '--full-root', '--json', result_file, '--info', test_file]
    result = run_scan_click(args, expected_rc=2)
    assert ('Error: The option --strip-root cannot be used together with the '
            '--full-root option(s) and --full-root is used.') in result.output


def test_scan_errors_out_with_conflicting_verbosity_options():
    test_file = test_env.get_test_loc('license_text/test.txt')
    result_file = test_env.get_temp_file('results.json')
    args = ['--quiet', '--verbose', '--json', result_file, '--info', test_file]
    result = run_scan_click(args, expected_rc=2)
    assert ('Error: The option --quiet cannot be used together with the '
            '--verbose option(s) and --verbose is used. You can set only one of '
            'these options at a time.') in result.output


def test_scan_with_timing_json_return_timings_for_each_scanner():
    test_dir = test_env.extract_test_tar('timing/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--license', '--copyright', '--info',
            '--package', '--timing', '--json', result_file, test_dir]
    run_scan_click(args)
    file_results = load_json_result(result_file)['files']

    expected = set(['emails', 'urls', 'licenses', 'copyrights', 'info', 'packages'])
    check_timings(expected, file_results)


def test_scan_with_timing_jsonpp_return_timings_for_each_scanner():
    test_dir = test_env.extract_test_tar('timing/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--license', '--copyright', '--info',
            '--package', '--timing', '--verbose', '--json-pp', result_file, test_dir]
    run_scan_click(args)
    file_results = load_json_result(result_file)['files']
    expected = set(['emails', 'urls', 'licenses', 'copyrights', 'info', 'packages'])
    check_timings(expected, file_results)


def check_timings(expected, file_results):
    for res in file_results:
        scan_timings = res['scan_timings']

        if not res['type'] == 'file':
            # should be an empty dict for dirs
            assert not scan_timings
            continue

        assert scan_timings

        for scanner, timing in scan_timings.items():
            assert scanner in expected
            assert timing
