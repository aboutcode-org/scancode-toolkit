# -*- coding: utf-8 -*-
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
from __future__ import print_function

import codecs
from collections import OrderedDict
import json
import os
import zipfile

import click
click.disable_unicode_literals_warning = True
import requests

from commoncode import fileutils
from commoncode import fetch

import licensedcode
from licensedcode.cache import get_licenses_db
from licensedcode.cache import get_index
from licensedcode.models import load_licenses
from licensedcode.models import License


"""
Sync and update the ScanCode licenses against:
 - the SPDX license list
 - the DejaCode licenses

Run python synclic.py -h for help.
"""

TRACE = False
TRACE_DEEP = False
TRACE_FETCH = False

class ExternalLicensesSource(object):
    """
    Base class to provide (including possibly fetch) licenses from an
    external source and expose these as licensedcode.models.License
    objects
    """
    # `matching_key` is the License object attribute to use as a key: one
    # of "key" or "spdx_license_key".
    matching_key = None

    # tuple of ScanCode reference license attributes that can be updated
    # from this source
    updatable_attributes = tuple()
    # tuple of ScanCode reference license attributes that cannot be updated
    # from this source. They can only be set when creating a new license.
    non_updatable_attributes = tuple()

    def __init__(self, src_dir):
        """
        `src_dir` is where the License objects are dumped.
        """
        src_dir = os.path.realpath(src_dir)
        self.src_dir = src_dir

        self.fetched = False
        if os.path.exists(src_dir):
            # fetch ONLY if the directory is empty
            self.fetched = True
        else:
            os.mkdir(src_dir)

        self.scancodes_by_key = get_licenses_db()

        self.scancodes_by_spdx_key = {l.spdx_license_key.lower(): l
            for l in self.scancodes_by_key.values()
            if l.spdx_license_key}

        composites_dir = os.path.join(licensedcode.data_dir, 'composites', 'licenses')
        self.composites_by_key = load_licenses(composites_dir, with_deprecated=True)
        self.composites_by_spdx_key = {l.spdx_license_key.lower(): l
            for l in self.composites_by_key.values()
            if l.spdx_license_key}

        foreign_dir = os.path.join(licensedcode.data_dir, 'non-english', 'licenses')
        self.non_english_by_key = load_licenses(foreign_dir, with_deprecated=True)
        self.non_english_by_spdx_key = {l.spdx_license_key.lower(): l
            for l in self.non_english_by_key.values()
            if l.spdx_license_key}

    def fetch_licenses(self, approx=False):
        """
        Yield License objects fetched from this external source.
        Store the metadata and texts in self.src_dir as a side effect.
        """
        raise NotImplementedError

    def get_licenses(self, approx=False):
        """
        Return a mapping of key -> ScanCode License objects either
        fetched externally or loaded from the existing `self.src_dir`
        """
        if self.fetched:
            print('Reusing external licenses stored in:', self.src_dir)
            return load_licenses(self.src_dir, with_deprecated=True)
        else:
            print('Fetching and storing external licenses in:', self.src_dir)
            licenses = {l.key: l for l in self.fetch_licenses(approx=approx)}
            print('Stored %d external licenses in: %r.' % (len(licenses), self.src_dir,))
            self.backup()
            return licenses

    def find_key(self, key, text, include_approx_matches=True):
        """
        Return a ScanCode license key string or None given an existing key and a license text.
        """

        keyl = key.lower()
        if self.matching_key == 'key':
            if keyl in self.scancodes_by_key:
                if TRACE_DEEP: print('Other license key in ScanCode:', key, end='. ')
                return keyl

        if keyl in self.scancodes_by_spdx_key:
            sckey = self.scancodes_by_spdx_key[keyl].key
            if TRACE_DEEP: print('Other license key in ScanCode as:', sckey, 'for SPDX:', key, end='. ')
            return sckey

        if TRACE_DEEP: print('Matching text for:', key, end='. ')
        new_key, exact, score = get_match(text)
        if not new_key:
            if TRACE_DEEP: print('SKIPPED: Other license key not MATCHED in ScanCode:', key, end='. ')
            return None
        if exact is True:
            if TRACE_DEEP: print('Other license key not in ScanCode: EXACT match to:', new_key, end='. ')
            return new_key

        if include_approx_matches:
            if exact is False:
                if TRACE_DEEP: print('Other license key not in ScanCode but OK matched to:', new_key, 'with score:', score, end='. ')
                return new_key

            if exact is None:
                if TRACE_DEEP: print('Other license key not in ScanCode: WEAK matched to:', new_key, 'with score:', score, end='. ')
                return new_key

            if exact == -1:
                if TRACE_DEEP: print('Other license key not in ScanCode: JUNK MATCH to:', new_key, 'with score:', score, end='. ')
                return new_key
        else:
            if TRACE_DEEP: print('SKIPPED: Other license key weakly matched in ScanCode: JUNK MATCH to:', new_key, 'with score:', score, end='. ')

    def save_license(self, key, mapping, text, include_approx_matches=False):
        """
        Return a ScanCode License for `key` constructed from a `mapping`
        of attributes and a license `text`. Save the license metadata
        and its text in the `self.src_dir`.
        """
        new_key = None
        if self.matching_key == 'key':
            new_key = self.find_key(key, text, include_approx_matches)
        elif self.matching_key == 'spdx_license_key':
            new_key = self.find_key(mapping['spdx_license_key'], text)

        if not new_key:
            key = key.lower()
            if TRACE: print('  No Scancode key found. USING key as:', key)
        else:
            if key == new_key:
                if TRACE: print('  Scancode key found:', key)
            else:
                if TRACE: print('  Scancode key found:', new_key, 'CHANGED from:', key)
                key = new_key

        lic = License(key=key, src_dir=self.src_dir)
        for name, value in mapping.items():
            setattr(lic, name, value)

        with codecs.open(lic.text_file, 'wb', encoding='utf-8')as tf:
            tf.write(text)
        lic.dump()
        return lic

    def backup(self):
        """
        Make a copy of src_dir to a `src_dir`-backup directory after the
        initial creation of Licenses in src_dir. This is used to find
        which changes where made to the other licenses.
        """

        backup_dir = self.src_dir.rstrip('\\/') + '-backup'
        if not os.path.exists(backup_dir):
            fileutils.copytree(self.src_dir, backup_dir)
        print('Original external licenses backup available in: %r.' % backup_dir)


