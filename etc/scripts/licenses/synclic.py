# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os
from os import mkdir
from os.path import exists
from os.path import join
from os.path import realpath
from pprint import pprint
import textwrap
import zipfile

import click
import requests

from commoncode import fetch
from commoncode import fileutils

import licensedcode
from licensedcode.models import load_licenses
from licensedcode.models import License

"""
Sync and update the ScanCode licenses against:
 - the SPDX license list
 - the DejaCode licenses

Run python synclic.py -h for help.
"""

TRACE = True
TRACE_ADD = True
TRACE_FETCH = True
TRACE_DEEP = False

# may be useful to change for testing
SPDX_DEFAULT_REPO = 'spdx/license-list-data'


class ScanCodeLicenses(object):
    """
    Licenses from the current ScanCode installation
    """

    def __init__(self):
        self.by_key = load_licenses(with_deprecated=True)
        self.by_spdx_key = get_licenses_by_spdx_key(self.by_key.values())

        # TODO: not yet used
        foreign_dir = join(licensedcode.models.data_dir, 'non-english', 'licenses')
        self.non_english_by_key = load_licenses(foreign_dir, with_deprecated=True)
        self.non_english_by_spdx_key = get_licenses_by_spdx_key(self.non_english_by_key.values())

    def clean(self):
        """
        Redump licenses YAML applying some reformating.
        """

        def _clean(licenses):
            for lic in licenses.values():
                updated = False
                if lic.standard_notice:
                    updated = True
                    lic.standard_notice = clean_text(lic.standard_notice)
                if lic.notes:
                    updated = True
                    lic.notes = clean_text(lic.notes)

                if updated:
                    lic.dump()

        for lics in [self.by_key, self.non_english_by_key]:
            _clean(lics)


def get_licenses_by_spdx_key(licenses, include_other=False):
    """
    Return a mapping of {spdx_key: license object} given a sequence of License objects.
    """
    by_spdx = {}
    for lic in licenses:
        if not (lic.spdx_license_key or lic.other_spdx_license_keys):
            continue

        if lic.spdx_license_key:
            slk = lic.spdx_license_key.lower()
            existing = by_spdx.get(slk)
            if existing and not lic.is_deprecated:
                key = lic.key
                # temp hack!!
                if slk != 'icu':
                    raise ValueError('Duplicated SPDX license key: %(slk)r defined in %(key)r and %(existing)r' % locals())
            if not lic.is_deprecated:
                by_spdx[slk] = lic

        if include_other:
            for other_spdx in lic.other_spdx_license_keys:
                if not (other_spdx and other_spdx.strip()):
                    continue
                slk = other_spdx.lower()
                existing = by_spdx.get(slk)
                if existing:
                    raise ValueError('Duplicated "other" SPDX license key: %(slk)r defined in %(key)r and %(existing)r' % locals())
                by_spdx[slk] = lic

    return by_spdx


class ExternalLicensesSource(object):
    """
    Base class to provide (including possibly fetch) licenses from an
    external source and expose these as licensedcode.models.License
    objects
    """
    # key_attribute is the License object attribute to use for key matching
    # between external and scancode: one of "key" or "spdx_license_key"
    key_attribute = None

    # tuple of ScanCode reference license attributes that can be updated
    # from this source
    updatable_attributes = tuple()

    # tuple of ScanCode reference license attributes that cannot be updated
    # from this source. They can only be set when creating a new license.
    non_updatable_attributes = tuple()

    def __init__(self, external_base_dir):
        """
        `external_base_dir` is the base directory where the License objects are
        dumped as a pair of .LICENSE/.yml files.
        """
        external_base_dir = realpath(external_base_dir)
        self.external_base_dir = external_base_dir

        # we use four sub-directories:
        # we store the original fetched licenses in this directory
        self.original_dir = os.path.join(external_base_dir, 'original')
        # we store updated external licenses in this directory
        self.update_dir = os.path.join(external_base_dir, 'updated')
        # we store new external licenses in this directory
        self.new_dir = os.path.join(external_base_dir, 'new')

        self.fetched = False
        if exists(self.original_dir):
            # fetch ONLY if the directory is non-existing
            self.fetched = True
        else:
            mkdir(self.original_dir)

        if not exists(self.update_dir):
            mkdir(self.update_dir)

        if not exists(self.new_dir):
            mkdir(self.new_dir)

    def get_licenses(self, scancode_licenses=None, **kwargs):
        """
        Return a mapping of key -> ScanCode License objects either fetched
        externally or loaded from the existing `self.original_dir`
        """
        print('Fetching and storing external licenses in:', self.original_dir)

        licenses = []
        for lic, text in self.fetch_licenses(scancode_licenses=scancode_licenses, **kwargs):
            try:
                with io.open(lic.text_file, 'w', encoding='utf-8')as tf:
                    tf.write(text)
                lic.dump()
                licenses.append(lic)
            except:
                if TRACE:
                    print()
                    print(repr(lic))
                raise

        print('Stored %d external licenses in: %r.' % (len(licenses), self.original_dir,))

        print('Modified (or not modified) external licenses will be in: %r.' % (self.update_dir,))
        fileutils.copytree(self.original_dir, self.update_dir)

        print('New external licenses will be in: %r.' % (self.new_dir,))

        return load_licenses(self.update_dir, with_deprecated=True)

    def fetch_licenses(self, scancode_licenses, **kwargs):
        """
        Yield tuples of (License object, license text) fetched from this external source.
        """
        raise NotImplementedError


