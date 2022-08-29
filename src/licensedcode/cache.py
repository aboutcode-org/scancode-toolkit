#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os
import pickle

import attr

from commoncode.datautils import attribute
from commoncode.fileutils import create_dir

from scancode_config import licensedcode_cache_dir
from scancode_config import scancode_cache_dir

"""
An on-disk persistent cache of LicenseIndex and related data structures such as
the licenses database. The data are pickled and must be regenerated if there
are any changes in the code or licenses text or rules. Loading and dumping the
cached pickle is safe to use across multiple processes using lock files.
"""

# This is the Pickle protocol we use, which was added in Python 3.4.
PICKLE_PROTOCOL = 4

# global in-memory cache of the LicenseCache
_LICENSE_CACHE = None

LICENSE_INDEX_LOCK_TIMEOUT = 60 * 4
LICENSE_INDEX_DIR = 'license_index'
LICENSE_INDEX_FILENAME = 'index_cache'
LICENSE_LOCKFILE_NAME = 'scancode_license_index_lockfile'
LICENSE_CHECKSUM_FILE = 'scancode_license_index_tree_checksums'


@attr.s(slots=True)
class LicenseCache:
    """
    Represent cachable/pickable LicenseIndex and index-related objects.
    """
    db = attribute(help='mapping of License objects by key')
    index = attribute(help='LicenseIndex object')
    licensing = attribute(help='Licensing object')
    spdx_symbols = attribute(help='mapping of LicenseSymbol objects by SPDX key')
    unknown_spdx_symbol = attribute(help='LicenseSymbol object')

    @staticmethod
    def load_or_build(
        licensedcode_cache_dir=licensedcode_cache_dir,
        scancode_cache_dir=scancode_cache_dir,
        force=False,
        index_all_languages=False,
        # used for testing only
        timeout=LICENSE_INDEX_LOCK_TIMEOUT,
        licenses_data_dir=None,
        rules_data_dir=None,
    ):
        """
        Load or build and save and return a LicenseCache object.

        We either load a cached LicenseIndex or build and cache the index.
        On the side, we load cached or build license db, SPDX symbols and other
        license-related data structures.

        - If the cache exists, it is returned unless corrupted or ``force`` is True.
        - If the cache does not exist, a new index is built and cached.
        - If ``index_all_languages`` is True, include texts in all languages when
          building the license index. Otherwise, only include the English license \
          texts and rules (the default)
        """
        idx_cache_dir = os.path.join(licensedcode_cache_dir, LICENSE_INDEX_DIR)
        create_dir(idx_cache_dir)
        cache_file = os.path.join(idx_cache_dir, LICENSE_INDEX_FILENAME)

        has_cache = os.path.exists(cache_file) and os.path.getsize(cache_file)

        # bypass build if cache exists
        if has_cache and not force:
            try:
                return load_cache_file(cache_file)
            except Exception as e:
                # work around some rare Windows quirks
                import traceback
                print('Inconsistent License cache: rebuilding index.')
                print(str(e))
                print(traceback.format_exc())

        from licensedcode.models import licenses_data_dir as ldd
        from licensedcode.models import rules_data_dir as rdd
        from licensedcode.models import load_licenses
        from scancode import lockfile

        licenses_data_dir = licenses_data_dir or ldd
        rules_data_dir = rules_data_dir or rdd

        lock_file = os.path.join(scancode_cache_dir, LICENSE_LOCKFILE_NAME)

        # here, we have no cache: lock, check and rebuild
        try:
            # acquire lock and wait until timeout to get a lock or die
            with lockfile.FileLock(lock_file).locked(timeout=timeout):
                # Here, the cache is either stale or non-existing: we need to
                # rebuild all cached data (e.g. mostly the index) and cache it

                licenses_db = load_licenses(licenses_data_dir=licenses_data_dir)

                index = build_index(
                    licenses_db=licenses_db,
                    licenses_data_dir=licenses_data_dir,
                    rules_data_dir=rules_data_dir,
                    index_all_languages=index_all_languages,
                )

                spdx_symbols = build_spdx_symbols(licenses_db=licenses_db)
                unknown_spdx_symbol = build_unknown_spdx_symbol(licenses_db=licenses_db)
                licensing = build_licensing(licenses_db=licenses_db)

                license_cache = LicenseCache(
                    db=licenses_db,
                    index=index,
                    licensing=licensing,
                    spdx_symbols=spdx_symbols,
                    unknown_spdx_symbol=unknown_spdx_symbol,
                )

                # save the cache as pickle new tree checksum
                with open(cache_file, 'wb') as fn:
                    pickle.dump(license_cache, fn, protocol=PICKLE_PROTOCOL)

                return license_cache

        except lockfile.LockTimeout:
            # TODO: handle unable to lock in a nicer way
            raise


