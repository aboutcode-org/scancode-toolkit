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
from __future__ import unicode_literals

from collections import OrderedDict
import json
import os
from unittest import TestCase
from unittest.case import skipIf

# from click.testing import CliRunner

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows

from scancode.cli_test_utils import _load_json_result
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain

from scancode import cli


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""


def test_package_option_detects_packages(monkeypatch):
    test_dir = test_env.get_test_loc('package', copy=True)
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--package', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    result = open(result_file).read()
    assert 'package.json' in result


def test_verbose_option_with_packages(monkeypatch):
    test_dir = test_env.get_test_loc('package', copy=True)
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--package', '--verbose', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'package.json' in result.output
    assert os.path.exists(result_file)
    result = open(result_file).read()
    assert 'package.json' in result


def test_copyright_option_detects_copyrights():
    test_dir = test_env.get_test_loc('copyright', copy=True)
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_copyrights(monkeypatch):
    test_dir = test_env.get_test_loc('copyright', copy=True)
    result_file = test_env.get_temp_file('json')
    result = run_scan_click(['--copyright', '--verbose', test_dir, result_file], monkeypatch)

    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert 'copyright_acme_c-c.c' in result.output
    assert len(open(result_file).read()) > 10


def test_license_option_detects_licenses():
    test_dir = test_env.get_test_loc('license', copy=True)
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--license', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_scancode_skip_vcs_files_and_dirs_by_default():
    test_dir = test_env.extract_test_tar('ignore/vcs.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--strip-root', test_dir, result_file])
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    # a single test.tst file and its directory that is not a VCS file should be listed
    assert 2 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'vcs', u'vcs/test.txt'] == scan_locs


def test_scancode_skip_single_file(monkeypatch):
    test_dir = test_env.extract_test_tar('ignore/user.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(
        ['--copyright', '--strip-root', '--ignore', 'sample.doc', test_dir, result_file],
        monkeypatch
    )
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    assert 6 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    expected = [
        'user',
        'user/ignore.doc',
        'user/src',
        'user/src/ignore.doc',
        'user/src/test',
        'user/src/test/sample.txt'
    ]
    assert expected == scan_locs


def test_scancode_skip_multiple_files(monkeypatch):
    test_dir = test_env.extract_test_tar('ignore/user.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--strip-root', '--ignore', 'ignore.doc', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    assert 5 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'user', u'user/src', u'user/src/test', u'user/src/test/sample.doc', u'user/src/test/sample.txt'] == scan_locs


def test_scancode_skip_glob_files(monkeypatch):
    test_dir = test_env.extract_test_tar('ignore/user.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--strip-root', '--ignore', '*.doc', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    assert 4 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'user', u'user/src', u'user/src/test', u'user/src/test/sample.txt'] == scan_locs


def test_scancode_skip_glob_path(monkeypatch):
    test_dir = test_env.extract_test_tar('ignore/user.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--strip-root', '--ignore', '*/src/test/*', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    assert 5 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'user', u'user/ignore.doc', u'user/src', u'user/src/ignore.doc', u'user/src/test'] == scan_locs

