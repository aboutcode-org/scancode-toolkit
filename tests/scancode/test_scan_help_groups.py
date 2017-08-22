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
from __future__ import unicode_literals

from os import path

import click
click.disable_unicode_literals_warning = True
from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from scancode.cli import ScanCommand
from scancode.cli import ScanOption
from scancode.cli_test_utils import run_scan_click


class TestHelpGroups(FileBasedTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_scan_help_without_custom_class(self):
        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, help='Help text for option')
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        assert 'misc:\n    --opt   Help text for option\n' in result.output

    def test_scan_help_with_custom_class(self):
        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, help='Help text for option', cls=ScanOption)
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        assert 'misc:\n    --opt   Help text for option\n' in result.output

    def test_scan_help_with_group(self):
        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, help='Help text for option', group='core', cls=ScanOption)
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        assert 'core:\n    --opt  Help text for option\n' in result.output

    def test_scan_cli_help(self):
        expected_file = self.get_test_loc('help/help.txt')
        result = run_scan_click(['--help'])
        assert open(expected_file).read() == result.output