def get_key_through_text_match(key, text, scancode_licenses, match_approx=False):
    """
    Match text and returna matched license key or None
    """
    if TRACE_DEEP: print('Matching text for:', key, end='. ')
    new_key, exact, score, match_text = get_match(text)
    if not new_key:
        if TRACE_DEEP: print('Not TEXT MATCHED:', key, end='. ')
        return None
    if exact is True and score == 100:
        if TRACE_DEEP: print('EXACT match to:', new_key, 'text:\n', match_text)
        return new_key

    if match_approx:
        if exact is False:
            if TRACE_DEEP: print('OK matched to:', new_key, 'with score:', score, 'text:\n', match_text)
            return new_key

        if exact is None:
            if TRACE_DEEP: print('WEAK matched to:', new_key, 'with score:', score, 'text:\n', match_text)
            return new_key

        if exact == -1:
            if TRACE_DEEP: print('JUNK MATCH to:', new_key, 'with score:', score, 'text:\n', match_text)
            return new_key

    else:
        if TRACE_DEEP:print('SKIPPED: WEAK/JUNK MATCH to:', new_key, 'with score:', score, 'text:\n', match_text)


def get_match(text):
    """
    Return a tuple of (license key, True if exact match, match score, match text)
    e.g.:
        - top matched license key or None,
        - True if this an exact match, False if the match is ok, None if the match is weak,
        - match score or 0 or None
        - matched text or None
    """

    from licensedcode.cache import get_index

    idx = get_index()
    matches = list(idx.match(query_string=text, min_score=80))
    if not matches:
        return None, None, 0, None

    match = matches[0]
    matched_text = match.matched_text(whole_lines=False)
    query = match.query
    query_len = len(query.whole_query_run().tokens)
    rule = match.rule
    rule_licenses = rule.license_keys()
    key = rule_licenses[0]

    is_exact = (
        len(matches) == 1
        and rule.is_from_license and len(rule_licenses) == 1
        and match.matcher == '1-hash'
        and match.score() == 100
        and match.len() == query_len
    )

    if is_exact:
        return key, True, 100, matched_text

    is_ok = (
        len(rule_licenses) == 1
        and match.coverage() > 95
        and match.score() > 95)
    if is_ok:
        return key, False, match.score(), matched_text

    is_weak = (
        len(rule_licenses) == 1
        and match.coverage() > 90
        and match.score() > 90)
    if is_weak:
        return key, None, match.score(), matched_text

    if match.score() > 85:
        # junk match
        return key, -1, match.score(), matched_text
    else:
        return None, None, None, None


def get_response(url, headers, params):
    """
    Return a native Python object of the JSON response of a GET HTTP
    request at `url` with `headers` and `params`.
    """

    if TRACE_FETCH: print('==> Fetching URL: %(url)s' % locals())
    response = requests.get(url, headers=headers, params=params)
    status = response.status_code
    if status != requests.codes.ok:  # NOQA
        raise Exception('Failed HTTP request for %(url)r: %(status)r' % locals())
    return response.json()


def clean_text(text):
    """
    Return a cleaned and formatted version of text
    """
    if not text:
        return text
    text = text.strip()
    lines = text.splitlines(False)
    formatted = []
    for line in lines:
        line = ' '.join(line.split())
        line = textwrap.wrap(line, width=75)
        formatted.extend(line)
    return '\n'.join(formatted)


