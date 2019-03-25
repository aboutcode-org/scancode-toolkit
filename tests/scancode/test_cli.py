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
import pytest

from commoncode import fileutils
from commoncode.fileutils import fsencode
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import load_json_result
from scancode.cli_test_utils import load_json_result_from_string
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
    check_json_scan(test_env.get_test_loc('single/iproute.expected.json'), result_file, remove_file_date=True)


def test_scan_info_license_copyrights():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '--license', '--copyright', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/all.expected.json'), result_file, regen=False)


def test_scan_noinfo_license_copyrights_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--license', '--copyright', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/all.rooted.expected.json'), result_file, regen=False)


def test_scan_email_url_info():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--info', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_keep_trucking_with_json():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', '--strip-root', test_file, '--json', result_file]
    result = run_scan_click(args, expected_rc=0)
    check_json_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file, regen=False)
    assert 'Some files failed to scan' not in result.output
    assert 'patchelf.pdf' not in result.output


def test_scan_with_errors_always_includes_full_traceback():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', '--timeout', '0.000001', '--verbose',
            test_file, '--json', result_file]
    result = run_scan_click(args, expected_rc=1)
    assert 'ERROR: Processing interrupted: timeout' in result.output
    assert 'patchelf.pdf' in result.output
    result_json = json.loads(open(result_file).read())
    assert result_json['files'][0]['scan_errors'][0].startswith('ERROR: for scanner: copyrights')
    assert result_json['headers'][0]['errors']


def test_failing_scan_return_proper_exit_code():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')
    args = ['--copyright', '--timeout', '0.000001',
            test_file, '--json', result_file]
    run_scan_click(args, expected_rc=1)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.html')
    args = ['--copyright', '--timeout', '0.000001',
            test_file, '--html', result_file]
    run_scan_click(args, expected_rc=1)


def test_scan_license_should_not_fail_with_output_to_html_and_json():
    test_dir = test_env.get_test_loc('dual_output_with_license', copy=True)
    result_file_html = test_env.get_temp_file('html')
    result_file_json = test_env.get_temp_file('json')
    args = ['--license', test_dir,
            '--json', result_file_json,
            '--html', result_file_html,
            '--verbose']
    result = run_scan_click(args)
    assert 'Object of type License is not JSON serializable' not in result.output


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html_app():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.app.html')
    args = ['--copyright', '--timeout', '0.000001',
            test_file, '--html-app', result_file]
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
         (u'type', u'file'),
         (u'authors', []),
         (u'copyrights', []),
         (u'holders', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test2.txt'),
         (u'type', u'file'),
         (u'authors', []),
         (u'copyrights', []),
         (u'holders', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test3.txt'),
         (u'type', u'file'),
         (u'authors', []),
         (u'copyrights', []),
         (u'holders', []),
         (u'scan_errors', [u'ERROR: for scanner: copyrights:\nERROR: Processing interrupted: timeout after 0 seconds.'])]
    ]

    result_json = json.loads(open(result_file).read(), object_pairs_hook=OrderedDict)
    assert sorted(sorted(x) for x in expected) == sorted(sorted(x.items()) for x in result_json['files'])


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

    check_json_scan(test_env.get_test_loc(expected), result_file, remove_file_date=True, regen=False)
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
    json_result1_output = load_json_result_from_string(result1_output)
    json_result_to_stdout = load_json_result_from_string(result_to_stdout.output)
    # cleanup JSON
    assert json_result1_output == json_result_to_stdout


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
    check_json_scan(test_env.get_test_loc(expected_file), result_file, remove_file_date=True, regen=False)


