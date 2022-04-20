# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
import subprocess
import sys
import unittest
from commoncode.fileutils import resource_iter

"""
This test suite runs various code checks such as:
 - code style
 - ABOUT files
 - release archives creation

NOTE: it has imports limited to the standard library by design
"""

root_dir = dirname(dirname(dirname(__file__)))

on_linux = str(sys.platform).lower().startswith('linux')


@unittest.skipIf(not on_linux, 'Check about files only on one OS')
class TestCheckAboutFiles(unittest.TestCase):

    def test_about_files_src(self):
        subprocess.check_output('venv/bin/about check src/'.split(), cwd=root_dir)

    def test_about_files_etc(self):
        subprocess.check_output('venv/bin/about check etc/'.split(), cwd=root_dir)

    def test_about_files_self(self):
        subprocess.check_output('venv/bin/about check scancode-toolkit.ABOUT'.split(), cwd=root_dir)


@unittest.skip('We do not yet check for code style')
@unittest.skipIf(not on_linux, 'Check codestyle only on one OS')
class TestCheckCode(unittest.TestCase):

    def test_codestyle(self):
        subprocess.check_output(
            'venv/bin/pycodestyle --ignore E501,W503,W504,W605 '
            '--exclude=lib,lib64,thirdparty,'
            'docs,bin,migrations,settings,local,tmp .'.split(), cwd=root_dir)


@unittest.skipIf(not on_linux, 'Check file length only on one OS')
class TestFilenameMaxLength(unittest.TestCase):

    def test_file_name_are_not_too_long(self):

        # See https://unix.stackexchange.com/questions/32795/what-is-the-maximum-allowed-filename-and-folder-size-with-ecryptfs
        # 143 is the max filename length that luks and ecryptfs support!

        long_filenames = [r for r in resource_iter('src') if len(r.split('/')[-1]) > 143]
        long_filenames.extend(r for r in resource_iter('tests') if len(r.split('/')[-1]) > 143)
        if long_filenames:
            msg = '\n'.join(long_filenames)
            raise Exception(f'These filenames are too long (over 143 characters):\n{msg}')
