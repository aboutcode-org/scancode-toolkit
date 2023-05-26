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

    def test_LicenseCache_load_or_build_from_empty(self):
        # recreate internal paths for testing
        licensedcode_cache_dir = self.get_temp_dir('index_cache')
        scancode_cache_dir = self.get_temp_dir('index_metafiles')
        idx_cache_dir = os.path.join(licensedcode_cache_dir, cache.LICENSE_INDEX_DIR)
        fileutils.create_dir(idx_cache_dir)
        cache_file = os.path.join(idx_cache_dir, cache.LICENSE_INDEX_FILENAME)
        lock_file = os.path.join(scancode_cache_dir, cache.LICENSE_LOCKFILE_NAME)

        licenses_data_dir = self.get_test_loc('cache/data/licenses', copy=True)
        rules_data_dir = self.get_test_loc('cache/data/rules', copy=True)

        assert not os.path.exists(cache_file)
        assert not os.path.exists(lock_file)

        timeout = 10

        # when a new cache is built, new cache files are created
        _cached1 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=False,
            timeout=timeout,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert os.path.exists(cache_file)
        fileutils.delete(cache_file)

        # force=True builds an index too if none exists
        _cached2 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=True,
            timeout=timeout,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert os.path.exists(cache_file)

        # force=True rebuilds an index
        idx_checksum_before = hash.sha1(cache_file)

        _cached3 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=True,
            timeout=timeout,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )

        assert hash.sha1(cache_file) != idx_checksum_before

        # force=False loads an index
        idx_checksum_before = hash.sha1(cache_file)

        _cached4 = cache.LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=False,
            timeout=timeout,
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=rules_data_dir,
        )
        assert hash.sha1(cache_file) == idx_checksum_before

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
        test_licenses = load_licenses(test_dir, check_consistency=False)
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
        test_licenses = load_licenses(test_dir, check_consistency=False)
        try:
            cache.get_spdx_symbols(licenses_db=test_licenses)
            self.fail('ValueError not raised!')
        except ValueError as e:
            msg = str(e)
            assert msg.startswith('Duplicated')
            assert 'SPDX license key' in msg

    def test_get_spdx_symbols_fails_on_duplicated_other_spdx_keys(self):
        test_dir = self.get_test_loc('spdx/db-dupe-other')
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(test_dir, check_consistency=False)
        try:
            cache.get_spdx_symbols(licenses_db=test_licenses)
            self.fail('ValueError not raised!')
        except ValueError as e:
            msg = str(e)
            assert msg.startswith('Duplicated')
            assert 'SPDX license key' in msg

    def test_get_spdx_symbols_checks_duplicates_with_deprecated_on_live_db(self):
        from licensedcode.models import load_licenses
        test_licenses = load_licenses(with_deprecated=True)
        cache.get_spdx_symbols(licenses_db=test_licenses)

    def test_build_spdx_license_expression(self):
        from licensedcode.cache import build_spdx_license_expression
        assert build_spdx_license_expression("mit")
    
    def test_build_spdx_license_expression_fails_on_invalid_key_none(self):
        from licensedcode.cache import build_spdx_license_expression
        from licensedcode.cache import InvalidLicenseKeyError
        try:
            build_spdx_license_expression("mit AND None")
        except InvalidLicenseKeyError:
            pass

    def test_build_spdx_license_expression_fails_on_deprecated_license(self):
        # TODO: this should not fail, see https://github.com/nexB/scancode-toolkit/issues/3400
        from licensedcode.cache import build_spdx_license_expression
        from licensedcode.cache import InvalidLicenseKeyError
        try:
            assert build_spdx_license_expression("broadcom-linking-unmodified")
        except InvalidLicenseKeyError:
            pass

    def test_build_spdx_license_expression_fails_on_invalid_key(self):
        from licensedcode.cache import build_spdx_license_expression
        from licensedcode.cache import InvalidLicenseKeyError
        try:
            assert build_spdx_license_expression("mitt")
        except InvalidLicenseKeyError:
            pass
