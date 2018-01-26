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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import click
click.disable_unicode_literals_warning = True

from click.termui import progressbar
from click.testing import CliRunner

from commoncode.testcase import FileDrivenTesting
from scancode import CommandLineOption
from scancode.cli import ScanCommand
from scancode.utils import fixed_width_file_name


class TestUtils(FileDrivenTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_click_progressbar_with_labels(self):

        # test related to https://github.com/mitsuhiko/click/issues/406
        @click.command()
        def mycli():
            """Sample cmd with progress bar"""
            click.echo('Start')
            with progressbar(range(10), label='xyz') as it:
                for _ in it:
                    pass
            click.echo('End')

        runner = CliRunner()
        result = runner.invoke(mycli)
        assert result.exit_code == 0
        expected = '''Start
xyz
End
'''
        assert expected == result.output


class TestFixedWidthFilename(FileDrivenTesting):

    def test_fixed_width_file_name_with_file_name_larger_than_max_length_is_shortened(self):
        test = fixed_width_file_name('0123456789012345678901234.c', 25)
        expected = '0123456789...5678901234.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_is_not_shortened(self):
        file_name = '0123456789012345678901234.c'
        test = fixed_width_file_name(file_name, max_length=50)
        assert file_name == test

    def test_fixed_width_file_name_with_file_name_at_max_length_is_not_shortened(self):
        test = fixed_width_file_name('01234567890123456789012.c', 25)
        expected = '01234567890123456789012.c'
        assert expected == test

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_not_shortened(self):
        test = fixed_width_file_name('0123456789012345678901.c', 25)
        expected = '0123456789012345678901.c'
        assert expected == test

    def test_fixed_width_file_name_with_none_filename_return_empty_string(self):
        test = fixed_width_file_name(None, 25)
        expected = ''
        assert expected == test

    def test_fixed_width_file_name_without_extension(self):
        test = fixed_width_file_name('012345678901234567890123456', 25)
        expected = '01234567890...67890123456'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_without_shortening(self):
        test = fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/drupal.js', 25)
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_posix_path_with_shortening(self):
        test = fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_without_shortening(self):
        test = fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\drupal.js', 25)
        expected = 'drupal.js'
        assert expected == test

    def test_fixed_width_file_name_with_win_path_with_shortening(self):
        test = fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert expected == test

    def test_fixed_width_file_name_with_very_small_file_name_and_long_extension(self):
        test = fixed_width_file_name('abc.abcdef', 5)
        # FIXME: what is expected is TBD
        expected = ''
        assert expected == test


class TestHelpGroups(FileDrivenTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_scan_help_group_and_sort_order_without_custom_class(self):

        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, help='Help text for option')
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        from scancode import MISC_GROUP
        assert MISC_GROUP in result.output
        assert  '--opt   Help text for option' in result.output

    def test_scan_help_group_and_sort_order_with_custom_class(self):

        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, sort_order=10,
                      help='Help text for option', cls=CommandLineOption)
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        from scancode import MISC_GROUP
        assert MISC_GROUP + ':\n    --opt   Help text for option\n' in result.output

    def test_scan_help_with_group(self):
        from scancode import CORE_GROUP

        @click.command(name='scan', cls=ScanCommand)
        @click.option('--opt', is_flag=True, help='Help text for option',
                      help_group=CORE_GROUP, cls=CommandLineOption)
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        assert CORE_GROUP + ':\n    --opt  Help text for option\n' in result.output