def get_response(url, headers, params):
    """
    Return a native Python object of the JSON response from calling
    `url` with `headers` and `params`.
    """

    if TRACE_FETCH: print('==> Fetching URL: %(url)s' % locals())
    response = requests.get(url, headers=headers, params=params)
    status = response.status_code
    if status != requests.codes.ok:  # @UndefinedVariable
        raise Exception('Failed HTTP request for %(url)r: %(status)r' % locals())
    return response.json(object_pairs_hook=OrderedDict)


def get_match(text):
    """
    Return a tuple of:
    (top matched license key or None,
      (True if this an exact match, False if the match is ok, None if the match is weak,
    the matched score).
    """
    idx = get_index()
    matches = list(idx.match(query_string=text, min_score=80))

    if not matches:
        return None, None, 0

    match = matches[0]
    query = match.query
    query_len = len(query.whole_query_run().tokens)
    rule = match.rule
    key = rule.licenses[0]

    is_exact = (
        rule.is_license and len(rule.licenses) == 1
        and match.matcher == '1-hash'
        and match.score() == 100
        and match.qlen == query_len
        )
    if is_exact:
        return key, True, 100

    is_ok = (
        len(rule.licenses) == 1
        and match.coverage() > 95
        and match.score() > 95)
    if is_ok:
        return key, False, match.score()

    is_weak = (
        len(rule.licenses) == 1
        and match.coverage() > 90
        and match.score() > 90)
    if is_weak:
        return key, None, match.score()

    if match.score() > 85:
        # junk match
        return key, -1, match.score()
    else:
        return None, None, None