def test_scan_mark_source_without_info(monkeypatch):
    test_dir = test_env.extract_test_tar('mark_source/JGroups.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('mark_source/without_info.expected.json')

    result = run_scan_click(['--mark-source', test_dir, result_file], monkeypatch)
    check_json_scan(expected_file, result_file)

def test_scan_mark_source_with_info(monkeypatch):
    test_dir = test_env.extract_test_tar('mark_source/JGroups.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('mark_source/with_info.expected.json')

    result = run_scan_click(['--info', '--mark-source', test_dir, result_file], monkeypatch)
    check_json_scan(expected_file, result_file)

def test_scan_only_findings(monkeypatch):
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('only_findings/expected.json')

    result = run_scan_click(['--only-findings', test_dir, result_file], monkeypatch)
    check_json_scan(expected_file, result_file)


def test_usage_and_help_return_a_correct_script_name_on_all_platforms():
    result = run_scan_click(['--help'])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = run_scan_click([])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = run_scan_click(['-xyz'])
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output


def test_scan_info_does_collect_infos():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--info', '--strip-root', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('info/basic.expected.json'), result_file)


def test_scan_info_does_collect_infos_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--info', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('info/basic.rooted.expected.json'), result_file)


def test_scan_info_returns_full_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')

    result = run_scan_click(['--info', '--full-root', test_dir])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert fileutils.as_posixpath(test_dir) in result.output


def test_scan_info_license_copyrights():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--info', '--license', '--copyright', '--strip-root', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('info/all.expected.json'), result_file)


def test_scan_noinfo_license_copyrights_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--email', '--url', '--license', '--copyright', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('info/all.rooted.expected.json'), result_file)


def test_scan_email_url_info():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--email', '--url', '--info', '--strip-root', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_json():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')

    result = run_scan_click([ '--copyright', '--strip-root', test_file, result_file])
    assert result.exit_code == 1
    assert 'Scanning done' in result.output
    check_json_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output


def test_scan_with_errors_and_diag_option_includes_full_traceback():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')

    result = run_scan_click([ '--copyright', '--diag', test_file, result_file])
    assert result.exit_code == 1
    assert 'Scanning done' in result.output
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output

    result_json = json.loads(open(result_file).read())
    expected = 'ERROR: copyrights: unpack requires a string argument of length 8'
    assert expected == result_json['files'][0]['scan_errors'][0]
    assert result_json['files'][0]['scan_errors'][1].startswith('ERROR: copyrights: Traceback (most recent call')


def test_failing_scan_return_proper_exit_code():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.json')

    result = run_scan_click([ '--copyright', test_file, result_file])
    assert result.exit_code == 1


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.html')

    result = run_scan_click([ '--copyright', '--format', 'html', test_file, result_file])
    assert result.exit_code == 1
    assert 'Scanning done' in result.output


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html_app():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    result_file = test_env.get_temp_file('test.app.html')

    result = run_scan_click([ '--copyright', '--format', 'html-app', test_file, result_file])
    assert result.exit_code == 1
    assert 'Scanning done' in result.output


def test_scan_works_with_multiple_processes():
    test_dir = test_env.get_test_loc('multiprocessing', copy=True)

    # run the same scan with one or three processes
    result_file_1 = test_env.get_temp_file('json')
    result1 = run_scan_click([ '--copyright', '--processes', '1', '--format', 'json', test_dir, result_file_1])
    assert result1.exit_code == 0

    result_file_3 = test_env.get_temp_file('json')
    result3 = run_scan_click([ '--copyright', '--processes', '3', '--format', 'json', test_dir, result_file_3])
    assert result3.exit_code == 0
    res1 = json.loads(open(result_file_1).read())
    res3 = json.loads(open(result_file_3).read())
    assert sorted(res1['files']) == sorted(res3['files'])


def test_scan_works_with_multiple_processes_and_timeouts():
    # this contains test files with a lot of copyrights that should
    # take more thant timeout to scan
    test_dir = test_env.get_test_loc('timeout', copy=True)
    # add some random bytes to the test files to ensure that the license results will
    # not be cached
    import time, random
    for tf in fileutils.file_iter(test_dir):
        with open(tf, 'ab') as tfh:
            tfh.write('(c)' + str(time.time()) + repr([random.randint(0, 10 ** 6) for _ in range(10000)]) + '(c)')

    result_file = test_env.get_temp_file('json')

    result = run_scan_click(
        [ '--copyright', '--processes', '2',
         '--timeout', '0.000001',
         '--strip-root', '--format', 'json', test_dir, result_file],
    )

    assert result.exit_code == 1
    assert 'Scanning done' in result.output
    expected = [
        [(u'path', u'test1.txt'), (u'scan_errors', [u'ERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test2.txt'), (u'scan_errors', [u'ERROR: Processing interrupted: timeout after 0 seconds.'])],
        [(u'path', u'test3.txt'), (u'scan_errors', [u'ERROR: Processing interrupted: timeout after 0 seconds.'])],
    ]

    result_json = json.loads(open(result_file).read(), object_pairs_hook=OrderedDict)
    assert sorted(expected) == sorted(x.items() for x in result_json['files'])


def test_scan_does_not_fail_when_scanning_unicode_files_and_paths():
    test_dir = test_env.get_test_loc(u'unicodepath/uc')

    result_file = test_env.get_temp_file('json')
    result = run_scan_click(
        ['--info', '--license', '--copyright',
         '--package', '--email', '--url', '--strip-root', test_dir , result_file])
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

    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True)


def test_scan_can_handle_licenses_with_unicode_metadata():
    test_dir = test_env.get_test_loc('license_with_unicode_meta')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--license', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_quiet_to_file_does_not_echo_anything():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result1_file = test_env.get_temp_file('json')

    result1 = run_scan_click(['--quiet', '--info', test_dir, result1_file])
    assert result1.exit_code == 0
    assert not result1.output


def test_scan_quiet_to_stdout_only_echoes_json_results():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    result1_file = test_env.get_temp_file('json')

    result1 = run_scan_click(['--quiet', '--info', test_dir, result1_file])
    assert result1.exit_code == 0
    assert not result1.output

    # also test with an output of JSON to stdout
    result2 = run_scan_click(['--quiet', '--info', test_dir])
    assert result2.exit_code == 0

    # outputs to file or stdout should be identical
    result1_output = open(result1_file).read()
    assert result1_output == result2.output


def test_scan_verbose_does_not_echo_ansi_escapes():
    test_dir = test_env.extract_test_tar('info/basic.tgz')

    result = run_scan_click(['--verbose', '--info', test_dir])
    assert result.exit_code == 0
    assert '[?' not in result.output


def test_scan_can_return_matched_license_text():
    test_file = test_env.get_test_loc('license_text/test.txt')
    expected_file = test_env.get_test_loc('license_text/test.expected')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--license', '--license-text', '--strip-root', test_file, result_file])
    assert result.exit_code == 0
    check_json_scan(test_env.get_test_loc(expected_file), result_file)


@skipIf(on_windows, 'This test cannot run on windows as these are not legal file names.')
def test_scan_can_handle_weird_file_names():
    test_dir = test_env.extract_test_tar('weird_file_name/weird_file_name.tar.gz')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['-c', '-i', '--strip-root', test_dir, result_file])
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

    check_json_scan(test_env.get_test_loc(expected), result_file)


