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

import os

import click
from click.testing import CliRunner

from commoncode.fileutils import as_posixpath

from scancode import extract_cli
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_windows

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing
the actual command outputs as if using a TTY or not.
"""


def test_extractcode_command_can_take_an_empty_directory(monkeypatch):
    test_dir = test_env.get_temp_dir()
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(extract_cli.extractcode, [test_dir])
    assert result.exit_code == 0
    assert 'Extracting archives...' in result.output
    assert 'Extracting done' in result.output


def test_extractcode_command_does_extract_verbose(monkeypatch):
    test_dir = test_env.get_test_loc('extract', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(extract_cli.extractcode, ['--verbose', test_dir])
    assert result.exit_code == 1
    assert os.path.exists(os.path.join(test_dir, 'some.tar.gz-extract'))
    expected = [
        'Extracting archives...',
        'some.tar.gz',
        'broken.tar.gz',
        'tarred_gzipped.tgz',
        'ERROR extracting',
        "broken.tar.gz: 'Unrecognized archive format'",
        'Extracting done.',
    ]
    for e in expected:
        assert e in result.output


def test_extractcode_command_always_shows_something_if_not_using_a_tty_verbose_or_not(monkeypatch):
    test_dir = test_env.get_test_loc('extract/some.tar.gz', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: False)
    runner = CliRunner()
    result = runner.invoke(extract_cli.extractcode, ['--verbose', test_dir])
    assert 'Extracting archives...\nExtracting done.\n' == result.output
    result = runner.invoke(extract_cli.extractcode, [test_dir])
    assert 'Extracting archives...\nExtracting done.\n' == result.output


def test_extractcode_command_works_with_relative_paths(monkeypatch):
    # The setup is a tad complex because we want to have a relative dir
    # to the base dir where we run tests from, ie the scancode-toolkit/ dir
    # To use relative paths, we use our tmp dir at the root of the code tree
    from os.path import dirname, join, abspath
    from  commoncode import fileutils
    import extractcode
    import tempfile
    import shutil

    try:
        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_file = test_env.get_test_loc('extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        test_tgt_dir = join(scancode_root, test_src_file) + extractcode.EXTRACT_SUFFIX

        runner = CliRunner()
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        result = runner.invoke(extract_cli.extractcode, [test_src_file])
        assert result.exit_code == 0
        assert 'Extracting done' in result.output
        assert not 'WARNING' in result.output
        assert not 'ERROR' in result.output
        expected = ['/c/a/a.txt', '/c/b/a.txt', '/c/c/a.txt']
        file_result = [as_posixpath(f.replace(test_tgt_dir, '')) for f in fileutils.file_iter(test_tgt_dir)]
        assert sorted(expected) == sorted(file_result)
    finally:
        fileutils.delete(test_src_dir)


def test_extractcode_command_works_with_relative_paths_verbose(monkeypatch):
    # The setup is a tad complex because we want to have a relative dir
    # to the base dir where we run tests from, ie the scancode-toolkit/ dir
    # To use relative paths, we use our tmp dir at the root of the code tree
    from os.path import dirname, join, abspath
    from  commoncode import fileutils
    import tempfile
    import shutil

    try:
        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_file = test_env.get_test_loc('extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        runner = CliRunner()
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        result = runner.invoke(extract_cli.extractcode, ['--verbose',test_src_file])
        assert result.exit_code == 0
        # extract the path from the second line of the output
        # check that the path is relative and not absolute
        lines = result.output.splitlines(False)
        line = lines[1]
        line_path = line.split(':', 1)[-1].strip()
        if on_windows:
            drive = test_file[:2]
            assert not line_path.startswith(drive)
        else:
            assert not line_path.startswith('/')
    finally:
        fileutils.delete(test_src_dir)

def test_usage_and_help_return_a_correct_script_name_on_all_platforms(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    result = runner.invoke(extract_cli.extractcode, ['--help'])
    assert 'Usage: extractcode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output

    result = runner.invoke(extract_cli.extractcode, [])
    assert 'Usage: extractcode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output

    result = runner.invoke(extract_cli.extractcode, ['-xyz'])
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output