# map to a number of start lines to strip from the lciense text
# to remove junk copyrights
STRIP_LINES_FROM = {
    'BSD-3-Clause-No-Nuclear-Warranty': 1,
    }

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
        # NOT YET: 'standard_notice',
    )
    non_updatable_attributes = (
        'short_name',
        'name',
        'notes',
    )

    def fetch_licenses(self, approx=False):
        """
        Yield all the latest License object from the latest SPDX license list.
        Store the texts in the license_dir.
        """
        # get latest tag
        tags_url = 'https://api.github.com/repos/spdx/license-list-data/tags'
        tags = get_response(tags_url, headers={}, params={})
        tag = tags[0]['name']

        # fetch licenses and exceptions
        # note that exceptions data have -- weirdly enough -- a different schema
        zip_url = 'https://github.com/spdx/license-list-data/archive/%(tag)s.zip' % locals()
        if TRACE_FETCH: print('Fetching SPDX license data from:', zip_url)
        licenses_zip = fetch.download_url(zip_url, timeout=120)
        with zipfile.ZipFile(licenses_zip) as archive:
            for path in archive.namelist():
                if not (path.endswith('.json')
                and ('/json/details/' in path or '/json/exceptions/' in path)):
                    continue
                if TRACE_FETCH: print('Loading license:', path)
                if path.endswith('+.json'):
                    # Skip the old plus licenses. We use them in
                    # ScanCode, but they are deprecated in SPDX.
                    continue
                details = json.loads(archive.read(path))
                try:
                    yield self._build_license(details, approx)
                except:
                    print(json.dumps(details, indent=2))
                    raise

    def _build_license(self, mapping, approx):
        """
        Return a ScanCode License object built from an SPDX license
        mapping.
        """
        spdx_license_key = mapping.get('licenseId') or mapping.get('licenseExceptionId')
        assert spdx_license_key
        spdx_license_key = spdx_license_key.strip()
        key = spdx_license_key.lower()

        deprecated = mapping.get('isDeprecatedLicenseId', False)
        if deprecated:
            # we use concrete keys for some plus/or later versions for
            # simplicity and override SPDX deprecation for these
            if key.endswith('+'):
                # 'gpl-1.0+', 'gpl-2.0+', 'gpl-3.0+',
                # 'lgpl-2.0+', 'lgpl-2.1+', 'lgpl-3.0+',
                # 'gfdl-1.1+', 'gfdl-1.2+', 'gfdl-1.3+'
                # 'agpl-3.0+'
                deprecated = False
            else:
                if key not in self.scancodes_by_spdx_key:
                    if TRACE: print('Skipping deprecated license not in ScanCode:', key)
                    return

        # TODO: Not yet available in ScanCode
        is_composite = key in self.composites_by_spdx_key
        if is_composite:
            # skip composite for now until they are properly handled in ScanCode
            if TRACE: print('Skipping composite license FOR NOW:', key)
            return

        # TODO: Not yet available in ScanCode
        is_foreign = key in self.non_english_by_spdx_key
        if is_foreign:
            if TRACE: print('Skipping NON-english license FOR NOW:', key)
            return

        other_urls = mapping.get('seeAlso', [])
        other_urls = (o for o in other_urls if o)
        other_urls = (o.strip() for o in other_urls)
        other_urls = (o for o in other_urls if o)
        # see https://github.com/spdx/license-list-data/issues/9
        junk_see_also = ('none', 'found')
        other_urls = (o for o in other_urls if o not in junk_see_also)

        other_urls = list(other_urls)

#         notes = mapping.get('licenseComments')
#         if notes and notes.strip():
#             notes = 'Per SPDX.org, ' + ' '.join(notes.split())

        standard_notice = mapping.get('standardLicenseHeader')
        if standard_notice:
            standard_notice = standard_notice.strip()
        lic = dict(
            spdx_license_key=spdx_license_key,
            name=mapping['name'].strip(),
            is_deprecated=deprecated,
            is_exception=bool(mapping.get('licenseExceptionId')),
            other_urls=other_urls,

            # TODO: the formatting might need to be preserved
            standard_notice=standard_notice,

            # FIXME: Do we really want to carry notes over???
            # notes=notes,

            # FIXME: available in ScanCode but as an OSI URL
            # we should check if we have the osi_url  when this flag is there
            # osi_url = mapping.get('isOsiApproved', False)

            # TODO: detect licenses on these texts to ensure they match?
            # TODO: add rule? and test license detection???
            # standard_template = mapping('standardLicenseTemplate')
            # exception_example
            # example = mapping.get('example')
        )
        text = mapping.get('licenseText') or mapping.get('licenseExceptionText')
        text = text.strip()
        return self.save_licenseey(key, lic, text, include_approx_matches=approx)