class SpdxSource(ExternalLicensesSource):
    """
    License source for the latest SPDX license list fetched from GitHub.
    """

    matching_key = 'spdx_license_key'

    updatable_attributes = (
        'spdx_license_key',
        'other_urls',
        'is_deprecated',
        'is_exception',
        # 'standard_notice',
    )

    non_updatable_attributes = (
        'short_name',
        'name',
        'notes',
    )

    def fetch_licenses(
        self,
        scancode_licenses=None,
        commitish=None,
        skip_oddities=True,
        from_repo=SPDX_DEFAULT_REPO,
    ):
        """
        Yield License objects fetched from the latest SPDX license list. Use the
        latest tagged version or the `commitish` if provided.
        If skip_oddities is True, some oddities are skipped or handled
        specially, such as licenses with a trailing + or foreign language
        licenses.
        """
        if not commitish:
            # get latest tag
            tags_url = 'https://api.github.com/repos/{from_repo}/tags'.format(**locals())
            tags = get_response(tags_url, headers={}, params={})
            tag = tags[0]['name']
        else:
            tag = commitish

        # fetch licenses and exceptions
        # note that exceptions data have -- weirdly enough -- a different schema
        zip_url = 'https://github.com/{from_repo}/archive/{tag}.zip'.format(**locals())
        if TRACE_FETCH: print('Fetching SPDX license data version:', tag, 'from:', zip_url)
        licenses_zip = fetch.download_url(zip_url, timeout=120)
        if TRACE_FETCH: print('Fetched SPDX licenses to:', licenses_zip)
        with zipfile.ZipFile(licenses_zip) as archive:
            for path in archive.namelist():
                if not (path.endswith('.json')
                and ('/json/details/' in path or '/json/exceptions/' in path)):
                    continue
                if TRACE_FETCH: print('Loading license:', path)
                if skip_oddities and path.endswith('+.json'):
                    # Skip the old plus licenses. We use them in
                    # ScanCode, but they are deprecated in SPDX.
                    continue
                details = json.loads(archive.read(path))
                lic = self.build_license(
                    mapping=details,
                    scancode_licenses=scancode_licenses,
                    skip_oddities=skip_oddities,
                )

                if lic:
                    yield lic

    def build_license(self, mapping, skip_oddities=True, scancode_licenses=None):
        """
        Return a ScanCode License object built from an SPDX license mapping.
        If skip_oddities is True, some oddities are skipped or handled
        specially, such as licenses with a trailing + or foreign language
        licenses.
        """
        spdx_license_key = mapping.get('licenseId') or mapping.get('licenseExceptionId')
        assert spdx_license_key
        spdx_license_key = spdx_license_key.strip()
        key = spdx_license_key.lower()

        # TODO: Not yet available in ScanCode
        is_foreign = scancode_licenses and key in scancode_licenses.non_english_by_spdx_key
        if skip_oddities and is_foreign:
            if TRACE: print('Skipping NON-english license FOR NOW:', key)
            return

        # these keys have a complicated history
        if skip_oddities and key in set([
            'gpl-1.0', 'gpl-2.0', 'gpl-3.0',
            'lgpl-2.0', 'lgpl-2.1', 'lgpl-3.0',
            'agpl-1.0', 'agpl-2.0', 'agpl-3.0',
            'gfdl-1.1', 'gfdl-1.2', 'gfdl-1.3',
            'nokia-qt-exception-1.1',
            'bzip2-1.0.5',
            'bsd-2-clause-freebsd',
            'bsd-2-clause-netbsd',
        ]):
            return

        deprecated = mapping.get('isDeprecatedLicenseId', False)
        if skip_oddities and deprecated:
            # we use concrete keys for some plus/or later versions for
            # simplicity and override SPDX deprecation for these
            if key.endswith('+'):
                # 'gpl-1.0+', 'gpl-2.0+', 'gpl-3.0+',
                # 'lgpl-2.0+', 'lgpl-2.1+', 'lgpl-3.0+',
                # 'gfdl-1.1+', 'gfdl-1.2+', 'gfdl-1.3+'
                # 'agpl-3.0+'
                deprecated = False

        # TODO: handle other_spdx_license_keys in license yaml files.

        other_urls = mapping.get('seeAlso', [])
        other_urls = (o for o in other_urls if o)
        other_urls = (o.strip() for o in other_urls)
        other_urls = (o for o in other_urls if o)
        # see https://github.com/spdx/license-list-data/issues/9
        junk_see_also = ('none', 'found')
        other_urls = (o for o in other_urls if o not in junk_see_also)

        other_urls = list(other_urls)

        standard_notice = mapping.get('standardLicenseHeader') or ''
        if standard_notice:
            standard_notice = clean_text(standard_notice)

        lic = License(
            key=key,
            src_dir=self.original_dir,
            spdx_license_key=spdx_license_key,
            name=mapping['name'].strip(),
            short_name=mapping['name'].strip(),
            is_deprecated=deprecated,
            is_exception=bool(mapping.get('licenseExceptionId')),
            other_urls=other_urls,

            # TODO: the formatting might need to be preserved
            standard_notice=standard_notice,

            # FIXME: Do we really want to carry notes over???
            # notes=notes,

            # FIXME: available in ScanCode but as an OSI URL
            # we should check if we have the osi_url when this flag is there?
            # osi_url = mapping.get('isOsiApproved', False)

            # TODO: detect licenses on these texts to ensure they match?
            # TODO: add rule? and test license detection???
            # standard_template = mapping('standardLicenseTemplate')
            # exception_example
            # example = mapping.get('example')
        )
        text = mapping.get('licenseText') or mapping.get('licenseExceptionText')
        text = text.strip()
        return lic, text


