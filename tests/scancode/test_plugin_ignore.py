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
from __future__ import unicode_literals

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import load_json_result
from scancode.plugin_ignore import is_ignored
from scancode.plugin_ignore import ProcessIgnore
from scancode.resource import Codebase


class TestPluginIgnoreFiles(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_is_ignored_glob_path(self):
        location = 'common/src/test/sample.txt'
        ignores = {'*/src/test/*': 'test ignore'}
        assert is_ignored(location=location, ignores=ignores)

    def test_is_ignored_single_path(self):
        location = 'common/src/test/sample.txt'
        ignores = {'common/src/test/sample.txt': 'test ignore'}
        assert is_ignored(location=location, ignores=ignores)

    def test_is_ignored_single_path_not_matching(self):
        location = 'common/src/test/sample.txt'
        ignores = {'src/test/sample.txt': 'test ignore'}
        assert not is_ignored(location=location, ignores=ignores)

    def test_is_ignored_single_file(self):
        location = 'common/src/test/sample.txt'
        ignores = {'sample.txt': 'test ignore'}
        assert is_ignored(location=location, ignores=ignores)

    def test_is_ignored_glob_file(self):
        location = 'common/src/test/sample.txt'
        ignores = {'*.txt': 'test ignore'}
        assert is_ignored(location=location, ignores=ignores)

    def check_ProcessIgnore(self, test_dir, expected, ignore):
        codebase = Codebase(test_dir)
        test_plugin = ProcessIgnore()
        test_plugin.process_codebase(codebase, ignore=ignore)
        resources = [res.get_path(strip_root=True, decode=True)
                     for res in codebase.walk(skip_root=True)]
        assert expected == sorted(resources)

    def test_ProcessIgnore_with_single_file(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        ignore = ('sample.doc',)
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc',
            'user/src/test',
            'user/src/test/sample.txt'
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore)

    def test_ProcessIgnore_with_multiple_files(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        ignore = ('ignore.doc', 'sample.doc',)
        expected = [
            'user',
            'user/src',
            'user/src/test',
            'user/src/test/sample.txt'
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore)

    def test_ProcessIgnore_with_glob_for_extension(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        ignore = ('*.doc',)
        expected = [
            'user',
            'user/src',
            'user/src/test',
            'user/src/test/sample.txt'
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore)

    def test_ProcessIgnore_with_glob_for_path(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        ignore = ('*/src/test',)
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc'
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore)

    def test_ProcessIgnore_with_multiple_ignores(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        ignore = ('*.doc', '*/src/test/*',)
        expected = [
            'user',
            'user/src',
            'user/src/test'
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore)


class TestScanPluginIgnoreFiles(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_scancode_ignore_vcs_files_and_dirs_by_default(self):
        test_dir = self.extract_test_tar('plugin_ignore/vcs.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(['--copyright', '--strip-root', test_dir,
                                 '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        # a single test.tst file and its directory that is not a VCS file should
        # be listed
        assert 1 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        assert [u'vcs', u'vcs/test.txt'] == scan_locs

    def test_scancode_ignore_vcs_files_and_dirs_by_default_no_multiprocess(self):
        test_dir = self.extract_test_tar('plugin_ignore/vcs.tgz')
        result_file = self.get_temp_file('json')
        result = run_scan_click(['--copyright', '--strip-root',
                                 '--processes', '0',
                                 test_dir,
                                 '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        # a single test.tst file and its directory that is not a VCS file should
        # be listed
        assert 1 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        assert [u'vcs', u'vcs/test.txt'] == scan_locs

    def test_scancode_ignore_single_file(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(
            ['--copyright', '--strip-root', '--ignore', 'sample.doc',
             test_dir, '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        assert 3 == scan_result['files_count']
        # FIXME: add assert 3 == scan_result['dirs_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc',
            'user/src/test',
            'user/src/test/sample.txt'
        ]
        assert expected == scan_locs

    def test_scancode_ignore_multiple_files(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(['--copyright', '--strip-root',
                                 '--ignore', 'ignore.doc', test_dir,
                                 '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        assert 2 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/src',
            u'user/src/test',
            u'user/src/test/sample.doc',
            u'user/src/test/sample.txt']
        assert expected == scan_locs

    def test_scancode_ignore_glob_files(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(['--copyright', '--strip-root',
                                 '--ignore', '*.doc', test_dir,
                                 '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        assert 1 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/src',
            u'user/src/test',
            u'user/src/test/sample.txt'
        ]
        assert expected == scan_locs

    def test_scancode_ignore_glob_path(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(['--copyright', '--strip-root',
                                 '--ignore', '*/src/test/*', test_dir,
                                 '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        assert 2 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user', 
            u'user/ignore.doc', 
            u'user/src', 
            u'user/src/ignore.doc', 
            u'user/src/test'
        ]
        assert expected == scan_locs

    def test_scancode_multiple_ignores(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')

        result = run_scan_click(['--copyright', '--strip-root', 
                                 '--ignore', '*/src/test', 
                                 '--ignore', '*.doc', 
                                 test_dir, '--json', result_file])
        assert result.exit_code == 0
        scan_result = load_json_result(result_file)
        assert 0 == scan_result['files_count']
        scan_locs = [x['path'] for x in scan_result['files']]
        assert [u'user', u'user/src'] == scan_locs