def test_scan_logs_errors_messages_not_verbosely_on_stderr():
    test_file = test_env.get_test_loc('errors/many_copyrights.c')
    # we use very short timeouts to simulate an error
    args = ['-c', '-n', '0', '--timeout', '0.0001', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Some files failed to scan properly:' in stderr
    assert 'Path: many_copyrights.c' in stderr
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stdout, stdout
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' not in stderr, stderr


def test_scan_logs_errors_messages_not_verbosely_on_stderr_with_multiprocessing():
    test_file = test_env.get_test_loc('errors/many_copyrights.c')
    # we use very short timeouts to simulate an error
    args = ['-c', '-n', '2', '--timeout', '0.0001', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Some files failed to scan properly:' in stderr
    assert 'Path: many_copyrights.c' in stderr
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stdout
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' not in stderr


def test_scan_logs_errors_messages_verbosely():
    test_file = test_env.get_test_loc('errors/many_copyrights.c')
    # we use very short timeouts to simulate an error
    args = ['-c', '--verbose', '-n', '0', '--timeout', '0.0001', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Some files failed to scan properly:' in stderr
    assert 'Path: many_copyrights.c' in stderr

    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stdout
    assert 'ERROR: for scanner: copyrights:' in stdout

    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stderr
    assert 'ERROR: for scanner: copyrights:' in stderr


def test_scan_logs_errors_messages_verbosely_with_verbose_and_multiprocessing():
    test_file = test_env.get_test_loc('errors/many_copyrights.c')
    # we use very short timeouts to simulate an error
    args = ['-c', '--verbose', '-n', '2', '--timeout', '0.0001', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=1)
    assert 'Some files failed to scan properly:' in stderr
    assert 'Path: many_copyrights.c' in stderr
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stdout
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' in stderr


def test_scan_does_not_report_errors_on_incorrect_package_manifest():
    test_file = test_env.get_test_loc('errors/broken_packages')
    args = ['-pi', '--verbose', '-n', '0', test_file, '--json', '-']
    _rc, stdout, stderr = run_scan_plain(args, expected_rc=0)
    assert 'Some files failed to scan properly:' not in stderr
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' not in stdout
    assert 'ERROR: Processing interrupted: timeout after 0 seconds.' not in stderr


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


def test_scan_cli_help(regen=True):
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
    # NB: these keys are the name of the scan plugins in setup.py
    expected = set(['emails', 'urls', 'licenses', 'copyrights', 'info', 'packages'])
    check_timings(expected, file_results)


def test_scan_with_timing_jsonpp_return_timings_for_each_scanner():
    test_dir = test_env.extract_test_tar('timing/basic.tgz')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--license', '--copyright', '--info',
            '--package', '--timing', '--verbose', '--json-pp', result_file, test_dir]
    run_scan_click(args)
    file_results = load_json_result(result_file)['files']
    # NB: these keys are the name of the scan plugins in setup.py
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


def test_summary_counts_when_using_disk_cache():
    test_file = test_env.get_test_loc('resource/samples')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '-n', '-1', '--max-in-memory', '-1', test_file, '--json', result_file]
    result = run_scan_click(args, expected_rc=0)
    assert ('44 resource(s): 33 file(s) and 11 directorie(s)') in result.output


def test_scan_should_not_fail_with_low_max_in_memory_setting_when_ignoring_files():
    test_file = test_env.get_test_loc('resource/client')
    result_file = test_env.get_temp_file('json')
    args = ['--info', '-n', '-1', '--ignore', '*.gif', '--max-in-memory=1', test_file, '--json', result_file]
    run_scan_click(args, expected_rc=0)


def test_get_displayable_summary():
    from scancode.cli import get_displayable_summary
    from scancode.resource import Codebase

    # Set up test codebase
    test_codebase = test_env.get_test_loc('resource/client')
    codebase = Codebase(test_codebase, strip_root=True)
    codebase.timings['scan'] = 0
    scan_names = 'foo, bar, baz'
    processes = 23
    errors = ['failed to scan ABCD']
    results = get_displayable_summary(codebase, scan_names, processes, errors)
    expected = (
        [u'Some files failed to scan properly:', u'failed to scan ABCD'],
        [
            u'Summary:        foo, bar, baz with 23 process(es)',
            u'Errors count:   1',
            u'Scan Speed:     0.00 files/sec. ',
            u'Initial counts: 0 resource(s): 0 file(s) and 0 directorie(s) ',
            u'Final counts:   0 resource(s): 0 file(s) and 0 directorie(s) ',
            u'Timings:',
            u'  scan_start: None',
            u'  scan_end:   None']
    )
    assert expected == results


@pytest.mark.xfail#('weird test with TTY interactions that need to be revisited')
def test_display_summary_edge_case_scan_time_zero_should_not_fail():
    from io import StringIO
    import sys

    from scancode.cli import display_summary
    from scancode.resource import Codebase

    # Set up test codebase
    test_codebase = test_env.get_test_loc('resource/client')
    codebase = Codebase(test_codebase, strip_root=True)
    codebase.timings['scan'] = 0
    scan_names = 'foo, bar, baz'
    processes = 23
    errors = ['failed to scan ABCD']
    try:
        # Redirect summary output from `stderr` to `result`
        result = StringIO()
        sys.stderr = result

        # Output from `display_summary` will be in `result`
        display_summary(codebase, scan_names, processes, errors)
    finally:
        # Set `stderr` back
        sys.stderr = sys.__stderr__


def test_check_error_count():
    test_dir = test_env.get_test_loc('failing')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--url', '--timeout', '0.000001',
            test_dir, '--json', result_file]
    result = run_scan_click(args, expected_rc=1)
    output = result.output
    output = output.replace('\n', ' ').replace('   ', ' ')
    output = output.split(' ')
    error_files = output.count('Path:')
    error_count = output[output.index('count:') + 1]
    assert str(error_files) == str(error_count)


def test_scan_keep_temp_files_is_false_by_default():
    test_file = test_env.get_test_loc('tempfiles/samples')
    result_file = test_env.get_temp_file('json')
    # mock using a well defined temporary directory
    temp_directory = test_env.get_temp_dir()
    env = dict(os.environ)
    env.update({'SCANCODE_TEMP': temp_directory})
    args = [
        '--info', test_file, '--json', result_file,
        # this forces using a temp file cache so that we have temp files
        '--max-in-memory', '-1']
    _ = run_scan_plain(args, expected_rc=0, env=env)
    # the SCANCODE_TEMP dir is not deleted, but it should be empty
    assert os.path.exists(temp_directory)
    # this does not make sense but that's what is seen in practice
    expected = 2 if on_windows else 1
    assert expected == len(list(os.walk(temp_directory)))


def test_scan_keep_temp_files_keeps_files():
    test_file = test_env.get_test_loc('tempfiles/samples')
    result_file = test_env.get_temp_file('json')
    # mock using a well defined temporary directory
    temp_directory = test_env.get_temp_dir()
    env = dict(os.environ)
    env.update({'SCANCODE_TEMP': temp_directory})
    args = [
        '--keep-temp-files',
        '--info', test_file, '--json', result_file,
        # this forces using a temp file cache
        '--max-in-memory', '-1']
    _rc, _stdout, _stderr = run_scan_plain(args, expected_rc=0, env=env)

    # the SCANCODE_TEMP dir is not deleted, but it should not be empty
    assert os.path.exists(temp_directory)
    # this does not make sense but that's what is seen in practice
    expected = 8 if on_windows else 7
    assert expected == len(list(os.walk(temp_directory)))