class DejaSource(ExternalLicensesSource):
    """
    License source for DejaCode licenses fetched through its API.
    """
    key_attribute = 'key'

    updatable_attributes = (
        'short_name',
        'name',
        'spdx_license_key',
        'homepage_url',
        'category',
        'owner',
        'text_urls',
        'osi_url',
        'faq_url',
        'other_urls',
        'is_deprecated',
        'is_exception',
        # NOT YET: 'standard_notice',
    )
    non_updatable_attributes = (
        'notes',
    )

    def __init__(self, external_base_dir, api_base_url=None, api_key=None):
        self.api_base_url = api_base_url or os.getenv('DEJACODE_API_URL')
        self.api_key = api_key or os.getenv('DEJACODE_API_KEY')
        assert (self.api_key and self.api_base_url), (
            'You must set the DEJACODE_API_URL and DEJACODE_API_KEY ' +
            'environment variables before running this script.')

        super(DejaSource, self).__init__(external_base_dir)

    def fetch_licenses(self, scancode_licenses, **kwargs):
        api_url = '/'.join([self.api_base_url.rstrip('/'), 'licenses/'])
        for licenses in call_deja_api(api_url, self.api_key, paginate=100):
            for lic in licenses:
                dlic = self.build_license(lic, scancode_licenses)
                if dlic:
                    yield dlic

    def build_license(self, mapping, scancode_licenses):
        """
        Return a ScanCode License object built from a DejaCode license
        mapping or None for skipped licenses.
        """
        key = mapping['key']

        # TODO: Not yet available in ScanCode
        is_foreign = key in scancode_licenses.non_english_by_key
        if is_foreign:
            if TRACE: print('Skipping NON-english license:', key)
            return

        # these licenses are rare commercial license with no text and only a
        # link so we ignore these
        dejacode_special_no_text = set([
            'alglib-commercial',
            'atlassian-customer-agreement',
            'dalton-maag-eula',
            'highsoft-standard-license-agreement-4.0',
            'monotype-tou',
            ])
        is_special = key in dejacode_special_no_text
        if is_special:
            if TRACE: print('Skipping special DejaCode license with NO TEXT FOR NOW:', key)
            return

        # these licenses are combos of many others and are ignored: we detect
        # instead each part of the combo
        dejacode_special_composites = set([
              'intel-bsd-special',
            ])
        is_combo = key in dejacode_special_composites
        if is_combo:
            if TRACE: print('Skipping DejaCode combo license', key)
            return

        deprecated = not mapping.get('is_active')
        if deprecated and key not in scancode_licenses.by_key:
            if TRACE: print('Skipping deprecated license not in ScanCode:', key)
            return

        standard_notice = mapping.get('standard_notice') or ''
        standard_notice = clean_text(standard_notice)

        lic = License(
            key=key,
            src_dir=self.original_dir,
            name=mapping['name'],
            short_name=mapping['short_name'],
            homepage_url=mapping['homepage_url'],

            category=mapping['category'],
            owner=mapping['owner_name'],

            # FIXME: we may not want to carry notes over???
            # lic.notes = mapping.notes
            spdx_license_key=mapping['spdx_license_key'],
            text_urls=mapping['text_urls'].splitlines(False),
            osi_url=mapping['osi_url'],
            faq_url=mapping['faq_url'],
            other_urls=mapping['other_urls'].splitlines(False),
            is_exception=mapping.get('is_exception', False),
            is_deprecated=deprecated,
            standard_notice=standard_notice,
        )
        text = mapping['full_text'] or ''
        # normalize EOL to POSIX
        text = text.replace('\r\n', '\n').strip()
        return lic, text

    def check_owners(self, licenses):
        """
        Check that all licenses have a proper owner. Return a list of owners
        that do not exists.
        """
        downers = set()
        for lic in licenses:
            lico = lic.owner
            owner = get_owner(self.api_base_url, self.api_key, lico)
            if not owner:
                downers.add(lico)
        return sorted(downers)


