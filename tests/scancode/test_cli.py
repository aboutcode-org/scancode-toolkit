#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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
import json
import os

import click
from click.testing import CliRunner

from commoncode.fileutils import as_posixpath
from commoncode.testcase import FileDrivenTesting

from scancode import cli


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing
the actual command outputs as if using a TTY or not.
"""

def load_json_result(result_file, test_dir):
    """
    Load the result file as utf-8 JSON and strip test_dir prefix from
    locations.
    Sort the results by location.
    """
    test_dir = as_posixpath(test_dir)
    with codecs.open(result_file, encoding='utf-8') as res:
        scan_result = json.load(res)
        for result in scan_result['results']:
            loc = result['location']
            loc = as_posixpath(loc).replace(test_dir, '').strip('/')
            result['location'] = loc
    scan_result['results'].sort(key=lambda x: x['location'])
    return scan_result


def test_copyright_option_detects_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_verbose_option_with_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('copyright', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', '--verbose', test_dir, result_file])
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
    result = runner.invoke(cli.scancode, ['--license', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10


def test_scancode_skip_vcs_files_and_dirs_by_default(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('ignore/vcs.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file])
    assert result.exit_code == 0
    scan_result = load_json_result(result_file, test_dir)
    # a single test.tst file and its directory that is not a VCS file should be listed
    assert 2 == scan_result['resource_count']
    scan_locs = [x['location'] for x in scan_result['results']]
    assert [u'vcs', u'vcs/test.txt'] == scan_locs


def test_usage_and_help_return_a_correct_script_name_on_all_platforms(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.scancode, ['--help'])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = runner.invoke(cli.scancode, [])
    assert 'Usage: scancode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output

    result = runner.invoke(cli.scancode, ['-xyz'])
    # this was showing up on Windows
    assert 'scancode-script.py' not in result.output


def test_info_collect_infos(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = load_json_result(test_env.get_test_loc('info/basic.expected.json'), test_dir)
    loaded_result = load_json_result(result_file, test_dir)
    assert expected == loaded_result


def test_info_license_copyrights(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.extract_test_tar('info/basic.tgz')
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    expected = load_json_result(test_env.get_test_loc('info/all.expected.json'), test_dir)
    loaded_result = load_json_result(result_file, test_dir)
    assert expected == loaded_result


def test_paths_are_posix_in_html_app_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html-app', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert '/posix_path/copyright_acme_c-c.c' in open(result_file).read()


def test_paths_are_posix_in_html_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('html')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'html', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert '/posix_path/copyright_acme_c-c.c' in open(result_file).read()


def test_paths_are_posix_in_json_format_output(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('posix_path', copy=True)
    runner = CliRunner()
    result_file = test_env.get_temp_file('json')
    result = runner.invoke(cli.scancode, [ '--copyright', '--format', 'json', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert '/posix_path/copyright_acme_c-c.c' in open(result_file).read()
