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
import os

import requests

from commoncode.fileutils import get_temp_dir
from commoncode.fileutils import system_temp_dir
from commoncode.fileutils import copytree

from licensedcode.models import load_licenses
from licensedcode.query import Query
from licensedcode.index import get_index
from licensedcode.match_hash import tokens_hash
from licensedcode import licenses_data_dir

from scancode import api

"""
Script to sync and update the ScanCode licenses ways against:
 - the SPDX license list
 - the DejaCode licenses
"""

TRACE = True


class ExternalLicenseBuilder(object):
    """
    Base class to fetch licenses from an external source and provide
    Scancode licensedcode.models.License objects
    """
    def __init__(self, src_dir):
        """
        `src_dir` is where the SacnCode License objects are dumped.
        """
        src_dir = os.path.realpath(src_dir)
        self.src_dir = src_dir

        self.fetched = False
        if os.listdir(src_dir):
            # fetch ONLY if the directory is empty
            self.fetched = True

    def get_licenses(self):
        """
        Yield License object from the latest SPDX license list.
        Store the texts in the license_dir.
        """
        raise NotImplementedError

    def licenses(self):
        """
        Return a mapping of key -> ScanCode License objects either
        fetched externally or loaded from the existing `self.src_dir`
        """
        if self.fetched:
            print('Reusing external licenses stored in:', src_dir)
            return load_licenses(self.src_dir, with_deprecated=True)
        else:
            print('Fetching and storing external licenses in:', src_dir)
            licenses = {l.key: l for l in self.get_licenses()}
            print('Stored %d external licenses in: %r.' % (len(licenses), src_dir,))
            return licenses

    def save_license(key, mapping, text):
        """
        Save and return a ScanCode License constructed from a mapping.
        Save the license and its text in the `self.src_dir`.
        """
        from licensedcode.models import License
        lic = License(key=key, src_dir=self.src_dir)
        for name, value in mapping.items():
            setattr(lic, name, value)

        with codecs.open(lic.text_file, 'wb', encoding='utf-8')as tf:
            tf.write(text)
        lic.dump()
        return lic

    def backup():
        """
        Make a copy of src_dir to a `src_dir`-backup directory after
        initial creation of Licenses in src_dir. This is used to find
        which changes where made to the other licenses.
        """

        backup_dir = self.src_dir.rstrip('\\/') + '-backup'
        if not os.path.exists(backup_dir):
            copytree(sefl.src_dir, backup_dir)



class SpdxLicenseBuilder(ExternalLicenseBuilder):

    def get_licenses(self):
        """
        Yield all the latest License object from the latest SPDX license list.
        Store the texts in the license_dir.
        """
        tags_url = 'https://api.github.com/repos/spdx/license-list-data/tags'
        tags = get_response(tags_url, headers={}, params={})
        # get latest tag
        version = tags[0]['name']

        # fetch licenses and exceptions

        lics_url = 'https://raw.githubusercontent.com/spdx/license-list-data/%(version)s/json/licenses.json' % locals()
        # fetch details at https://raw.githubusercontent.com/spdx/license-list-data/v2.6/json/details/0BSD.json

        for lic in get_response(lics_url, headers={}, params={})['licenses']:
            key = license_mapping.get('licenseId')
            details_url = 'https://raw.githubusercontent.com/spdx/license-list-data/%(version)s/json/details/%(key)s.json' % locals()
            details = get_response(details_url_url, headers={}, params={})
            yield self._build_license(details)

        # exceptions data have -- weirdly enough -- a different schema
        # and urls templates
        excs_url = 'https://raw.githubusercontent.com/spdx/license-list-data/%(version)s/json/exceptions.json' % locals()
        for excp in get_response(excs_url, headers={}, params={})['exceptions']:
            key = license_mapping.get('licenseExceptionId')
            details_url = 'https://raw.githubusercontent.com/spdx/license-list-data/%(version)s/json/exceptions/%(key)s.json' % locals()
            details = get_response(details_url_url, headers={}, params={})
            yield self._build_license(details)

    def _build_license(self, mapping):
        """
        Return a ScanCode License object built from an SPDX license
        mapping.
        """
        spdx_license_key = mapping.get('licenseId') or mapping.get('licenseExceptionId')
        assert spdx_license_key
        key = spdx_license_key
        src_dir = self.storage_directory

        other_urls = mapping.get('seeAlso', [])
        other_urls.append('https://spdx.org/licenses/%(spdx_license_key)s.html' % locals())

        lic = dict(
            spdx_license_key=spdx_license_key,
            name=mapping['name'],
            is_deprecated=mapping.get('isDeprecatedLicenseId', False),
            is_exception=bool(mapping.get('licenseExceptionId')),
            # FIXME: we may not want to carry notes over???
            notes=mapping.get('licenseComments'),
            other_urls=other_urls,

            # Not yet available in ScanCode
            # TODO: detect licenses on these texts to ensure they match?
            # TODO: add rule? and test license detection???
            # lic.standard_template = mapping('standardLicenseTemplate')
            # lic.notice = mapping.get('standardLicenseHeader')
            # exception_example
            # lic.example = mapping.get('example')
            # lic.osi_approved = mapping.get('isOsiApproved', False)
        )
        return self.save_license(key, lic, text)


