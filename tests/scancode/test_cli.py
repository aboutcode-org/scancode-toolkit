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

import click
from click.testing import CliRunner

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows

from scancode.cli_test_utils import _load_json_result
from scancode.cli_test_utils import check_scan

from scancode import cli
from unittest.case import expectedFailure


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""
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


def test_verbose_option_with_packages():
    test_dir = test_env.get_test_loc('package', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--package', '--verbose', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'package.json' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_copyright_option_detects_copyrights():
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_copyrights():
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--verbose', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_scan_progress_display_is_not_damaged_with_long_file_names(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('long_file_name')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert '0123456789...0123456789.c' in result.output


def test_license_option_detects_licenses():
    test_dir = test_env.get_test_loc('license', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--license', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_scancode_skip_vcs_files_and_dirs_by_default():
    test_dir = test_env.extract_test_tar('ignore/vcs.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--strip-root', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    scan_result = _load_json_result(result_file)
    # a single test.tst file and its directory that is not a VCS file should be listed
    assert 2 == scan_result['files_count']
    scan_locs = [x['path'] for x in scan_result['files']]
    assert [u'vcs', u'vcs/test.txt'] == scan_locs


def test_usage_and_help_return_a_correct_script_name_on_all_platforms():
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


def test_scan_info_does_collect_infos():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--strip-root', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/basic.expected.json'), result_file)


def test_scan_info_does_collect_infos_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/basic.rooted.expected.json'), result_file, regen=False)


def test_scan_info_returns_full_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result = runner.invoke(cli.scancode, ['--info', '--full-root', test_dir], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert test_dir in result.output


def test_scan_info_license_copyrights():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright', '--strip-root', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/all.expected.json'), result_file)


def test_scan_noinfo_license_copyrights_with_root():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--email', '--url', '--license', '--copyright', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/all.rooted.expected.json'), result_file, regen=False)


