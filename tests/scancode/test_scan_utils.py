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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

import click
from click.testing import CliRunner
from click.termui import progressbar

from commoncode.testcase import FileBasedTesting

from scancode import utils


class TestUtils(FileBasedTesting):
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

    def test_get_relative_path(self):
        # plain file without parent
        assert 'file' == utils.get_relative_path(path='/file', len_base_path=5, base_is_dir=False)
        # plain file in a deep path
        assert 'that' == utils.get_relative_path(path='/this/file/that', len_base_path=5, base_is_dir=False)

        # plain path with directories
        assert 'file/that' == utils.get_relative_path(path='/this/file/that', len_base_path=5, base_is_dir=True)
        assert 'that' == utils.get_relative_path(path='/this/file/that', len_base_path=10, base_is_dir=True)
        assert 'this/file/that' == utils.get_relative_path(path='/foo//this/file/that', len_base_path=4, base_is_dir=True)