class DejaSource(ExternalLicensesSource):
    """
    License source for DejaCode licenses fetched through its API.
    """
    matching_key = 'key'

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
        # Not yet available in ScanCode
        # 'is_composite',
    )
    non_updatable_attributes = (
        'notes',
    )

    def __init__(self, src_dir, api_base_url=None, api_key=None):
        super(DejaSource, self).__init__(src_dir)

        self.api_base_url = api_base_url or os.environ.get('DEJACODE_API_URL', None)
        self.api_key = api_key or os.environ.get('DEJACODE_API_KEY', None)

        assert (self.api_key and self.api_base_url), (
            'You must set the DEJACODE_API_URL and DEJACODE_API_KEY ' +
            'environment variables before running this script.')

    def fetch_licenses(self, approx=False):
        api_url = '/'.join([self.api_base_url.rstrip('/'), 'licenses/'])
        for licenses in call_deja_api(api_url, self.api_key, paginate=100):
            for lic in licenses:
                dlic = self._build_license(lic, approx)
                if dlic:
                    yield dlic

    def _build_license(self, mapping, approx=False):
        """
        Return a ScanCode License object built from a DejaCode license
        mapping or None for skipped licenses.
        """
        key = mapping['key']

        # TODO: Not yet available in ScanCode
        is_composite = key in self.composites_by_key
        if is_composite:
            # skip composite for now until they are properly handled in ScanCode
            if TRACE: print('Skipping composite license FOR NOW:', key)
            return

        # TODO: Not yet available in ScanCode
        is_foreign = key in self.non_english_by_key
        if is_foreign:
            if TRACE: print('Skipping NON-english license FOR NOW:', key)
            return

        # these license are rare commercial license with no text and only a link
        # we ignore these
        dejacode_special_no_text = set([
            'alglib-commercial',
            'atlassian-customer-agreement',
            'dalton-maag-eula',
            'highsoft-standard-license-agreement-4.0',
            'monotype-tou',
            # junk duplicate of fsf-ap
            'laurikari',
            ])
        is_special = key in dejacode_special_no_text
        if is_special:
            # skip composite for now until they are properly handled in ScanCode
            if TRACE: print('Skipping special DejaCode license with NO TEXT FOR NOW:', key)
            return

        deprecated = not mapping.get('is_active')
        if deprecated and key not in self.scancodes_by_key:
            if TRACE: print('Skipping deprecated license not in ScanCode:', key)
            return

        lic = dict(
            short_name=mapping['short_name'],
            name=mapping['name'],
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
            standard_notice=mapping['standard_notice'],

        )
        text = mapping['full_text']
        return self.save_license(key, lic, text, include_approx_matches=approx)


def call_deja_api(api_url, api_key, paginate=0, headers=None, params=None):
    """
    Yield result mappings from the reponses of calling the API at
    `api_url` with `api_key` . Raise an exception on failure.

    Pass `headers` and `params` mappings to the underlying request if
    provided. If `paginate` is a non-zero attempt to paginate with
    `paginate` number of pages at a time and return all the results.
    """
    headers = headers or {
        'Authorization': 'Token {}'.format(api_key),
        'Accept': 'application/json; indent=2',
    }

    params = params or {}

    def _get_results(response):
        return response.json(object_pairs_hook=OrderedDict)

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


SOURCES = {
    'dejacode': DejaSource,
    'spdx': SpdxSource,
}