def test_scan_email_url_info():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--email', '--url', '--info', '--strip-root', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('info/email_url_info.expected.json'), result_file)


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_json():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.json')
    result = runner.invoke(cli.scancode, [ '--copyright', '--strip-root', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_scan(test_env.get_test_loc('failing/patchelf.expected.json'), result_file)
    assert 'Some files failed to scan' in result.output
    assert 'patchelf.pdf' in result.output


def test_scan_with_errors_and_diag_option_includes_full_traceback():
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


def test_failing_scan_return_proper_exit_code():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.json')
    result = runner.invoke(cli.scancode, [ '--copyright', test_file, result_file], catch_exceptions=True)
    # this will start failing when the proper return code is there, e.g. 1.
    assert result.exit_code != 1


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_should_not_fail_on_faulty_pdf_or_pdfminer_bug_but_instead_report_errors_and_keep_trucking_with_html_app():
    test_file = test_env.get_test_loc('failing/patchelf.pdf')
    runner = CliRunner()
    result_file = test_env.get_temp_file('test.app.html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html-app', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_works_with_multiple_processes():
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


def test_scan_works_with_multiple_processes_and_timeouts():
    # this contains test files with a lot of 100+ small licenses mentions that should
    # take more thant timeout to scan
    test_dir = test_env.get_test_loc('timeout', copy=True)
    # add some random bytes to the test files to ensure that the license results will
    # not be cached
    import time, random
    for tf in fileutils.file_iter(test_dir):
        with open(tf, 'ab') as tfh:
            tfh.write('(c)' + str(time.time()) + repr([random.randint(0, 10 ** 6) for _ in range(10000)]) + '(c)')

    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    result = runner.invoke(
        cli.scancode,
        [ '--copyright', '--processes', '2', '--timeout', '0.01', '--strip-root', '--format', 'json', test_dir, result_file],
        catch_exceptions=True)

    assert result.exit_code == 0
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

    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright',
                                          '--package', '--email', '--url', '--strip-root', test_dir , result_file], catch_exceptions=False)
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

    check_scan(test_env.get_test_loc(expected), result_file, strip_dates=True, regen=False)


def test_scan_can_handle_licenses_with_unicode_metadata():
    test_dir = test_env.get_test_loc('license_with_unicode_meta')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--license', test_dir, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    assert 'Scanning done' in result.output


def test_scan_quiet_to_file_does_not_echo_anything():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result1_file = test_env.get_temp_file('json')
    result1 = runner.invoke(cli.scancode, ['--quiet', '--info', test_dir, result1_file], catch_exceptions=True)
    assert result1.exit_code == 0
    assert not result1.output


def test_scan_quiet_to_stdout_only_echoes_json_results():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result1_file = test_env.get_temp_file('json')
    result1 = runner.invoke(cli.scancode, ['--quiet', '--info', test_dir, result1_file], catch_exceptions=True)
    assert result1.exit_code == 0
    assert not result1.output

    # also test with an output of JSON to stdout
    runner2 = CliRunner()
    result2 = runner2.invoke(cli.scancode, ['--quiet', '--info', test_dir], catch_exceptions=True)
    assert result2.exit_code == 0

    # outputs to file or stdout should be identical
    result1_output = open(result1_file).read()
    assert result1_output == result2.output


def test_scan_verbose_does_not_echo_ansi_escapes():
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result = runner.invoke(cli.scancode, ['--verbose', '--info', test_dir], catch_exceptions=True)
    assert result.exit_code == 0
    assert '[?' not in result.output


def test_scan_can_return_matched_license_text():
    test_file = test_env.get_test_loc('license_text/test.txt')
    expected_file = test_env.get_test_loc('license_text/test.expected')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')

    result = runner.invoke(cli.scancode, ['--license', '--license-text', '--strip-root', test_file, result_file], catch_exceptions=True)
    assert result.exit_code == 0
    check_scan(test_env.get_test_loc(expected_file), result_file, regen=False)


@skipIf(on_windows, 'This test cannot run on windows as these are not legal file names.')
def test_scan_can_handle_weird_file_names():
    test_dir = test_env.extract_test_tar('weird_file_name/weird_file_name.tar.gz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['-c', '-i', '--strip-root', test_dir, result_file], catch_exceptions=True)
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


def test_scan_can_run_from_other_directory():
    import scancode
    from commoncode.command import execute
    test_file = test_env.get_test_loc('altpath/copyright.c')
    expected_file = test_env.get_test_loc('altpath/copyright.expected.json')
    result_file = test_env.get_temp_file('json')
    scan_cmd = os.path.join(scancode.root_dir, 'scancode')
    work_dir = os.path.dirname(result_file)
    rc, stdout, stderr = execute(scan_cmd, ['-ci', '--strip-root', test_file, result_file], cwd=work_dir)
    if rc != 0:
        print()
        print('stdout:')
        print(stdout)
        print()
        print('stderr:')
        print(stderr)
    assert rc == 0
    check_scan(test_env.get_test_loc(expected_file), result_file, strip_dates=True, regen=False)


class TestFixedWidthFilename(TestCase):

    def test_fixed_width_file_name_with_file_name_larger_than_max_length_is_shortened(self):
        test = cli.fixed_width_file_name('0123456789012345678901234.c')
        expected = '0123456789...5678901234.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_is_not_shortened(self):
        file_name = '0123456789012345678901234.c'
        test = cli.fixed_width_file_name(file_name, max_length=50)
        assert file_name == test

    def test_fixed_width_file_name_with_file_name_at_max_length_is_not_shortened(self):
        test = cli.fixed_width_file_name('01234567890123456789012.c')
        expected = '01234567890123456789012.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_not_shortened(self):
        test = cli.fixed_width_file_name('0123456789012345678901.c')
        expected = '0123456789012345678901.c'
        assert expected == test

    def test_fixed_width_file_name_with_none_filename_return_empty_string(self):
        test = cli.fixed_width_file_name(None)
        expected = ''
        assert expected == test

    def test_fixed_width_file_name_without_extension(self):
        test = cli.fixed_width_file_name('012345678901234567890123456')
        expected = '01234567890...67890123456'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_without_shortening(self):
        test = cli.fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/drupal.js')
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_with_shortening(self):
        test = cli.fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/012345678901234567890123.c')
        expected = '0123456789...4567890123.c'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_without_shortening(self):
        test = cli.fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\drupal.js')
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_with_shortening(self):
        test = cli.fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\012345678901234567890123.c')
        expected = '0123456789...4567890123.c'
        assert expected == test

    @expectedFailure
    def test_fixed_width_file_name_with_very_small_file_name_and_long_extension(self):
        test = cli.fixed_width_file_name('abc.abcdef', 5)
        # FIXME: what is expected is TBD
        expected = ''
        assert expected == test
