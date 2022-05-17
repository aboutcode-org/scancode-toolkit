#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from commoncode.fileset import is_included
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import load_json_result
from scancode.plugin_ignore import ProcessIgnore
from commoncode.resource import Codebase


class TestPluginIgnoreFiles(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_is_included_glob_path(self):
        location = 'common/src/test/sample.txt'
        excludes = {'*/src/test/*': 'test ignore'}
        assert not is_included(location, excludes=excludes)

    def test_is_included_single_path(self):
        location = 'common/src/test/sample.txt'
        excludes = {'common/src/test/sample.txt': 'test ignore'}
        assert not is_included(location, excludes=excludes)

    def test_is_included_single_path_not_matching(self):
        location = 'common/src/test/sample.txt'
        excludes = {'src/test/sample.txt': 'test ignore'}
        assert is_included(location, excludes=excludes)

    def test_is_included_single_file(self):
        location = 'common/src/test/sample.txt'
        excludes = {'sample.txt': 'test ignore'}
        assert not is_included(location, excludes=excludes)

    def test_is_included_glob_file(self):
        location = 'common/src/test/sample.txt'
        excludes = {'*.txt': 'test ignore'}
        assert not is_included(location, excludes=excludes)

    def check_ProcessIgnore(self, test_dir, expected, ignore, include=()):
        codebase = Codebase(test_dir)
        test_plugin = ProcessIgnore()
        test_plugin.process_codebase(codebase, ignore=ignore, include=include)
        resources = [res.strip_root_path for res in codebase.walk(skip_root=True)]
        assert sorted(resources) == expected

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
        ignore = ('*/src/test/*',)
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc',
            'user/src/test' # test is included, but no file inside
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

    def test_ProcessIgnore_include_with_glob_for_extension(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        include = ('*.doc',)
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc',
            'user/src/test',
            'user/src/test/sample.doc',
        ]
        self.check_ProcessIgnore(test_dir, expected, ignore=(), include=include)

    def test_ProcessIgnore_process_codebase_does_not_fail_to_access_an_ignored_resourced_cached_to_disk(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        codebase = Codebase(test_dir, max_in_memory=1)
        test_plugin = ProcessIgnore()
        ignore = ['test']
        test_plugin.process_codebase(codebase, ignore=ignore)


class TestScanPluginIgnoreFiles(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_scancode_ignore_vcs_files_and_dirs_by_default(self):
        test_dir = self.extract_test_tar('plugin_ignore/vcs.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        # a single test.tst file and its directory that is not a VCS file should
        # be listed
        assert scan_result['headers'][0]['extra_data']['files_count'] == 1
        scan_locs = [x['path'] for x in scan_result['files']]
        assert scan_locs == [u'vcs', u'vcs/test.txt']

    def test_scancode_ignore_vcs_files_and_dirs_by_default_no_multiprocess(self):
        test_dir = self.extract_test_tar('plugin_ignore/vcs.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--processes', '0', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        # a single test.tst file and its directory that is not a VCS file should
        # be listed
        assert scan_result['headers'][0]['extra_data']['files_count'] == 1
        scan_locs = [x['path'] for x in scan_result['files']]
        assert scan_locs == [u'vcs', u'vcs/test.txt']

    def test_scancode_ignore_single_file(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', 'sample.doc', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 3
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
        assert scan_locs == expected

    def test_scancode_ignore_multiple_files(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', 'ignore.doc', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 2
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/src',
            u'user/src/test',
            u'user/src/test/sample.doc',
            u'user/src/test/sample.txt']
        assert scan_locs == expected

    def test_scancode_ignore_glob_files(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', '*.doc', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 1
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/src',
            u'user/src/test',
            u'user/src/test/sample.txt'
        ]
        assert scan_locs == expected

    def test_scancode_ignore_glob_path(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', '*/src/test/*', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 2
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/ignore.doc',
            u'user/src',
            u'user/src/ignore.doc',
            u'user/src/test'
        ]
        assert scan_locs == expected

    def test_scancode_multiple_ignores(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', '*/src/test/*', '--ignore', '*.doc', test_dir, '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 0
        scan_locs = [x['path'] for x in scan_result['files']]
        assert scan_locs == [u'user', u'user/src', u'user/src/test']

    def test_scancode_codebase_attempt_to_access_an_ignored_resourced_cached_to_disk(self):
        test_dir = self.extract_test_tar('plugin_ignore/user.tgz')
        result_file = self.get_temp_file('json')
        args = ['--copyright', '--strip-root', '--ignore', 'test', test_dir, '--max-in-memory', '1', '--json', result_file]
        run_scan_click(args)
        scan_result = load_json_result(result_file)
        assert scan_result['headers'][0]['extra_data']['files_count'] == 2
        scan_locs = [x['path'] for x in scan_result['files']]
        expected = [
            u'user',
            u'user/ignore.doc',
            u'user/src',
            u'user/src/ignore.doc',
            u'user/src/test',
        ]
        assert scan_locs == expected
