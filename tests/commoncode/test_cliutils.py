#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import click
click.disable_unicode_literals_warning = True
from click.testing import CliRunner

from commoncode.testcase import FileDrivenTesting
from commoncode.cliutils import fixed_width_file_name
from commoncode.cliutils import GroupedHelpCommand
from commoncode.cliutils import PluggableCommandLineOption


class TestFixedWidthFilename(FileDrivenTesting):

    def test_fixed_width_file_name_with_file_name_larger_than_max_length_is_shortened(self):
        test = fixed_width_file_name('0123456789012345678901234.c', 25)
        expected = '0123456789...5678901234.c'
        assert test == expected

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_is_not_shortened(self):
        file_name = '0123456789012345678901234.c'
        test = fixed_width_file_name(file_name, max_length=50)
        assert test == file_name

    def test_fixed_width_file_name_with_file_name_at_max_length_is_not_shortened(self):
        test = fixed_width_file_name('01234567890123456789012.c', 25)
        expected = '01234567890123456789012.c'
        assert test == expected

    def test_fixed_width_file_name_with_file_name_smaller_than_max_length_not_shortened(self):
        test = fixed_width_file_name('0123456789012345678901.c', 25)
        expected = '0123456789012345678901.c'
        assert test == expected

    def test_fixed_width_file_name_with_none_filename_return_empty_string(self):
        test = fixed_width_file_name(None, 25)
        expected = ''
        assert test == expected

    def test_fixed_width_file_name_without_extension(self):
        test = fixed_width_file_name('012345678901234567890123456', 25)
        expected = '01234567890...67890123456'
        assert test == expected

    def test_fixed_width_file_name_with_posix_path_without_shortening(self):
        test = fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/drupal.js', 25)
        expected = 'drupal.js'
        assert test == expected

    def test_fixed_width_file_name_with_posix_path_with_shortening(self):
        test = fixed_width_file_name('C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert test == expected

    def test_fixed_width_file_name_with_win_path_without_shortening(self):
        test = fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\drupal.js', 25)
        expected = 'drupal.js'
        assert test == expected

    def test_fixed_width_file_name_with_win_path_with_shortening(self):
        test = fixed_width_file_name('C\\:Documents_and_Settings\\Boki\\Desktop\\head\\patches\\drupal6\\012345678901234567890123.c', 25)
        expected = '0123456789...4567890123.c'
        assert test == expected

    def test_fixed_width_file_name_with_very_small_file_name_and_long_extension(self):
        test = fixed_width_file_name('abc.abcdef', 5)
        # FIXME: what is expected is TBD
        expected = ''
        assert test == expected


class TestGroupedHelpCommand(FileDrivenTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_GroupedHelpCommand_help_group_and_sort_order_without_custom_class(self):

        @click.command(name='scan', cls=GroupedHelpCommand)
        @click.option('--opt', is_flag=True, help='Help text for option')
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        from commoncode.cliutils import MISC_GROUP
        assert MISC_GROUP in result.output
        assert  '--opt   Help text for option' in result.output

    def test_GroupedHelpCommand_with_help_group_and_sort_order_with_custom_class(self):

        @click.command(name='scan', cls=GroupedHelpCommand)
        @click.option('--opt', is_flag=True, sort_order=10,
                      help='Help text for option', cls=PluggableCommandLineOption)
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        from commoncode.cliutils import MISC_GROUP
        assert MISC_GROUP + ':\n    --opt   Help text for option\n' in result.output

    def test_GroupedHelpCommand_help_with_group(self):
        from commoncode.cliutils import CORE_GROUP

        @click.command(name='scan', cls=GroupedHelpCommand)
        @click.option(
            '--opt',
            is_flag=True,
            help='Help text for option',
            help_group=CORE_GROUP,
            cls=PluggableCommandLineOption,
        )
        def scan(opt):
            pass

        runner = CliRunner()
        result = runner.invoke(scan, ['--help'])
        assert CORE_GROUP + ':\n    --opt  Help text for option\n' in result.output