def test_scan_can_run_from_other_directory():
    test_file = test_env.get_test_loc('altpath/copyright.c')
    expected_file = test_env.get_test_loc('altpath/copyright.expected.json')
    result_file = test_env.get_temp_file('json')
    work_dir = os.path.dirname(result_file)

    rc, stdout, stderr = run_scan_plain(
        ['-ci', '--strip-root', test_file, result_file], cwd=work_dir)

    if rc != 0:
        print()
        print('stdout:')
        print(stdout)
        print()
        print('stderr:')
        print(stderr)
    assert rc == 0
    check_json_scan(test_env.get_test_loc(expected_file), result_file, strip_dates=True)


def test_scan_logs_errors_messages():
    test_file = test_env.get_test_loc('errors', copy=True)
    rc, stdout, stderr = run_scan_plain(['-pi', test_file, ])
    assert rc == 1
    assert 'package.json' in stderr
    assert 'delimiter: line 5 column 12' in stdout
    assert 'ValueError: Expecting' not in stdout


def test_scan_logs_errors_messages_with_diag():
    test_file = test_env.get_test_loc('errors', copy=True)

    rc, stdout, stderr = run_scan_plain(['-pi', '--diag', test_file, ])
    assert rc == 1
    assert 'package.json' in stderr
    assert 'delimiter: line 5 column 12' in stderr
    assert 'ValueError: Expecting' in stdout
    assert 'delimiter: line 5 column 12' in stdout


def test_scan_progress_display_is_not_damaged_with_long_file_names_orig(monkeypatch):
    test_dir = test_env.get_test_loc('long_file_name')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', test_dir, result_file], monkeypatch)
    assert result.exit_code == 0
    expected1 = 'Scanned: abcdefghijklmnopqr...234567890123456789.c'
    expected2 = 'Scanned: 0123456789012345678901234567890123456789.c'
    assert expected1 in result.output
    assert expected2 in result.output


class TestFixedWidthFilename(TestCase):

    def test_fixed_width_file_name_with_file_name_larger_than_max_length_is_shortened(self):
        test = cli.fixed_width_file_name('0123456789012345678901234.c', 25)
        expected = '0123456789...5678901234.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_is_not_shortened(self):
        file_name = '0123456789012345678901234.c'
        test = cli.fixed_width_file_name(file_name, max_length=50)
        assert file_name == test

    def test_fixed_width_file_name_with_file_name_at_max_length_is_not_shortened(self):
        test = cli.fixed_width_file_name('01234567890123456789012.c', 25)
        expected = '01234567890123456789012.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_not_shortened(self):
        test = cli.fixed_width_file_name('0123456789012345678901.c', 25)
        expected = '0123456789012345678901.c'
        assert expected == test

    def test_fixed_width_file_name_with_none_filename_return_empty_string(self):
        test = cli.fixed_width_file_name(None, 25)
        expected = ''
        assert expected == test

    def test_fixed_width_file_name_without_extension(self):
        test = cli.fixed_width_file_name('012345678901234567890123456', 25)
        expected = '01234567890...67890123456'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_without_shortening(self):
        test = cli.fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/drupal.js', 25)
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_with_shortening(self):
        test = cli.fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_without_shortening(self):
        test = cli.fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\drupal.js', 25)
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_with_shortening(self):
        test = cli.fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert expected == test

    def test_fixed_width_file_name_with_very_small_file_name_and_long_extension(self):
        test = cli.fixed_width_file_name('abc.abcdef', 5)
        # FIXME: what is expected is TBD
        expected = ''
        assert expected == test