def build_index(
    licenses_db=None,
    licenses_data_dir=None,
    rules_data_dir=None,
    index_all_languages=False,
):
    """
    Return an index built from rules and licenses directories

    If ``index_all_languages`` is True, include texts and rules in all languages.
    Otherwise, only include the English license texts and rules (the default)
    """
    from licensedcode.index import LicenseIndex
    from licensedcode.models import get_rules
    from licensedcode.models import get_all_spdx_key_tokens
    from licensedcode.models import get_license_tokens
    from licensedcode.models import licenses_data_dir as ldd
    from licensedcode.models import rules_data_dir as rdd
    from licensedcode.models import load_licenses
    from licensedcode.legalese import common_license_words

    licenses_data_dir = licenses_data_dir or ldd
    rules_data_dir = rules_data_dir or rdd

    licenses_db = licenses_db or load_licenses(licenses_data_dir=licenses_data_dir)
    rules = get_rules(licenses_db=licenses_db, rules_data_dir=rules_data_dir)

    legalese = common_license_words
    spdx_tokens = set(get_all_spdx_key_tokens(licenses_db))
    license_tokens = set(get_license_tokens())

    # only skip licenses to be indexed
    if not index_all_languages:
        rules = (r for r in rules if r.language == 'en')

    return LicenseIndex(
        rules,
        _legalese=legalese,
        _spdx_tokens=spdx_tokens,
        _license_tokens=license_tokens,
        _all_languages=index_all_languages,
    )


def build_licensing(licenses_db=None):
    """
    Return a `license_expression.Licensing` objet built from a `licenses_db`
    mapping of {key: License} or the standard license db.
    """
    from license_expression import LicenseSymbolLike
    from license_expression import Licensing
    from licensedcode.models import load_licenses

    licenses_db = licenses_db or load_licenses()
    return Licensing((LicenseSymbolLike(lic) for lic in licenses_db.values()))


def build_spdx_symbols(licenses_db=None):
    """
    Return a mapping of {lowercased SPDX license key: LicenseSymbolLike} where
    LicenseSymbolLike wraps a License object loaded from a `licenses_db` mapping
    of {key: License} or the standard license db.
    """
    from license_expression import LicenseSymbolLike
    from licensedcode.models import load_licenses

    licenses_db = licenses_db or load_licenses()

    licenses_by_spdx_key = get_licenses_by_spdx_key(
        licenses=licenses_db.values(),
        include_deprecated=False,
        lowercase_keys=True,
        include_other_spdx_license_keys=True,
    )

    return {
        spdx: LicenseSymbolLike(lic)
        for spdx, lic in licenses_by_spdx_key.items()
    }


def get_licenses_by_spdx_key(
    licenses=None,
    include_deprecated=False,
    lowercase_keys=True,
    include_other_spdx_license_keys=False,
):
    """
    Return a mapping of {SPDX license id: License} where license is a License
    object loaded from a `licenses` list of License or the standard
    license db if not provided.

    Optionally include deprecated if ``include_deprecated`` is True.


    Optionally make the keys lowercase if ``lowercase_keys`` is True.

    Optionally include the license "other_spdx_license_keys" if present and
    ``include_other_spdx_license_keys`` is True.
    """
    from licensedcode.models import load_licenses

    if not licenses:
        licenses = load_licenses().values()

    licenses_by_spdx_key = {}

    for lic in licenses:
        if not (lic.spdx_license_key or lic.other_spdx_license_keys):
            continue

        if lic.spdx_license_key:
            slk = lic.spdx_license_key
            if lowercase_keys:
                slk = slk.lower()
            existing = licenses_by_spdx_key.get(slk)
            if existing and not lic.is_deprecated:
                # temp hack for wharty ICU key!!
                if slk not in ('icu', 'ICU',):
                    raise ValueError(
                        f'Duplicated SPDX license key: {slk!r} defined in '
                        f'{lic.key!r} and {existing!r}'
                    )

            if (
                not lic.is_deprecated
                or (lic.is_deprecated and include_deprecated)
            ):
                licenses_by_spdx_key[slk] = lic

        if include_other_spdx_license_keys:
            for other_spdx in lic.other_spdx_license_keys:
                if not other_spdx or not other_spdx.strip():
                    continue
                slk = other_spdx
                if lowercase_keys:
                    slk = slk.lower()

                existing = licenses_by_spdx_key.get(slk)
                if existing:
                    raise ValueError(
                        f'Duplicated "other" SPDX license key: {slk!r} defined '
                        f'in {lic.key!r} and {existing!r}'
                    )

                licenses_by_spdx_key[slk] = lic

    return licenses_by_spdx_key


