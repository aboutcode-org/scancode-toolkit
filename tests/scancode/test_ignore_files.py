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
from __future__ import unicode_literals

from os import path

from commoncode.testcase import FileBasedTesting
from commoncode.ignore import is_ignored
from scancode.cache import get_scans_cache_class
from scancode.cli import CommandOption
from scancode.cli import get_resources
from scancode.plugin_ignore import ProcessIgnore


class TestIgnoreFiles(FileBasedTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_ignore_glob_path(self):
        test = (
            'common/src/test/sample.txt',
            {'*/src/test/*': 'test ignore'},
            {}
        )
        assert is_ignored(*test)

    def test_ignore_single_path(self):
        test = (
            'common/src/test/sample.txt',
            {'src/test/sample.txt': 'test ignore'},
            {}
        )
        assert is_ignored(*test)

    def test_ignore_single_file(self):
        test = (
            'common/src/test/sample.txt',
            {'sample.txt': 'test ignore'},
            {}
        )
        assert is_ignored(*test)

    def test_ignore_glob_file(self):
        test = (
            'common/src/test/sample.txt',
            {'*.txt': 'test ignore'},
            {}
        )
        assert is_ignored(*test)

    def test_resource_paths_with_single_file(self):

        test_dir = self.extract_test_tar('ignore/user.tgz')
        test_plugins = [ProcessIgnore(
            [CommandOption(group=None, name='ignore', option='--ignore', value=('sample.doc',), default=None)]
        )]
        scan_cache_class = get_scans_cache_class(self.get_temp_dir())
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc',
            'user/src/test',
            'user/src/test/sample.txt'
        ]

        resources = get_resources(test_dir, scan_cache_class)
        for plugin in test_plugins:
            resources = plugin.process_resources(resources)

        resources = [resource.rel_path for resource in resources]
        assert expected == sorted(resources)

    def test_resource_paths_with_multiple_files(self):
        test_dir = self.extract_test_tar('ignore/user.tgz')
        test_plugins = [ProcessIgnore(
            [CommandOption(group=None, name='ignore', option='--ignore', value=('ignore.doc',), default=None)]
        )]
        scan_cache_class = get_scans_cache_class(self.get_temp_dir())
        expected = [
            'user',
            'user/src',
            'user/src/test',
            'user/src/test/sample.doc',
            'user/src/test/sample.txt'
        ]
        resources = get_resources(test_dir, scan_cache_class)
        for plugin in test_plugins:
            resources = plugin.process_resources(resources)

        resources = [resource.rel_path for resource in resources]
        assert expected == sorted(resources)

    def test_resource_paths_with_glob_file(self):
        test_dir = self.extract_test_tar('ignore/user.tgz')
        test_plugins = [ProcessIgnore(
            [CommandOption(group=None, name='ignore', option='--ignore', value=('*.doc',), default=None)]
        )]
        scan_cache_class = get_scans_cache_class(self.get_temp_dir())
        expected = [
            'user',
            'user/src',
            'user/src/test',
            'user/src/test/sample.txt'
        ]
        resources = get_resources(test_dir, scan_cache_class)
        for plugin in test_plugins:
            resources = plugin.process_resources(resources)

        resources = [resource.rel_path for resource in resources]
        assert expected == sorted(resources)

    def test_resource_paths_with_glob_path(self):
        test_dir = self.extract_test_tar('ignore/user.tgz')
        test_plugins = [ProcessIgnore(
            [CommandOption(group=None, name='ignore', option='--ignore', value=('*/src/test',), default=None)]
        )]
        scan_cache_class = get_scans_cache_class(self.get_temp_dir())
        expected = [
            'user',
            'user/ignore.doc',
            'user/src',
            'user/src/ignore.doc'
        ]
        resources = get_resources(test_dir, scan_cache_class)
        for plugin in test_plugins:
            resources = plugin.process_resources(resources)

        resources = [resource.rel_path for resource in resources]
        assert expected == sorted(resources)

    def test_resource_paths_with_multiple_plugins(self):
        test_dir = self.extract_test_tar('ignore/user.tgz')
        scan_cache_class = get_scans_cache_class(self.get_temp_dir())
        test_plugins = [
            ProcessIgnore(
                [CommandOption(group=None, name='ignore', option='--ignore', value=('*.doc',), default=None)]
            ),
            ProcessIgnore(
                [CommandOption(group=None, name='ignore', option='--ignore', value=('*/src/test/*',), default=None)]
            ),
        ]
        expected = [
            'user',
            'user/src',
            'user/src/test'
        ]
        resources = get_resources(test_dir, scan_cache_class)
        for plugin in test_plugins:
            resources = plugin.process_resources(resources)

        resources = [resource.rel_path for resource in resources]
        assert expected == sorted(resources)