def merge_licenses(scancode_license, other_license, updatable_attributes):
    """
    Compare and update two License objects in-place given a sequence of
    `updatable_attributes`.
    Return a two-tuple of lists as:
        (scancode license updates, other license updates)
    Each list item is a three-tuple of:
        (attribute name, value before, value after)
    """
    scancode_updated = []
    def update_sc(_attrib, _sc_val, _o_val):
        setattr(scancode_license, _attrib, _o_val)
        scancode_updated.append((_attrib, _sc_val, _o_val))

    other_updated = []
    def update_ot(_attrib, _sc_val, _o_val):
        setattr(other_license, _attrib, _sc_val)
        other_updated.append((_attrib, _o_val, _sc_val))

    skey = scancode_license.key
    okey = other_license.key
    if skey != okey:
        raise Exception(
                'Non mergeable licenses with different keys: %(skey)s <> %(okey)s' % locals())
#         if scancode_license.spdx_license_key != other_license.spdx_license_key:
#             pass
#         else:
#             if TRACE:
#                 print('Merging licenses with different keys, but same SPDX key: %(skey)s <> %(okey)s' % locals())
#             update_ot('key', skey, okey)

    for attrib in updatable_attributes:
        sc_val = getattr(scancode_license, attrib)
        o_val = getattr(other_license, attrib)

        # for boolean flags, the other license wins. But only for True.
        # all our flags are False by default
        if isinstance(sc_val, bool) and isinstance(o_val, bool):
            if sc_val is False and sc_val != o_val:
                update_sc(attrib, sc_val, o_val)
            continue

        if isinstance(sc_val, (list, tuple)) and isinstance(o_val, (list, tuple)):
            norm_sc_val = set(s for s in sc_val if s and s.strip())
            norm_o_val = set(s for s in o_val if s and s.strip())

            # special case for URL lists, we consider all URL fields to
            # update
            if attrib.endswith('_urls',):
                all_sc_urls = set(list(norm_sc_val)
                    + scancode_license.text_urls
                    + scancode_license.other_urls
                    + [scancode_license.homepage_url,
                       scancode_license.osi_url,
                       scancode_license.faq_url])
                all_sc_urls = set(u for u in all_sc_urls if u)
                new_other_urls = norm_o_val.difference(all_sc_urls)
                # add other urls to ScanCode
                combined = norm_sc_val | new_other_urls
                if set(norm_sc_val) != combined:
                    update_sc(attrib, sc_val, sorted(combined))

                # FIXME: FOR NOW WE DO NOT UPDATE THE OTHER SIDE with ScanCode URLs

            else:
                # merge ScanCode and other value lists
                combined = norm_sc_val | norm_o_val
                if combined == norm_sc_val:
                    pass
                else:
                    update_sc(attrib, sc_val, sorted(combined))
                # FIXME: FOR NOW WE DO NOT UPDATE THE OTHER SIDE with ScanCode seqs

            continue

        if isinstance(sc_val, basestring) and isinstance(o_val, basestring):
            # keep the stripped and normalized spaces value
            # normalized spaces
            norm_sc_val = ' '.join(sc_val.split())
            norm_o_val = ' '.join(o_val.split())

            # Fix up values with normalized values
            if sc_val != norm_sc_val:
                sc_val = norm_sc_val
                update_sc(attrib, sc_val, norm_sc_val)

            if o_val != norm_o_val:
                o_val = norm_o_val
                update_ot(attrib, o_val, norm_o_val)

        scancode_equals_other = sc_val == o_val
        if scancode_equals_other:
            continue

        other_is_empty = sc_val and not o_val
        if other_is_empty:
            update_ot(attrib, sc_val, o_val)
            continue

        scancode_is_empty = not sc_val and o_val
        if scancode_is_empty:
            update_sc(attrib, sc_val, o_val)
            continue

        # on difference, the other license wins
        if sc_val != o_val:
            update_sc(attrib, sc_val, o_val)
            continue

    return scancode_updated, other_updated