def build_unknown_spdx_symbol(licenses_db=None):
    """
    Return the unknown SPDX license symbol given a `licenses_db` mapping of
    {key: License} or the standard license db.
    """
    from license_expression import LicenseSymbolLike
    from licensedcode.models import load_licenses
    licenses_db = licenses_db or load_licenses()
    return LicenseSymbolLike(licenses_db['unknown-spdx'])


def get_cache(force=False, index_all_languages=False):
    """
    Return a LicenseCache either rebuilt, cached or loaded from disk.

    If ``index_all_languages`` is True, include texts in all languages when
    building the license index. Otherwise, only include the English license \
    texts and rules (the default)
    """
    populate_cache(force=force, index_all_languages=index_all_languages)
    global _LICENSE_CACHE
    return _LICENSE_CACHE


def populate_cache(force=False, index_all_languages=False):
    """
    Load or build and cache a LicenseCache. Return None.
    """
    global _LICENSE_CACHE
    if force or not _LICENSE_CACHE:
        _LICENSE_CACHE = LicenseCache.load_or_build(
            licensedcode_cache_dir=licensedcode_cache_dir,
            scancode_cache_dir=scancode_cache_dir,
            force=force,
            index_all_languages=index_all_languages,
            # used for testing only
            timeout=LICENSE_INDEX_LOCK_TIMEOUT,
        )


def load_cache_file(cache_file):
    """
    Return a LicenseCache loaded from ``cache_file``.
    """
    with open(cache_file, 'rb') as lfc:
        # Note: weird but read() + loads() is much (twice++???) faster than load()
        try:
            return pickle.load(lfc)
        except Exception as e:
            msg = (
                'ERROR: Failed to load license cache (the file may be corrupted ?).\n'
                f'Please delete "{cache_file}" and retry.\n'
                'If the problem persists, copy this error message '
                'and submit a bug report at https://github.com/nexB/scancode-toolkit/issues/'
            )
            raise Exception(msg) from e


def get_index(force=False, index_all_languages=False):
    """
    Return and eventually build and cache a LicenseIndex.
    """
    return get_cache(force=force, index_all_languages=index_all_languages).index


get_cached_index = get_index


def get_licenses_db():
    """
    Return a mapping of license key -> license object.
    """
    return get_cache().db


def get_licensing():
    """
    Return a license_expression.Licensing objet built from the all the licenses.
    """
    return get_cache().licensing


def get_unknown_spdx_symbol():
    """
    Return the unknown SPDX license symbol.
    """
    return get_cache().unknown_spdx_symbol


def get_spdx_symbols(licenses_db=None):
    """
    Return a mapping of {lowercased SPDX license key: LicenseSymbolLike} where
    LicenseSymbolLike wraps a License object
    """
    if licenses_db:
        return build_spdx_symbols(licenses_db)
    return get_cache().spdx_symbols


def build_spdx_license_expression(license_expression, licensing=None):
    """
    Return an SPDX license expression from a ScanCode ``license_expression``
    string.

    For example::
    >>> exp = "mit OR gpl-2.0 with generic-exception"
    >>> spdx = "MIT OR GPL-2.0-only WITH LicenseRef-scancode-generic-exception"
    >>> assert build_spdx_license_expression(exp) == spdx
    """
    if not licensing:
        licensing = get_licensing()
    parsed = licensing.parse(license_expression)
    return parsed.render(template='{symbol.wrapped.spdx_license_key}')
