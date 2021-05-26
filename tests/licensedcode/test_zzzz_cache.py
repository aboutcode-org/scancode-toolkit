#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.testcase import FileBasedTesting
from commoncode import fileutils
from commoncode import hash
from licensedcode import cache

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

pytestmark = pytest.mark.scanslow


class LicenseIndexCacheTest(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_tree_checksum_ignores_some_files_and_directories(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)
        before = cache.tree_checksum(test_dir)
        # create some new pyc file and a dir
        with open(os.path.join(test_dir, 'some.pyc'), 'w') as pyc:
            pyc.write('')
        fileutils.create_dir(os.path.join(test_dir, 'some dir'))

        after = cache.tree_checksum(test_dir)
        assert after == before

        with open(os.path.join(test_dir, 'some.py'), 'w') as py:
            py.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after != before

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE'), 'w') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after != before

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE~'), 'w') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after == before

        with open(os.path.join(test_dir, 'some.LICENSE.swp'), 'w') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after == before

    def test_tree_checksum_does_not_ignore_the_index_cache(self):
        # this is stored in the code tree as package data and we should not
        # ignore it
        test_dir = self.get_test_loc('cache/tree', copy=True)
        before = cache.tree_checksum(test_dir)
        # create some file name like the index
        with open(os.path.join(test_dir, cache.LICENSE_INDEX_FILENAME), 'w') as pyc:
            pyc.write(' ')
        fileutils.create_dir(os.path.join(test_dir, 'some dir'))
        after = cache.tree_checksum(test_dir)
        assert after != before

    def test_tree_checksum_is_different_when_file_is_added(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)
        before = cache.tree_checksum(test_dir)

        with open(os.path.join(test_dir, 'some.py'), 'w') as py:
            py.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after != before

        before = after
        with open(os.path.join(test_dir, 'some.LICENSE'), 'w') as f:
            f.write(' ')
        after = cache.tree_checksum(test_dir)
        assert after != before

    def test_tree_checksum_is_different_when_file_is_changed(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)

        with open(os.path.join(test_dir, 'some.py'), 'w') as py:
            py.write(' ')
        before = cache.tree_checksum(test_dir)

        with open(os.path.join(test_dir, 'some.py'), 'w') as py:
            py.write(' asas')
        after = cache.tree_checksum(test_dir)
        assert after != before

    def test_tree_checksum_is_different_when_file_is_removed(self):
        test_dir = self.get_test_loc('cache/tree', copy=True)

        new_file = os.path.join(test_dir, 'some.py')
        with open(new_file, 'w') as py:
            py.write(' ')
        before = cache.tree_checksum(test_dir)

        fileutils.delete(new_file)
        after = cache.tree_checksum(test_dir)
        assert after != before

    def test_LicenseCache_load_or_build(self):

        # recreate internal paths for testing
        licensedcode_cache_dir = self.get_temp_dir('index_cache')
        scancode_cache_dir = self.get_temp_dir('index_metafiles')
        idx_cache_dir = os.path.join(licensedcode_cache_dir, cache.LICENSE_INDEX_DIR)
        fileutils.create_dir(idx_cache_dir)
        cache_file = os.path.join(idx_cache_dir, cache.LICENSE_INDEX_FILENAME)
        lock_file = os.path.join(scancode_cache_dir, cache.LICENSE_LOCKFILE_NAME)
        checksum_file = os.path.join(scancode_cache_dir, cache.LICENSE_CHECKSUM_FILE)

        tree_base_dir = self.get_temp_dir('src_dir')
        licenses_data_dir = self.get_test_loc('cache/data/licenses', copy=True)
        rules_data_dir = self.get_test_loc('cache/data/rules', copy=True)

        # now add some file in the mock source tree
        new_file = os.path.join(tree_base_dir, 'some.py')
        with open(new_file, 'w') as nf:
            nf.write('somthing')

        assert not os.path.exists(checksum_file)
        assert not os.path.exists(cache_file)
        assert not os.path.exists(lock_file)

        timeout = 10

        # when a new cache is built, new cache files are created
        check_consistency = True
        _cached1 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert os.path.exists(checksum_file)
        assert os.path.exists(cache_file)

        # when nothing changed a new index files is not created
        tree_before = open(checksum_file).read()
        idx_checksum_before = hash.sha1(cache_file)
        _cached2 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert open(checksum_file).read() == tree_before
        assert hash.sha1(cache_file) == idx_checksum_before

        # now add some file in the source tree
        new_file = os.path.join(tree_base_dir, 'some file')
        with open(new_file, 'w') as nf:
            nf.write('somthing')

        # when check_consistency is False, the index is not rebuild when
        # new files are added
        check_consistency = False
        _cached3 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )
        assert open(checksum_file).read() == tree_before
        assert hash.sha1(cache_file) == idx_checksum_before

        # when check_consistency is True, the index is rebuilt when new
        # files are added
        check_consistency = True
        _cached4 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )
        assert open(checksum_file).read() != tree_before

        # now add some ignored file in the source tree
        tree_before = open(checksum_file).read()
        idx_checksum_before = hash.sha1(cache_file)
        new_file = os.path.join(tree_base_dir, 'some file.pyc')
        with open(new_file, 'w') as nf:
            nf.write('somthing')

        # when check_consistency is True, the index is not rebuilt when new
        # files are added that are ignored
        check_consistency = True
        _cached5 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert open(checksum_file).read() == tree_before
        assert hash.sha1(cache_file) == idx_checksum_before

        # if the treechecksum file dies, the index is not rebuilt if
        # check_consistency is False. and no new checksum is created
        fileutils.delete(checksum_file)
        idx_checksum_before = hash.sha1(cache_file)

        check_consistency = False
        _cached6 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert not os.path.exists(checksum_file)

        # with the treechecksum file gone, the index is rebuilt if
        # check_consistency is True and a new checksum is created
        idx_checksum_before = hash.sha1(cache_file)

        check_consistency = True
        _cached7 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert open(checksum_file).read() == tree_before

        # if the index cache file dies the index is rebuilt
        fileutils.delete(cache_file)
        check_consistency = False
        cached8 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            check_consistency=check_consistency,
            timeout=timeout,
            tree_base_dir=tree_base_dir,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )
        idx1 = cached8.index

        # load index, forced from file
        cached9 = cache.load_cache_file(cache_file)
        idx2 = cached9.index
        assert set(idx2.dictionary.keys()) == set(idx1.dictionary.keys())

    def test_load_index_with_corrupted_index(self):
        test_file = self.get_temp_file('test')
        with open(test_file, 'w') as tf:
            tf.write('some junk')
        try:
            cache.load_cache_file(test_file)
            self.fail('No exception raised for corrupted index file.')
        except Exception as ex:
            assert 'Failed to load license cache' in str(ex)

    def test_get_unknown_spdx_symbol(self):
        assert cache.get_unknown_spdx_symbol().key == 'unknown-spdx'

    def test_get_spdx_symbols_from_dir(self):
        test_dir = self.get_test_loc('spdx/db')
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(test_dir)
        result = {
            key: val.key for key, val
            in cache.get_spdx_symbols(licenses_db=test_licenses).items()
        }
        expected = {
            u'bar': u'xxd',
            u'foo': u'xxd',
            u'qt-lgpl-exception-1.1': u'qt-lgpl-exception-1.1',
            u'xskat': u'xskat'
        }

        assert result == expected

    def test_get_spdx_symbols(self):
        result = cache.get_spdx_symbols()
        assert 'mit' in result

    def test_get_spdx_symbols_fails_on_duplicates(self):
        test_dir = self.get_test_loc('spdx/db-dupe')
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(test_dir)
        try:
            cache.get_spdx_symbols(licenses_db=test_licenses)
            self.fail('ValueError not raised!')
        except ValueError as e:
            assert 'Duplicated SPDX license key' in str(e)

    def test_get_spdx_symbols_fails_on_duplicated_other_spdx_keys(self):
        test_dir = self.get_test_loc('spdx/db-dupe-other')
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(test_dir)
        try:
            cache.get_spdx_symbols(licenses_db=test_licenses)
            self.fail('ValueError not raised!')
        except ValueError as e:
            assert 'Duplicated "other" SPDX license key' in str(e)

    def test_get_spdx_symbols_checks_duplicates_with_deprecated_on_live_db(self):
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(with_deprecated=True)
        cache.get_spdx_symbols(licenses_db=test_licenses)