def synchronize_licenses(external_source,
        create_external=False, update_only=False, approx=False):
    """
    Update the ScanCode licenses data and texts in-place (e.g. in their
    current storage directory) from an `external_source`
    ExternalLicensesSource.

    If `update_only_external` is True, only existing ScanCode licensses
    are updated. New licenses are NOT created.

    If `create_external` is True, also create external licenses from
    ScanCode licenses if they do not exists there.

    The process is to:
    1. Fetch external license using the `external_source` and store these.
    2. Compare and update ScanCode licenses with these external licenses.
    """

    # mappings of key -> License
    scancodes_by_key = external_source.scancodes_by_key
    others_by_key = external_source.get_licenses(approx=approx)

    # track changes with sets of license keys
    same = set()
    scancodes_added = set()
    others_added = set()
    scancodes_changed = set()
    others_changed = set()
    # FIXME: track deprecated
    # removed = set()

    # 1. iterate scancode licenses and compare with other
    for sc_key, sc_license in scancodes_by_key.items():

        if not TRACE:print('.', end='')

        # does this key exists elsewhere?
        ot_license = others_by_key.get(sc_key)
        if not ot_license:
            if create_external:
                if TRACE: print('ScanCode license key not in Other: created new other:', sc_key)
                ot_license = sc_license.relocate(external_source.src_dir)
                others_added.add(ot_license.key)
                others_by_key[ot_license.key] = ot_license
            continue

        # the key exist in scancode
        sc_updated, ot_updated = merge_licenses(
            sc_license, ot_license, external_source.updatable_attributes)

        if not sc_updated and not ot_updated:
            # if TRACE: print('Licenses attributes are identical:', sc_license.key)
            same.add(sc_license.key)

        if sc_updated:
            if TRACE: print('ScanCode license updated:', sc_license.key, end='. Attributes: ')
            for attrib, oldv, newv in sc_updated:
                if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
            scancodes_changed.add(sc_license.key)

        if ot_updated:
            if TRACE: print('Other license updated:', sc_license.key, end='. Attributes: ')
            for attrib, oldv, newv in ot_updated:
                if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
            others_changed.add(sc_license.key)

    # 2. iterate other licenses and compare with ScanCode
    for o_key, ot_license in others_by_key.items():
        # does this key exists in scancode?
        sc_license = scancodes_by_key.get(o_key)
        if sc_license:
            # we already dealt with this in the first loop
            continue

        if not TRACE:print('.', end='')

        if not update_only:
            # Create a new ScanCode license
            sc_license = ot_license.relocate(licensedcode.licenses_data_dir, o_key)
            scancodes_added.add(sc_license.key)
            scancodes_by_key[sc_license.key] = sc_license
            if TRACE: print('Other license key not in ScanCode:', ot_license.key, 'created in ScanCode.')

    # finally write changes
    for k in scancodes_changed | scancodes_added:
        scancodes_by_key[k].dump()

    if create_external:
        for k in others_changed | others_added:
            others_by_key[k].dump()

# TODO: at last: print report of incorrect OTHER licenses to submit
# updates eg. make API calls to DejaCode to create or update
# licenses and submit review request e.g. submit requests to SPDX
# for addition



@click.command()
@click.argument('license_dir', type=click.Path(), metavar='DIR')
@click.option('-s', '--source', type=click.Choice(SOURCES), help='Select an external license source.')
@click.option('-t', '--trace', is_flag=True, default=False, help='Print execution trace.')
@click.option('-u', '--update-only', is_flag=True, default=False, help='Only update ScanCode licenses. Do not create new licenses in ScanCode.')
@click.option('-x', '--create-external', is_flag=True, default=False, help='Also create new external licenses from ScanCode if needed.')
@click.option('-a', '--approx', is_flag=True, default=False, help='Include approximate license detection matches for finding a matching license.')
@click.option('-c', '--clean', is_flag=True, default=False, help='Clean DIR and backup DIR if they exist.')
@click.help_option('-h', '--help')
def cli(license_dir, source, trace, clean, update_only, create_external, approx):
    """
    Synchronize ScanCode licenses with an external license source.

    DIR is the directory to store (or load) external licenses.

    When using the dejacode source your need to set the
    'DEJACODE_API_URL' and 'DEJACODE_API_KEY' environment variables with
    your credentials.
    """
    global TRACE
    TRACE = trace

    if clean:
        fileutils.delete(license_dir)
        fileutils.delete(license_dir.rstrip('/\\') + '-backup')

    source = SOURCES[source]
    synchronize_licenses(source(license_dir), create_external=create_external, update_only=update_only, approx=approx)
    print()


if __name__ == '__main__':
    cli()
