# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from os.path import dirname
import subprocess
import sys
import unittest


"""
This test suite runs code checks such as:
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
        subprocess.check_output('bin/about check src/'.split(), cwd=root_dir)

    def test_about_files_etc(self):
        subprocess.check_output('bin/about check etc/'.split(), cwd=root_dir)

    def test_about_files_self(self):
        subprocess.check_output('bin/about check scancode-toolkit.ABOUT'.split(), cwd=root_dir)


@unittest.skip('We do not yet check for code style')
@unittest.skipIf(not on_linux, 'Check codestyle only on one OS')
class TestCheckCode(unittest.TestCase):

    def test_codestyle(self):
        subprocess.check_output(
            'bin/pycodestyle --ignore E501,W503,W504,W605 '
            '--exclude=lib,lib64,thirdparty,'
            'docs,bin,migrations,settings,local,tmp .'.split(), cwd=root_dir)
