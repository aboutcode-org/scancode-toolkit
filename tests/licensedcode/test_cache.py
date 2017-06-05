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

import os

from commoncode.testcase import FileBasedTesting
from commoncode import date
from commoncode import fileutils
from commoncode import hash
from licensedcode import cache


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class LicenseIndexCacheTest(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_tree_checksum_ignores_some_files_and_directories(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)
        before = cache.tree_checksum(test_dir)
        # create some new pyc file and a dir
        with open(os.path.join(test_dir, 'some.pyc'), 'wb') as pyc:
            pyc.write('')
        fileutils.create_dir(os.path.join(test_dir, 'some dir'))

        after = cache.tree_checksum(test_dir)
        assert before == after

        with open(os.path.join(test_dir, 'some.py'), 'wb') as py:
            py.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before != after

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE'), 'wb') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before != after

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE~'), 'wb') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before == after

        with open(os.path.join(test_dir, 'some.LICENSE.swp'), 'wb') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before == after

    def test_tree_checksum_is_different_when_file_is_added(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)
        before = cache.tree_checksum(test_dir)

        with open(os.path.join(test_dir, 'some.py'), 'wb') as py:
            py.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before != after

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE'), 'wb') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert before != after

    def test_tree_checksum_is_different_when_file_is_changed(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)

        with open(os.path.join(test_dir, 'some.py'), 'wb') as py:
            py.write(' ')
        before = cache.tree_checksum(test_dir)

        with open(os.path.join(test_dir, 'some.py'), 'wb') as py:
            py.write(' asas')
        after = cache.tree_checksum(test_dir)
        assert before != after

    def test_tree_checksum_is_different_when_file_is_removed(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)

        new_file = os.path.join(test_dir, 'some.py')
        with open(new_file, 'wb') as py:
            py.write(' ')
        before = cache.tree_checksum(test_dir)

        fileutils.delete(new_file)
        after = cache.tree_checksum(test_dir)
        assert before != after

    def test_get_or_build_index_through_cache(self):
        # note: this is a rather complex test because caching involves some globals
        license_index_cache_dir = self.get_temp_dir('index_cache')
        _index_lock_file = os.path.join(license_index_cache_dir, 'lockfile')
        _tree_checksum_file = os.path.join(license_index_cache_dir, 'tree_checksums')
        _index_cache_file = os.path.join(license_index_cache_dir, 'index_cache')

        _tree_base_dir = self.get_temp_dir('src_dir')

        _licenses_dir = self.get_test_loc('cache/data', copy=True)
        _licenses_data_dir = os.path.join(_licenses_dir, 'licenses')
        _rules_data_dir = os.path.join(_licenses_dir, 'rules')

        _timeout = 10

        assert not os.path.exists(_tree_checksum_file)
        assert not os.path.exists(_index_cache_file)
        assert not os.path.exists(_index_lock_file)

        check_consistency = True
        return_index = False

        # when a new index is built, new index files are created
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)

        assert os.path.exists(_tree_checksum_file)
        assert os.path.exists(_index_cache_file)
        assert not os.path.exists(_index_lock_file)

        # when nothing changed a new index files is not created
        tree_before = open(_tree_checksum_file).read()
        idx_checksum_before = hash.sha1(_index_cache_file)
        idx_date_before = date.get_file_mtime(_index_cache_file)
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)
        assert tree_before == open(_tree_checksum_file).read()
        assert idx_checksum_before == hash.sha1(_index_cache_file)
        assert idx_date_before == date.get_file_mtime(_index_cache_file)

        # now add some file in the source tree
        new_file = os.path.join(_tree_base_dir, 'some file')
        with open(new_file, 'wb') as nf:
            nf.write('somthing')

        # when check_consistency is False, the index is not rebuild when
        # new files are added
        check_consistency = False
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)
        assert tree_before == open(_tree_checksum_file).read()
        assert idx_checksum_before == hash.sha1(_index_cache_file)
        assert idx_date_before == date.get_file_mtime(_index_cache_file)

        # when check_consistency is True, the index is rebuilt when new
        # files are added
        check_consistency = True
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)
        assert tree_before != open(_tree_checksum_file).read()
        assert idx_date_before != date.get_file_mtime(_index_cache_file)

        # now add some ignored file in the source tree
        tree_before = open(_tree_checksum_file).read()
        idx_checksum_before = hash.sha1(_index_cache_file)
        idx_date_before = date.get_file_mtime(_index_cache_file)
        new_file = os.path.join(_tree_base_dir, 'some file.pyc')
        with open(new_file, 'wb') as nf:
            nf.write('somthing')

        check_consistency = True
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)

        assert tree_before == open(_tree_checksum_file).read()
        assert idx_checksum_before == hash.sha1(_index_cache_file)
        assert idx_date_before == date.get_file_mtime(_index_cache_file)

        # if the treechecksum file dies the index is rebuilt
        fileutils.delete(_tree_checksum_file)
        idx_checksum_before = hash.sha1(_index_cache_file)

        check_consistency = False
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)

        assert tree_before == open(_tree_checksum_file).read()
        assert idx_date_before != date.get_file_mtime(_index_cache_file)

        # if the index cache file dies the index is rebuilt
        fileutils.delete(_index_cache_file)

        check_consistency = False
        cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)

        assert tree_before == open(_tree_checksum_file).read()
        assert os.path.exists(_index_cache_file)

    def test__load_index(self):
        license_index_cache_dir = self.get_temp_dir('index_cache')
        _index_lock_file = os.path.join(license_index_cache_dir, 'lockfile')
        _tree_checksum_file = os.path.join(license_index_cache_dir, 'tree_checksums')
        _index_cache_file = os.path.join(license_index_cache_dir, 'index_cache')

        _tree_base_dir = self.get_temp_dir('src_dir')

        _licenses_dir = self.get_test_loc('cache/data', copy=True)
        _licenses_data_dir = os.path.join(_licenses_dir, 'licenses')
        _rules_data_dir = os.path.join(_licenses_dir, 'rules')

        _timeout = 10

        assert not os.path.exists(_tree_checksum_file)
        assert not os.path.exists(_index_cache_file)
        assert not os.path.exists(_index_lock_file)

        check_consistency = True
        return_index = True

        # Create a basic index
        idx1 = cache.get_or_build_index_through_cache(
            check_consistency,
            return_index,
            _tree_base_dir,
            _tree_checksum_file,
            _index_lock_file,
            _index_cache_file,
            _licenses_data_dir,
            _rules_data_dir,
            _timeout)

        assert os.path.exists(_tree_checksum_file)
        assert os.path.exists(_index_cache_file)
        assert not os.path.exists(_index_lock_file)

        idx2 = cache._load_index(_index_cache_file)
        assert idx1.to_dict(True) == idx2.to_dict(True)