class DejaLicenseBuilder(ExternalLicenseBuilder):

    def __init__(self, src_dir, api_base_url=None, api_key=None):
        super(DejaLicenseBuilder, self).__init__(src_dir)
        self.api_base_url = api_base_url or os.environ.get('DEJACODE_API_URL', None)
        self.api_key = api_key or os.environ.get('DEJACODE_API_KEY', None)

        assert api_key and api_base_url, (
            'You must set the DEJACODE_API_URL and DEJACODE_API_URL '
            'environment variables before running this script.')

    def get_licenses():
        api_url = '/'.join([self.api_base_url.rstrip('/'), 'licenses/'])
        for license in call_deja_api(api_url, self.api_key, paginate=100):
            yield self._build_license(lic)

    def _build_license(self, mapping):
        """
        Return a ScanCode License object built from a DejaCode license mapping.
        """
        key = mapping['key']
        src_dir = self.src_dir
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

            is_deprecated=not mapping.get('is_active'),
            standard_notice=mapping['standard_notice'],

            # TODO: Not yet available in ScanCode
            # is_composite = mapping['is_component_license']
        )
        text = mapping['full_text']
        return self.save_license(key, lic, text)


def call_deja_api(api_url, api_key, paginate=0, headers=None, params=None):
    """
    Yield JSON results from the reponses of calling the API at `api_url`
    with `api_key` . Raise an exception on failure.

    Pass `headers` and `params` mappings to the underlying request if
    provided. If `paginate` is a non-zero attempt to paginate with
    `paginate` number of pages and return all the results.
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
            if first:
                first = False
            response = get_response(api_url, headers, params)
            yield response.get('results', [])

            api_url = response.get('next')
            if not api_url:
                break
    else:
        response = get_response(api_url, headers, params)
        yield response.get('results', [])


#######################
# Common code, not specific to a license origin

def merge_license_attribs(scancode_license, other_license):
    """
    Compare and update two License objects, in-place.
    Return a two-tuple of lists as:
        (scancode license updates, other license updates)
    Each list item is a three-tuple of:
        (attribute name, value before, value after)
    """
    # FIXME: there are cases where we want to do this? such as a creation???
    skey = scancode_license.key
    okey = other_license.key
    if skey != okey:
        raise Exception(
            'Non mergeable licenses with different keys: %(skey)s <> %(okey)s' % locals())

    attributes = (
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
        'standard_notice',
        'notes',
        # Not yet available in ScanCode
        # 'is_composite',
    )

    scancode_updated = []
    def sc_update(_attrib, _sc_val, _o_val):
        setattr(scancode_license, _attrib, _o_val)
        scancode_updated.append((_attrib, _sc_val, _o_val))

    other_updated = []
    def o_update(_attrib, _sc_val, _o_val):
        setattr(other_license, _attrib, _sc_val)
        other_updated.append((_attrib, _o_val, _sc_val))

    for attrib in attributes:
        sc_val = getattr(scancode_license, attrib)
        o_val = getattr(other_license, attrib)

        # for boolean flags, the other license wins
        if isinstance(sc_val, bool) and isinstance(o_val, bool):
            if sc_val != o_val:
                sc_update(attrib, sc_val, o_val)
            continue

        if isinstance(sc_val, (list, tuple)) and isinstance(o_val, (list, tuple)):
            norm_sc_val = sorted(s for s in sc_val if s and s.strip())
            norm_o_val = sorted(s for s in o_val if s and s.strip())
            # merge ScanCode and other value lists
            combined = sorted(set(norm_sc_val + norm_o_val))
            if norm_sc_val != combined:
                sc_update(attrib, sc_val, combined)
            if norm_o_val != combined:
                o_update(attrib, o_val, combined)
            continue

        if isinstance(sc_val, basestring) and isinstance(o_val, basestring):
            # keep the stripped and normalized spaces value
            # normalized spaces
            norm_sc_val = ' '.join(sc_val.split())
            norm_o_val = ' '.join(o_val.split())

            # Fix up values with normalized values
            if sc_val != norm_sc_val:
                sc_val = norm_sc_val
                sc_update(attrib, sc_val, nor_sc_val)

            if o_val != norm_o_val:
                o_val = norm_o_val
                o_update(attrib, o_val, norm_o_val)

        scancode_equals_other = sc_val == o_val
        if scancode_equals_other:
            continue

        other_is_empty = sc_val and not o_val
        if other_is_empty:
            o_update(attrib, sc_val, o_val)
            continue

        scancode_is_empty = not sc_val and o_val
        if scancode_is_empty:
            sc_update(attrib, sc_val, o_val)
            continue

        # on difference, the other license wins
        if sc_val != o_val:
            sc_update(attrib, sc_val, o_val)
            continue

    return scancode_updated, other_updated


def update_licenses(other_dir, license_builder=DejaLicenseBuilder):
    """
    Update the ScanCode licenses data and texts in-place (e.g. in their
    current storage directory) from external license data and texts.

    The process is to:
    1. Fetch external license using the `license_builder` object and
    store these in `other_dir` (using the ScanCode License
    storage format)
    2. Compare and update ScanCode licenses with these external licenses.
    """
    other_dir = fetch_dejacode_licenses(other_dir)

    # mappings of key -> License
    other_licenses = load_licenses(other_dir, with_deprecated=True)
    scancode_licenses = load_licenses(with_deprecated=True)

    # build additional lookup mappings
    other_by_spdx = {l.spdx_license_key: l for l in other_licenses.values() if l.spdx_license_key}
    scancode_by_spdx = {l.spdx_license_key: l for l in scancode_licenses.values() if l.spdx_license_key}

    # TODO:
    # by license short name
    # by license name

    # track changes, the reference is the ScanCode dataset
    same = set()
    added_scancode = set()
    added_other = set()
    changed_scancode = set()
    changed_other = set()
    # FIXME: track deprecated
    # removed = set()

    for sc_key, scancode_license in scancode_licenses.items():
        print('.')
        # does this key exists elsewhere?
        other_license = other_licenses.get(sc_key)

        if other_license:
            if TRACE: print('License key exists both sides:', sc_key)
            scancode_updated, other_updated = merge_license_attribs(scancode_license, other_license)

            if not scancode_updated and not other_updated:
                if TRACE: print('Licenses attributes are identical:', sc_key)
                same.add(sc_key)

            if scancode_updated:
                if TRACE: print('ScanCode license updated:', sc_key)
                for attrib, oldv, newv in scancode_updated:
                    if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
                scancode_license.dump()
                changed_scancode.add(sc_key)

            if other_updated:
                if TRACE: print('Other license updated:', sc_key)
                for attrib, oldv, newv in other_updated:
                    if TRACE: print('  %(attrib)s: %(oldv)r -> %(newv)r' % locals())
                other_license.dump()
                changed_other.add(sc_key)

        else:
            if TRACE: print('ScanCode license key not in Other:', sc_key)
            # compare license attributes and texts to determine if this is a new new or existing license

            # and Create a new DejaCode license
            other_license = scancode_license.relocate(other_dir)
            added_other.add(other_license.key)
            other_licenses[other_license.key] = other_license
            if TRACE: print('  Created other:', other_license)

    for o_key, other_license in scancode_licenses.items():
        # does this key exists in scancode?
        scancode_license = scancode_licenses.get(o_key)
        if other_license:
            # we alreday dealt with this in the previous loop
            continue

        print('.')
        if TRACE: print('Other license key not in ScanCode:', o_key)
        # compare license attributes and texts to determine if this is a new new or existing license
        # and create ScanCode licens`e
        is_exact, key = is_exact_match(other_license)
        if is_exact:
            if TRACE: print('Other license key:', other_license.key, 'matched exactly to different ScanCode key:', key)
        else:
            # TODO: check for close matches

            # Create a new ScanCode license
            scancode_license = other_license.relocate(licenses_data_dir)
            added_scancode.add(scancode_license.key)
            scancode_licenses[scancode_license.key] = scancode_license
            if TRACE: print('  Created ScanCode:', scancode_license)


    # finally write changes
    for k in changed_scancode | added_scancode:
        scancode_licenses[k].dump()

    for k in changed_other | added_other:
        other_licenses[k].dump()

    # TODO: at last: print report of incorrect OTHER licenses to submit updates
    # eg. make API calls to DejaCode to create or update licenses and submit review request


def get_hash_and_length(other_license):
    """
    Return details from a License object texts.
    """
    idx = get_index()
    qry = Query(other_license.text_file, idx=idx)
    query_hash = tokens_hash(qry.whole_query_run().tokens)
    length = len(qry.whole_query_run().tokens)
    return query_hash, length


def license_matches(text):
    """
    Return a sequence of license match mappings with texts and
    diagnostics by scanning `text` with the current ScanCode license
    index.
    """
    if TRACE: print('Matching text')
    return list(api.get_licenses(other_license.text_file, include_text=True, diag=True))


def is_exact_match(other_license):
    """
    Return licenses maches with texts and diagnostics by detecting the text of other_license with the current ScanCode licenses.
    """
    matches = license_matches(other_license)
    _other_hash, other_len = get_hash_and_length(other_license)
    is_exact_license_match = False

    key = None
    if matches and len(matches) == 1:
        match = matches[0]
        rule = match.matched_rule
        is_exact_license_match = (
            rule.is_license
            and len(rule.licenses) == 1
            and rule.matcher == '1-hash'
            and match.qlen == other_len
        )
        if is_exact_license_match:
            key = rule.licenses[0]

    return is_exact_license_match, key


def get_response(api_url, headers, params):
    """
    Return a native Python object of the JSON response from calling
    `api_url` with `headers` and `params`.
    """

    if TRACE: print('Calling API: %(api_url)s' % locals())
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code != requests.codes.ok:
        raise Exception('Failed API call HTTP request: {}'.format(response.status_code))
    return response.json(object_pairs_hook=OrderedDict)



if __name__ == '__main__':
    import sys
    dejacode_license_dir = None
    args = sys.argv[1:]
    dejacode_license_dir = args[0]
    assert os.path.exists(dejacode_license_dir)
    update_licenses(dejacode_license_dir)