def call_deja_api(api_url, api_key, paginate=0, headers=None, params=None):
    """
    Yield result mappings from the reponses of calling the API at
    `api_url` with `api_key` . Raise an exception on failure.

    Pass `headers` and `params` mappings to the
    underlying request if provided.
    If `paginate` is a non-zero attempt to paginate with `paginate`
    number of pages at a time and return all the results.
    """
    headers = headers or {
        'Authorization': 'Token {}'.format(api_key),
        'Accept': 'application/json; indent=2',
    }

    params = params or {}

    def _get_results(response):
        return response.json()

    if paginate:
        assert isinstance(paginate, int)
        params['page_size'] = paginate

        first = True
        while True:
            response = get_response(api_url, headers, params)
            if first:
                first = False
                # use page_size only on first call.
                # the next URL already contains the page_size
                params.pop('page_size')

            yield response.get('results', [])

            api_url = response.get('next')
            if not api_url:
                break
    else:
        response = get_response(api_url, headers, params)
        yield response.get('results', [])


def create_license(api_url, api_key, lico):
    """
    Post the `lico` License object to the DejaCode API at `api_url` with
    `api_key` . Raise an exception on failure.
    """
    owner = get_or_create_owner(api_url, api_key, lico.owner, create=True)

    url = api_url.rstrip('/')
    url = '{url}/licenses/'.format(**locals())

    headers = {
        'Authorization': 'Token {}'.format(api_key),
        'Content-Type': 'application/json',
        'Accept': 'application/json; indent=2',
    }

    # recheck that the license key does not exists remotely
    params = dict(key=lico.key)
    # note: we get PARAMS
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception('Failed to get license for {name} at {url}:\n{headers}\n{content}'.format(**locals()))

    results = response.json().get('results', [])

    if results:
        if TRACE:
            print('License already exists:', lico)
        return

    data = license_to_dict(lico)

    response = requests.post(url, headers=headers, json=data)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception('Failed to create license: {lico} at {url}:\n{headers}\n{content}'.format(**locals()))

    print('Created new license:', lico)
    results = response.json()
    if TRACE_DEEP:
        pprint(results)
    return results


