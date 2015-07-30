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

import os
import json

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from commoncode.fileutils import as_posixpath

from scancode import cli
import codecs


class TestCommandLine(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_extract_option_is_exclusive_of_other_options(self):
        test_dir = self.get_temp_dir()
        runner = CliRunner()
        result = runner.invoke(cli.scancode, ['--extract', '--copyright', test_dir])
        assert result.exit_code == 2
        assert 'option cannot be combined with other scanning options' in result.output

        result = runner.invoke(cli.scancode, ['--copyright', '--extract', test_dir])
        assert result.exit_code == 2
        assert 'option cannot be combined with other scanning options' in result.output

        result = runner.invoke(cli.scancode, ['--extract', '--license', test_dir])
        assert result.exit_code == 2
        assert 'option cannot be combined with other scanning options' in result.output

        result = runner.invoke(cli.scancode, ['--extract', '--license', '--copyright', test_dir])
        assert result.exit_code == 2
        assert 'option cannot be combined with other scanning options' in result.output

    def test_extract_option_can_take_an_empty_directory(self):
        test_dir = self.get_temp_dir()
        runner = CliRunner()
        result = runner.invoke(cli.scancode, ['--extract', test_dir])
        assert result.exit_code == 0
        assert 'Extracting done' in result.output

    def test_extract_option_does_extract(self):
        test_dir = self.get_test_loc('extract', copy=True)
        runner = CliRunner()
        result = runner.invoke(cli.scancode, ['--extract', test_dir])
        assert result.exit_code == 0
        assert 'Extracting done' in result.output
        assert 'ERROR: Unrecognized archive format' in result.output
        assert os.path.exists(os.path.join(test_dir, 'some.tar.gz-extract'))

    def test_extract_option_works_with_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, ie the scancode-toolkit/ dir
        # To use relative paths, we use our tmp dir at the root of the code
        from os.path import dirname, join, abspath
        from  commoncode import fileutils
        import extractcode
        import tempfile
        import shutil

        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_file = self.get_test_loc('extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        test_tgt_dir = join(scancode_root, test_src_file) + extractcode.EXTRACT_SUFFIX

        runner = CliRunner()
        result = runner.invoke(cli.scancode, ['--extract', test_src_file])
        assert result.exit_code == 0
        assert 'Extracting done' in result.output
        assert not 'WARNING' in result.output
        assert not 'ERROR' in result.output
        expected = ['/c/a/a.txt', '/c/b/a.txt', '/c/c/a.txt']
        file_result = [as_posixpath(f.replace(test_tgt_dir, '')) for f in fileutils.file_iter(test_tgt_dir)]
        assert sorted(expected) == sorted(file_result)

    def test_copyright_option_detects_copyrights(self):
        test_dir = self.get_test_loc('copyright', copy=True)
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file])
        assert result.exit_code == 0
        assert 'Scanning done' in result.output
        assert os.path.exists(result_file)
        assert len(open(result_file).read()) > 10

    def test_verbose_copyrights(self):
        test_dir = self.get_test_loc('copyright', copy=True)
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--copyright', '--verbose', test_dir, result_file])
        assert result.exit_code == 0
        assert 'Scanning done' in result.output
        assert 'copyright_acme_c-c.c' in result.output
        assert os.path.exists(result_file)
        assert len(open(result_file).read()) > 10

    def test_license_option_detects_licenses(self):
        test_dir = self.get_test_loc('license', copy=True)
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--license', test_dir, result_file])
        assert result.exit_code == 0
        assert 'Scanning done' in result.output
        assert os.path.exists(result_file)
        assert len(open(result_file).read()) > 10

    def test_scancode_skip_vcs_files_and_dirs_by_default(self):
        test_dir = self.extract_test_tar('ignore/vcs.tgz')
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--copyright', test_dir, result_file])
        assert result.exit_code == 0
        scan_result = self.load_json_result(result_file, test_dir)
        # a single test.tst file and its directory that is not a VCS file should be listed
        assert 2 == scan_result['resource_count']
        scan_locs = [x['location'] for x in scan_result['results']]
        assert [u'vcs', u'vcs/test.txt'] == scan_locs

    def load_json_result(self, result_file, test_dir):
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

    def test_usage_and_help_return_a_correct_script_name_on_all_platforms(self):
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

    def test_info_collect_infos(self):
        test_dir = self.get_test_loc('info/basic', copy=True)
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--info', test_dir, result_file])
        assert result.exit_code == 0
        assert 'Scanning done' in result.output
        expected = self.load_json_result(self.get_test_loc('info/basic.expected.json'), test_dir)
        loaded_result = self.load_json_result(result_file, test_dir)
        assert expected == loaded_result

    def test_info_license_copyrights(self):
        test_dir = self.get_test_loc('info/basic', copy=True)
        runner = CliRunner()
        result_file = self.get_temp_file('json')
        result = runner.invoke(cli.scancode, ['--info', '--license', '--copyright', test_dir, result_file])
        assert result.exit_code == 0
        assert 'Scanning done' in result.output
        expected = self.load_json_result(self.get_test_loc('info/all.expected.json'), test_dir)
        loaded_result = self.load_json_result(result_file, test_dir)
        assert expected == loaded_result