def get_or_create_owner(api_url, api_key, name, create=False):
    """
    Check if owner name exists. If `create` create the owner if it does not
    exists in the DejaCode API at `api_url` with `api_key`. Raise an exception
    on failure.
    """

    owner = get_owner(api_url, api_key, name)
    if owner:
        if TRACE:
            print('Owner exists:', name)
            if TRACE_DEEP:
                pprint(owner)
        return owner

    if not create:
        if TRACE:
            print('No existing owner:', name)
        return

    url = api_url.rstrip('/')
    url = '{url}/owners/'.format(**locals())
    headers = {
        'Authorization': 'Token {}'.format(api_key),
        'Content-Type': 'application/json',
        'Accept': 'application/json; indent=2',
    }
    # note: we post JSON
    params = dict(name=name.strip())
    response = requests.post(url, headers=headers, json=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception('Failed to create owner request for {name} at {url}:\n{headers}\n{content}'.format(**locals()))

    result = response.json()
    if TRACE:
        print('Created new owner:', name)
        if TRACE_DEEP:
            pprint(result)
    return result


def get_owner(api_url, api_key, name):
    """
    Check if owner name exists in the DejaCode API at `api_url` with `api_key`.
    Raise an exception on failure. Return None if the name does not exist and
    the owner data otherwise
    """
    headers = {
        'Authorization': 'Token {}'.format(api_key),
        'Accept': 'application/json; indent=2',
    }
    params = dict(name=name.strip())
    url = api_url.rstrip('/')
    url = '{url}/owners/'.format(**locals())
    # note: we get PARAMS
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception('Failed to get owner for {name} at {url}:\n{headers}\n{content}'.format(**locals()))

    results = response.json().get('results', [])

    if results:
        result = results[0]
        if TRACE_DEEP:
            print('Existing owner:', name)
            pprint(result)
        return result


def license_to_dict(lico):
    """
    Return an dict of license data with texts for API calls.
    Fields with empty values are not included.
    """
    licm = dict(
        is_active=False,
        reviewed=False,
        license_status='NotReviewed',
        is_component_license=False,
        key=lico.key,
        short_name=lico.short_name,
        name=lico.name,
        category=lico.category,
        owner=lico.owner,
        is_exception=lico.is_exception
    )
    if lico.text:
        licm.update(full_text=lico.text)
    if lico.homepage_url:
        licm.update(homepage_url=lico.homepage_url)
    if lico.spdx_license_key:
        licm.update(spdx_license_key=lico.spdx_license_key)
    if lico.notes:
        licm.update(reference_notes=lico.notes)
    if lico.text_urls:
        licm.update(text_urls='\n'.join(lico.text_urls))
    if lico.osi_url:
        licm.update(osi_url=lico.osi_url)
    if lico.faq_url:
        licm.update(faq_url=lico.faq_url)
    if lico.other_urls:
        licm.update(other_urls='\n'.join(lico.other_urls))
    return licm


EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES = {
    'dejacode': DejaSource,
    'spdx': SpdxSource,
}


def merge_licenses(scancode_license, external_license, updatable_attributes,
                   from_spdx=False):
    """
    Compare and update two License objects in-place given a sequence of
    `updatable_attributes`.
    Return a two-tuple of lists as:
        (scancode license updates, other license updates)
    Each list item is a three-tuple of:
        (attribute name, value before, value after)

    If `from_spdx` is True, this means that the SPDX keys where used for
    matching. In this case, the key that is used is that from the ScanCode
    license.
    """
    if TRACE:
        print('merge_licenses:', scancode_license, external_license)

    updated_scancode_attributes = []

    def update_scancode(_attrib, _sc_val, _ext_val):
        setattr(scancode_license, _attrib, _ext_val)
        updated_scancode_attributes.append((_attrib, _sc_val, _ext_val))

    updated_external_attributes = []

    def update_external(_attrib, _sc_val, _ext_val):
        setattr(external_license, _attrib, _sc_val)
        updated_external_attributes.append((_attrib, _ext_val, _sc_val))

    if from_spdx:
        scancode_key = scancode_license.spdx_license_key
        external_key = external_license.spdx_license_key
        if scancode_key != external_key:
            raise Exception(
                f'Non mergeable licenses with different SPDX keys: scancode_license.spdx_license_key {scancode_key} <>  external_license.spdx_license_key {external_key}'
            )
    else:
        scancode_key = scancode_license.key
        external_key = external_license.key
        if scancode_key != external_key:
            raise Exception('Non mergeable licenses with different keys: %(scancode_key)s <> %(external_key)s' % locals())

#         if scancode_license.spdx_license_key != external_license.spdx_license_key:
#             pass
#         else:
#             if TRACE:
#                 print('Merging licenses with different keys, but same SPDX key: %(scancode_key)s <> %(external_key)s' % locals())
#             update_external('key', scancode_key, external_key)

    for attrib in updatable_attributes:
        scancode_value = getattr(scancode_license, attrib)
        external_value = getattr(external_license, attrib)

        # for boolean flags, the other license wins. But only for True.
        # all our flags are False by default
        if isinstance(scancode_value, bool) and isinstance(external_value, bool):
            if scancode_value is False and scancode_value != external_value:
                update_scancode(attrib, scancode_value, external_value)
            continue

        if isinstance(scancode_value, (list, tuple)) and isinstance(external_value, (list, tuple)):
            normalized_scancode_value = set(s for s in scancode_value if s and s.strip())
            normalize_external_value = set(s for s in external_value if s and s.strip())

            # special case for URL lists, we consider all URL fields to
            # update
            if attrib.endswith('_urls',):
                all_sc_urls = set(
                    list(normalized_scancode_value) +
                    scancode_license.text_urls +
                    scancode_license.other_urls +
                    [scancode_license.homepage_url,
                     scancode_license.osi_url,
                     scancode_license.faq_url
                    ]
                )
                all_sc_urls = set(u for u in all_sc_urls if u)
                new_other_urls = normalize_external_value.difference(all_sc_urls)
                # add other urls to ScanCode
                combined = normalized_scancode_value | new_other_urls
                if set(normalized_scancode_value) != combined:
                    update_scancode(attrib, scancode_value, sorted(combined))

                # FIXME: FOR NOW WE DO NOT UPDATE THE OTHER SIDE with ScanCode URLs

            else:
                # merge ScanCode and other value lists
                combined = normalized_scancode_value | normalize_external_value
                if combined == normalized_scancode_value:
                    pass
                else:
                    update_scancode(attrib, scancode_value, sorted(combined))
                # FIXME: FOR NOW WE DO NOT UPDATE THE OTHER SIDE with ScanCode seqs

            continue

        if (isinstance(scancode_value, str) and isinstance(external_value, str)):
            # keep the stripped and normalized spaces value
            # normalized spaces
            normalized_scancode_value = ' '.join(scancode_value.split())
            normalize_external_value = ' '.join(external_value.split())

            # Fix up values with normalized values
            if scancode_value != normalized_scancode_value:
                scancode_value = normalized_scancode_value
                update_scancode(attrib, scancode_value, normalized_scancode_value)

            if external_value != normalize_external_value:
                external_value = normalize_external_value
                update_external(attrib, external_value, normalize_external_value)

        scancode_equals_external = scancode_value == external_value
        if scancode_equals_external:
            continue

        external_is_empty = scancode_value and not external_value
        if external_is_empty:
            update_external(attrib, scancode_value, external_value)
            continue

        scancode_is_empty = not scancode_value and external_value
        if scancode_is_empty:
            update_scancode(attrib, scancode_value, external_value)
            continue

        # on difference, the other license wins
        if scancode_value != external_value:
            update_scancode(attrib, scancode_value, external_value)
            continue

    return updated_scancode_attributes, updated_external_attributes


def synchronize_licenses(scancode_licenses, external_source, use_spdx_key=False,
                         match_text=False, match_approx=False, commitish=None):
    """
    Update the `scancode_licenses` ScanCodeLicenses licenses and texts in-place
    (e.g. in their current storage directory) from an `external_source`
    ExternalLicensesSource.

    Also update the external_source licenses this way:
    - original licenses from the external source are left unmodified in the original sub dir
    - new licenses found in scancode that are not in the external source are created in the new sub dir
    - external licenses that are modified from Scancode are created in the updated sub dir
    - external licenses that are not found in Scancode are created in the deleted sub dir

    The process is this:
    fetch external remote licenses
    build external license objects in memory, save in the original sub directory
    load scancode licenses

    for each scancode license:
        find a possible exact key match with an external license
        if there is a match, update and save the external license object in an "updated" directory
        if there is no match, save the external license object in a "new" directory

    for each external license:
        find a possible exact key or spdx key match with a scancode license
        if there is a match, update and save the scancode license object
        if there is no match, create and save a new scancode license object

    then later:
        find a possible license text match with a license

    """
    if TRACE: print('synchronize_licenses using SPDX keys:', use_spdx_key)

    # mappings of key -> License
    scancodes_by_key = scancode_licenses.by_key
    externals_by_key = external_source.get_licenses(scancode_licenses, commitish=commitish)

    if use_spdx_key:
        scancodes_by_key = scancode_licenses.by_spdx_key
        externals_by_key = get_licenses_by_spdx_key(externals_by_key.values())

    externals_by_spdx_key = get_licenses_by_spdx_key(externals_by_key.values())

    # track changes with sets of license keys
    same = set()
    added_to_scancode = set()
    added_to_external = set()
    updated_in_scancode = set()
    updated_in_external = set()

    unmatched_scancode_by_key = {}

    # FIXME: track deprecated
    # removed = set()

    # 1. iterate scancode licenses and compare with other
    for matching_key, scancode_license in scancodes_by_key.items():

        if not TRACE:print('.', end='')

        # does this scancode license exists in others based on the matching key?
        external_license = externals_by_key.get(matching_key)
        if not external_license:
            if TRACE_DEEP: print('ScanCode license not in External:', matching_key)
            unmatched_scancode_by_key[scancode_license.key] = scancode_license
            continue

        # the matching key exists on both sides: merge/update both licenses
        scancode_updated, external_updated = merge_licenses(
            scancode_license, external_license,
            external_source.updatable_attributes,
            from_spdx=use_spdx_key)

        if not scancode_updated and not external_updated:
            if TRACE_DEEP: print('License attributes are identical:', matching_key)
            same.add(matching_key)

        if scancode_updated:
            if TRACE: print('ScanCode license updated: SPDX:', use_spdx_key, matching_key, end='. Attributes: ')
            for attrib, oldv, newv in scancode_updated:
                if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
            updated_in_scancode.add(matching_key)

        if external_updated:
            if TRACE: print('External license updated: SPDX:', use_spdx_key, matching_key, end='. Attributes: ')
            for attrib, oldv, newv in external_updated:
                if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
            updated_in_external.add(matching_key)

    """
        if not external_license:
            matched_key = get_key_through_text_match(
                matching_key, scancode_license.text,
                scancode_licenses,
                match_approx=True)
            if matched_key:
                print('\nScanCode license not in External:', matching_key, 'but matched to:', matched_key)
                external_license
            else:
                print('\nScanCode license not in External:', matching_key, ' and added to external')
                external_license = scancode_license.relocate(external_source.new_dir)
                added_to_external.add(matching_key)
                externals_by_key[matching_key] = external_license
                continue
"""
    # 2. iterate other licenses and compare with ScanCode
    if TRACE: print()
    for matching_key, external_license in externals_by_key.items():
        # does this key exists in scancode?
        scancode_license = scancodes_by_key.get(matching_key)
        if scancode_license:
            # we already dealt with this in the first loop
            continue

        if not TRACE: print('.', end='')

        if match_text:

            matched_key = get_key_through_text_match(
                matching_key, external_license.text,
                scancode_licenses,
                match_approx=match_approx)
            if TRACE:
                print('External license with different key:', matching_key, 'and text matched to ScanCode key:', matched_key)

            if matched_key:
                print('\nExternal license with different key and matched text to ScanCode:', matching_key, ' matched to:', matched_key)
                if matched_key in unmatched_scancode_by_key:
                    del unmatched_scancode_by_key[matched_key]

                scancode_license = scancodes_by_key.get(matched_key)

                scancode_updated, external_updated = merge_licenses(
                    scancode_license, external_license,
                    external_source.updatable_attributes,
                    from_spdx=use_spdx_key)

                if not scancode_updated and not external_updated:
                    if TRACE_DEEP: print('License attributes are identical:', matching_key)
                    same.add(matching_key)

                if scancode_updated:
                    if TRACE: print('ScanCode license updated: SPDX:', use_spdx_key, matching_key, end='. Attributes: ')
                    for attrib, oldv, newv in scancode_updated:
                        if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
                    updated_in_scancode.add(matching_key)

                if external_updated:
                    if TRACE: print('External license updated: SPDX:', use_spdx_key, matching_key, end='. Attributes: ')
                    for attrib, oldv, newv in external_updated:
                        if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
                    updated_in_external.add(matching_key)

        else:
            # Create a new ScanCode license
            scancode_license = external_license.relocate(licensedcode.models.licenses_data_dir, matching_key)
            added_to_scancode.add(matching_key)
            scancodes_by_key[matching_key] = scancode_license
            if TRACE: print('External license key not in ScanCode:', matching_key, 'created in ScanCode.', 'SPDX:', use_spdx_key)

    # 3. For scancode licenses that were not matched to anything in external add them in external
    if TRACE:
        print()
        print('Processing unmatched_scancode_by_key.')
    for lkey, scancode_license in unmatched_scancode_by_key.items():
        if lkey in set(['here-proprietary']):
            continue
        if scancode_license.is_deprecated:
            continue
        external_license = scancode_license.relocate(external_source.new_dir)
        added_to_external.add(lkey)
        externals_by_key[lkey] = external_license
        if TRACE: print('ScanCode license key not in External:', lkey, 'created in External.')

    # finally write changes in place for updates and news
    for k in updated_in_scancode | added_to_scancode:
        scancodes_by_key[k].dump()

    for k in updated_in_external | added_to_external:
        externals_by_key[k].dump()

# TODO: at last: print report of incorrect OTHER licenses to submit
# updates eg. make API calls to DejaCode to create or update
# licenses and submit review request e.g. submit requests to SPDX
# for addition
    for key in sorted(added_to_external):
        lic = externals_by_key[key]
        if not lic.owner:
            print('New external license without owner:', key)

    print()
    print('#####################################################')
    print('Same licenses:       ', len(same))
    print('Add to ScanCode:     ', len(added_to_scancode))
    print('Updated in ScanCode: ', len(updated_in_scancode))
    print('Added to External::  ', len(added_to_external))
    print('Updated in External: ', len(updated_in_external))
    print('#####################################################')

    return [externals_by_key[k] for k in added_to_external]


@click.command()
@click.argument('license_dir', type=click.Path(), metavar='DIR')
@click.option('-s', '--source', type=click.Choice(EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES), help='Select an external license source.')
@click.option('-m', '--match-text', is_flag=True, default=False, help='Match external license texts with license detection to find a matching ScanCode license.')
@click.option('-a', '--match-approx', is_flag=True, default=False, help='Include approximate license detection matches when matching ScanCode license.')
@click.option('-t', '--trace', is_flag=True, default=False, help='Print execution trace.')
@click.option('--create-ext', is_flag=True, default=False, help='Create new external licenses in the external source if possible.')
@click.option('--commitish', type=str, default=None, help='An optional commitish to use for SPDX license data instead of the latest release.')
@click.help_option('-h', '--help')
def cli(license_dir, source, match_text, match_approx, trace, create_ext, commitish=None):
    """
    Synchronize ScanCode licenses with an external license source.

    DIR is the directory to store fetched external licenses (or where to load from already fetched licenses).
    Side-by-side with "DIR", three directories are created with new, updated or deleted licenses (with regards to ScanCode licenses)
    The ScanCode licenses are collected from the current installation.

    When using the dejacode source your need to set the 'DEJACODE_API_URL' and
    'DEJACODE_API_KEY' environment variables with your credentials.
    """
    global TRACE
    TRACE = trace

    licenses_source_class = EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES[source]
    external_source = licenses_source_class(license_dir)
    scancode_licenses = ScanCodeLicenses()

    use_spdx_key = source == 'spdx'
    added_to_external = synchronize_licenses(
        scancode_licenses, external_source,
        use_spdx_key=use_spdx_key,
        match_text=match_text,
        match_approx=match_approx,
        commitish=commitish,
    )
    print()
    if create_ext and isinstance(external_source, DejaSource):
        api_url = external_source.api_base_url
        api_key = external_source.api_key
        for elic in added_to_external:
            create_license(api_url, api_key, elic)


if __name__ == '__main__':
    cli()
