# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
import textwrap
import time
import zipfile

from os import mkdir
from os.path import exists
from os.path import realpath
from pprint import pprint

import click
import requests

from commoncode import fetch
from commoncode import fileutils

import licensedcode
from licensedcode.cache import get_licenses_by_spdx_key
from licensedcode import models
from licensedcode.match import MATCH_HASH
from licensedcode.models import load_licenses
from licensedcode.models import License

"""
Sync and update the ScanCode licenses against:
 - the SPDX license list
 - the DejaCode licenses

Run python synclic.py -h for help.
"""

TRACE = False
TRACE_ADD = False
TRACE_DEEP = False

# may be useful to change for testing
SPDX_DEFAULT_REPO = "spdx/license-list-data"


class ScanCodeLicenses:
    """
    Licenses from the current ScanCode installation
    """

    def __init__(self):
        self.by_key = load_licenses(with_deprecated=True)
        self.by_spdx_key = get_licenses_by_spdx_key(self.by_key.values())

    def clean(self):
        """
        Redump licenses YAML re-applying pretty-printing.
        """
        for lic in self.by_key.values():
            updated = False
            if lic.standard_notice:
                updated = True
                lic.standard_notice = clean_text(lic.standard_notice)
            if lic.notes:
                updated = True
                lic.notes = clean_text(lic.notes)

            if updated:
                models.update_ignorables(lic, verbose=False)
                lic.dump(licenses_data_dir=licensedcode.models.licenses_data_dir)


class ExternalLicensesSource:
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

    def __init__(self, external_base_dir=None):
        """
        `external_base_dir` is the base directory where the License objects are
        dumped as a pair of .LICENSE/.yml files.
        """
        if external_base_dir:
            external_base_dir = realpath(external_base_dir)
            self.external_base_dir = external_base_dir

            # we use four sub-directories:
            # we store the original fetched licenses in this directory
            self.original_dir = os.path.join(external_base_dir, "original")
            # we store updated external licenses in this directory
            self.update_dir = os.path.join(external_base_dir, "updated")
            # we store new external licenses in this directory
            self.new_dir = os.path.join(external_base_dir, "new")

            if not exists(self.original_dir):
                mkdir(self.original_dir)

            # always cleanup updated and new
            if exists(self.update_dir):
                fileutils.delete(self.update_dir)
            mkdir(self.update_dir)

            if exists(self.new_dir):
                fileutils.delete(self.new_dir)
            mkdir(self.new_dir)

    def get_licenses(
        self,
        scancode_licenses=None,
        use_cache=False,
        **kwargs,
    ):
        """
        Return a mapping of key -> ScanCode License objects either fetched
        externally or loaded from the existing `self.original_dir`
        If ``force_refetch`` the licenses are always refected. Otherwise if
        `self.original_dir` exists, they are loaded from there.
        """
        if not use_cache:
            print("Fetching and storing external licenses in:", self.original_dir)

            licenses = []
            if TRACE_DEEP:
                print()
            for lic in self.fetch_licenses(
                scancode_licenses=scancode_licenses,
                **kwargs,
            ):
                if TRACE_DEEP:
                    start = time.time()

                try:
                    lic.dump(licenses_data_dir=self.original_dir)
                    licenses.append(lic)
                except:
                    if TRACE:
                        print()
                        print(repr(lic))
                    raise
                if TRACE_DEEP:
                    print(
                        f"    Saving fetched license: {lic.key} in :",
                        round(time.time() - start, 1),
                        "s",
                    )

            print(
                "Stored %d external licenses in: %r."
                % (
                    len(licenses),
                    self.original_dir,
                )
            )
        else:
            print("Reusing and loading external licenses in:", self.original_dir)

        print(f"Modified (or not modified) external licenses will be in: {self.update_dir}.")
        fileutils.copytree(self.original_dir, self.update_dir)

        print(f"New external licenses will be in: {self.new_dir}.")
        return load_licenses(self.update_dir, with_deprecated=True)

    def fetch_licenses(self, scancode_licenses, **kwargs):
        """
        Yield License objects fetched from this external source.
        """
        raise NotImplementedError


def get_key_through_text_match(key, text, scancode_licenses, match_approx=False):
    """
    Match text and returna matched license key or None.
    """
    if TRACE_DEEP:
        print("Matching text for:", key, end=". ")
    new_key, exact, score, match_text = get_match(text)
    if not new_key:
        if TRACE_DEEP:
            print("Not TEXT MATCHED:", key, end=". ")
        return None
    if exact is True and score == 100:
        if TRACE_DEEP:
            print("EXACT match to:", new_key, "text:\n", match_text)
        return new_key

    if match_approx:
        if exact is False:
            if TRACE_DEEP:
                print("OK matched to:", new_key, "with score:", score, "text:\n", match_text)
            return new_key

        if exact is None:
            if TRACE_DEEP:
                print("WEAK matched to:", new_key, "with score:", score, "text:\n", match_text)
            return new_key

        if exact == -1:
            if TRACE_DEEP:
                print("JUNK MATCH to:", new_key, "with score:", score, "text:\n", match_text)
            return new_key

    else:
        if TRACE_DEEP:
            print(
                "SKIPPED: WEAK/JUNK MATCH to:", new_key, "with score:", score, "text:\n", match_text
            )


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
        and rule.is_from_license
        and len(rule_licenses) == 1
        and match.matcher == MATCH_HASH
        and match.score() == 100
        and match.len() == query_len
    )

    if is_exact:
        return key, True, 100, matched_text

    is_ok = len(rule_licenses) == 1 and match.coverage() > 95 and match.score() > 95
    if is_ok:
        return key, False, match.score(), matched_text

    is_weak = len(rule_licenses) == 1 and match.coverage() > 90 and match.score() > 90
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

    if TRACE:
        print("==> Fetching URL: %(url)s" % locals())
    response = requests.get(url, headers=headers, params=params)
    status = response.status_code
    if status != requests.codes.ok:  # NOQA
        raise Exception("Failed HTTP request for %(url)r: %(status)r" % locals())
    return response.json()


def clean_text(text):
    """
    Return a cleaned and formatted version of text
    """
    if not text:
        return text
    text = text.rstrip()
    lines = text.splitlines(False)
    formatted = []
    for line in lines:
        line = " ".join(line.split())
        line = textwrap.wrap(line, width=75)
        formatted.extend(line)
    return "\n".join(formatted)


class SpdxSource(ExternalLicensesSource):
    """
    License source for the latest SPDX license list fetched from GitHub.
    """

    matching_key = "spdx_license_key"

    updatable_attributes = (
        "spdx_license_key",
        "other_urls",
        "is_deprecated",
        "is_exception",
        # 'standard_notice',
    )

    non_updatable_attributes = (
        "short_name",
        "name",
        "notes",
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
        latest tagged version or the `commitish` if provided. If
        ``skip_oddities`` is True, some oddities are skipped or handled
        specially, such as licenses with a trailing +.
        """
        for spdx_details in self.fetch_spdx_licenses(
            commitish=commitish,
            skip_oddities=skip_oddities,
            from_repo=from_repo,
        ):

            lic = self.build_license(
                mapping=spdx_details,
                scancode_licenses=scancode_licenses,
                skip_oddities=skip_oddities,
            )

            if lic:
                yield lic

    def fetch_spdx_licenses(
        self,
        commitish=None,
        skip_oddities=True,
        from_repo=SPDX_DEFAULT_REPO,
    ):
        """
        Yield mappings of SPDX License list data fetched from the SPDX license
        list. Use the latest tagged version or the `commitish` if provided.

        If ``skip_oddities`` is True, some oddities are skipped or handled
        specially, such as licenses with a trailing +.
        """
        if not commitish:
            # get latest tag
            tags_url = "https://api.github.com/repos/{from_repo}/tags".format(**locals())
            tags = get_response(tags_url, headers={}, params={})
            tag = tags[0]["name"]
        else:
            tag = commitish

        # fetch licenses and exceptions
        # note that exceptions data have -- weirdly enough -- a different schema
        zip_url = "https://github.com/{from_repo}/archive/{tag}.zip".format(**locals())
        if TRACE:
            print("Fetching SPDX license data version:", tag, "from:", zip_url)
        licenses_zip = fetch.download_url(zip_url, timeout=120)
        if TRACE:
            print("Fetched SPDX licenses to:", licenses_zip)
        with zipfile.ZipFile(licenses_zip) as archive:
            for path in archive.namelist():
                if not (
                    path.endswith(".json")
                    and ("/json/details/" in path or "/json/exceptions/" in path)
                ):
                    continue
                if TRACE:
                    print("Loading license:", path)
                if skip_oddities and path.endswith("+.json"):
                    # Skip the old plus licenses. We use them in
                    # ScanCode, but they are deprecated in SPDX.
                    continue
                yield json.loads(archive.read(path))

    def build_license(self, mapping, skip_oddities=True, scancode_licenses=None):
        """
        Return a License object built from a ``mapping`` of SPDX license data.
        If ``skip_oddities`` is True, some oddities are skipped or handled
        specially, such as license ids with a trailing +.
        """
        spdx_license_key = mapping.get("licenseId") or mapping.get("licenseExceptionId")
        assert spdx_license_key
        spdx_license_key = spdx_license_key.strip()
        key = spdx_license_key.lower()

        # these keys have a complicated history
        spdx_keys_with_complicated_past = set(
            [
                "gpl-1.0",
                "gpl-2.0",
                "gpl-3.0",
                "lgpl-2.0",
                "lgpl-2.1",
                "lgpl-3.0",
                "agpl-1.0",
                "agpl-2.0",
                "agpl-3.0",
                "gfdl-1.1",
                "gfdl-1.2",
                "gfdl-1.3",
                "nokia-qt-exception-1.1",
                "bzip2-1.0.5",
                "bsd-2-clause-freebsd",
                "bsd-2-clause-netbsd",
            ]
        )
        if skip_oddities and key in spdx_keys_with_complicated_past:
            return

        deprecated = mapping.get("isDeprecatedLicenseId", False)
        if skip_oddities and deprecated:
            # we use concrete keys for some plus/or later versions for
            # simplicity and override SPDX deprecation for these
            if key.endswith("+"):
                # 'gpl-1.0+', 'gpl-2.0+', 'gpl-3.0+',
                # 'lgpl-2.0+', 'lgpl-2.1+', 'lgpl-3.0+',
                # 'gfdl-1.1+', 'gfdl-1.2+', 'gfdl-1.3+'
                # 'agpl-3.0+'
                deprecated = False

        other_urls = mapping.get("seeAlso", [])
        other_urls = (o for o in other_urls if o)
        other_urls = (o.strip() for o in other_urls)
        other_urls = (o for o in other_urls if o)
        # see https://github.com/spdx/license-list-data/issues/9
        junk_see_also = ("none", "found")
        other_urls = [o for o in other_urls if o not in junk_see_also]

        standard_notice = mapping.get("standardLicenseHeader") or ""
        if standard_notice:
            standard_notice = clean_text(standard_notice)

        text = (mapping.get("licenseText") or mapping.get("licenseExceptionText")).strip()
        if not text:
            raise Exception(f"Missing text fpr SPDX {spdx_license_key}")

        lic = License(
            key=key,
            spdx_license_key=spdx_license_key,
            text=text,
            name=mapping["name"].strip(),
            short_name=mapping["name"].strip(),
            is_deprecated=deprecated,
            is_exception=bool(mapping.get("licenseExceptionId")),
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
        return lic


# these licenses are rare commercial license with no text and only a
# link or these licenses may be combos of many others or are ignored
# because of some weirdness we detect instead each part of the combos
# separately or as a rule, but not as a single license for now.


# mapping of {license key: reason for skipping}
dejacode_special_skippable_keys = {
    "alglib-commercial": "no license text",
    "atlassian-customer-agreement": "no license text",
    "dalton-maag-eula": "no license text",
    "highsoft-standard-license-agreement-4.0": "no license text",
    "monotype-tou": "no license text",
    "newlib-subdirectory": "composite of many licenses",
    "dejacode": "composite of many licenses",
}


class DejaSource(ExternalLicensesSource):
    """
    License source for DejaCode licenses fetched through its API.
    """

    key_attribute = "key"

    updatable_attributes = (
        "short_name",
        "name",
        "spdx_license_key",
        "homepage_url",
        "category",
        "owner",
        "text_urls",
        "language",
        "osi_url",
        "faq_url",
        "other_urls",
        "is_deprecated",
        "is_exception",
        # not yet
        # "notes",
        # "standard_notice",
    )
    non_updatable_attributes = ("notes",)

    def __init__(self, external_base_dir=None, api_base_url=None, api_key=None):
        self.api_base_url = (api_base_url or os.getenv("DEJACODE_API_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("DEJACODE_API_KEY")
        assert self.api_key and self.api_base_url, (
            "You must set the DEJACODE_API_URL and DEJACODE_API_KEY "
            "environment variables before running this script."
        )

        super(DejaSource, self).__init__(external_base_dir)

    def fetch_licenses(self, scancode_licenses, per_page=100, max_fetch=None, **kwargs):

        license_data = self.fetch_license_data(per_page=per_page, max_fetch=max_fetch)
        license_data = self.filter_license_data(license_data, scancode_licenses)

        for lic_data in license_data:
            lic = self.build_license(mapping=lic_data)
            if lic:
                yield lic

    def fetch_license_data(self, per_page=100, max_fetch=None, **kwargs):
        """
        Yield mappings of license daa fetched from the API.
        """
        api_url = f"{self.api_base_url}/licenses/"
        for licenses in call_deja_api(api_url, self.api_key, paginate=per_page):
            for lic_data in licenses:
                if max_fetch is not None:
                    if max_fetch > 0:
                        max_fetch -= 1
                    else:
                        return
                yield lic_data

    def filter_license_data(self, license_data, scancode_licenses, skip_oddities=True):
        """
        Return a filtered iterable of ``license_data``
        """
        assert scancode_licenses

        for lic_data in license_data:
            key = lic_data["key"]

            if skip_oddities:
                special_reason = dejacode_special_skippable_keys.get(key)
                if special_reason:
                    if TRACE:
                        print(f"Skipping special DejaCode license: {key}: {special_reason}")
                    continue

            deprecated = not lic_data.get("is_active")
            if deprecated and key not in scancode_licenses.by_key:
                if TRACE:
                    print("Skipping deprecated license not in ScanCode:", key)
                continue

            yield lic_data

    def build_license(self, mapping, *args, **kwargs):
        """
        Return a License object built from a DejaCode license mapping or None
        for skipped licenses.
        """

        key = mapping["key"]
        standard_notice = mapping.get("standard_notice") or ""
        standard_notice = clean_text(standard_notice)
        # notes = mapping.get("reference_notes") or ""
        # notes = clean_text(notes)

        deprecated = not mapping.get("is_active")
        spdx_license_key = mapping.get("spdx_license_key") or None
        if deprecated:
            spdx_license_key = None
        else:
            if not spdx_license_key:
                spdx_license_key = f"LicenseRef-scancode-{key}"

        text = mapping["full_text"] or ""
        # normalize EOL to POSIX
        text = text.replace("\r\n", "\n").strip()

        lic = License(
            key=key,
            text=text,
            name=mapping["name"],
            short_name=mapping["short_name"],
            language=mapping.get("language") or "en",
            homepage_url=mapping["homepage_url"],
            category=mapping["category"],
            owner=mapping["owner_name"],
            # FIXME: we may not want to carry notes over???
            # lic.notes = mapping.notes
            spdx_license_key=spdx_license_key,
            text_urls=mapping["text_urls"].splitlines(False),
            osi_url=mapping["osi_url"],
            faq_url=mapping["faq_url"],
            other_urls=mapping["other_urls"].splitlines(False),
            is_exception=mapping.get("is_exception", False),
            is_deprecated=deprecated,
            standard_notice=standard_notice,
            # notes=notes,
        )
        return lic

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

    def fetch_spdx_license_details(
        self,
        scancode_licenses,
        per_page=100,
        max_fetch=None,
        **kwargs,
    ):
        """
        Yield a tuple of (license key, SPDX license key, license_api_url) for DejaCode licenses.
        """
        license_data = self.fetch_license_data(per_page=per_page, max_fetch=max_fetch)
        license_data = self.filter_license_data(license_data, scancode_licenses)
        for lic_data in license_data:
            key = lic_data["key"]
            spdx_license_key = lic_data.get("spdx_license_key") or None
            license_api_url = lic_data["api_url"]
            yield key, spdx_license_key, license_api_url

    def patch_spdx_license(self, api_url, license_key, spdx_license_key):
        """
        PATCH the DejaCode ``license_key`` to set the ``spdx_license_key``
        using the DejaCode API.
        Raise an exception on failure.
        """
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json; indent=2",
        }
        params = dict(key=license_key, spdx_license_key=spdx_license_key)
        response = requests.patch(api_url, headers=headers, json=params)
        if not response.ok:
            content = response.content
            headers = response.headers
            raise Exception(
                f"Failed to update license: {license_key!r} "
                f"with SPDX: {spdx_license_key!r} "
                f"at {api_url}:\n{headers}\n{content}"
            )


def call_deja_api(api_url, api_key, paginate=0, params=None):
    """
    Yield result mappings from the reponses of calling the API at
    `api_url` with `api_key` . Raise an exception on failure.

    Pass `headers` and `params` mappings to the
    underlying request if provided.
    If `paginate` is a non-zero attempt to paginate with `paginate`
    number of pages at a time and return all the results.
    """
    headers = get_api_headers(api_key)
    params = params or {}
    if paginate:
        assert isinstance(paginate, int)
        params["page_size"] = paginate

        first = True
        while True:
            response = get_response(api_url, headers, params)
            if first:
                first = False
                # use page_size only on first call.
                # the next URL already contains the page_size
                params.pop("page_size")

            yield response.get("results", [])

            api_url = response.get("next")
            if not api_url:
                break
    else:
        response = get_response(api_url, headers, params)
        yield response.get("results", [])


def get_deja_api_data(api_url, api_key, params=None):
    """
    Return a results mapping from calling the API at ``api_url`` with
    ``api_key``. Raise an exception on failure.
    Pass the `params` mappings to the underlying request if provided.
    """
    data = {}
    for results in call_deja_api(api_url, api_key, params=params or {}):
        data.update(results)
    return data


def create_or_update_license(api_url, api_key, lico, update=False):
    """
    POST the ``lico`` License object to the DejaCode API at ``api_url`` with
    ``api_key``. Raise an exception on failure. Create license if needed. Update
    existing with a PATCH request if ``update`` is True.
    """
    _owner = get_or_create_owner(api_url, api_key, lico.owner, create=True)

    url = f"{api_url}/licenses/"
    headers = get_api_headers(api_key)

    # recheck that the license key does not exists remotely
    params = dict(key=lico.key)
    # note: we GET params
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception(f"Failed to fetch license for {lico.key} at {url}:\n{headers}\n{content}")

    results = response.json().get("results", [])

    if not results:
        # add new license
        data = license_to_dict(lico)
        data = add_license_creation_fields(data)
        response = requests.post(url, headers=headers, json=data)
        if not response.ok:
            content = response.content
            headers = response.headers
            raise Exception(f"Failed to create license: {lico.key} at {url}:\n{headers}\n{content}")

        print("Created new license:", lico)
        created = response.json()

        if TRACE_DEEP:
            pprint(created)
        return created
    else:
        # update existing license if requested
        if not update:
            if TRACE:
                print(f"License already exists, no update requested, skipping: {lico.key}")
            return

        # get updatable attributes external remote with current license
        data = license_to_dict(lico)
        # if change that can be updated, craft PATCH request
        if data:
            # force the status to pending when we update
            data.update(
                license_status="Pending",
            )
            response = requests.patch(url, headers=headers, json=data)
        if not response.ok:
            content = response.content
            headers = response.headers
            raise Exception(f"Failed to update license: {lico.key} at {url}:\n{headers}\n{content}")

        new_results = response.json().get("results", [])
        if TRACE:
            print("Updated license details:", new_results)


def get_or_create_owner(api_url, api_key, name, create=False):
    """
    Check if owner name exists. If `create` create the owner if it does not
    exists in the DejaCode API at `api_url` with `api_key`. Raise an exception
    on failure.
    """

    owner = get_owner(api_url, api_key, name)
    if owner:
        if TRACE:
            print("Owner exists:", name)
            if TRACE_DEEP:
                pprint(owner)
        return owner

    if not create:
        if TRACE:
            print("No existing owner:", name)
        return

    url = f"{api_url}/owners/"
    headers = get_api_headers(api_key)

    # note: we post JSON
    params = dict(name=name.strip())
    response = requests.post(url, headers=headers, json=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception(
            f"Failed to create owner request for {name} at {url}:\n{headers}\n{content}"
        )

    result = response.json()
    if TRACE:
        print("Created new owner:", name)
        if TRACE_DEEP:
            pprint(result)
    return result


def get_api_headers(api_key):
    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json; indent=2",
    }


def get_owner(api_url, api_key, name):
    """
    Check if owner name exists in the DejaCode API at `api_url` with `api_key`.
    Raise an exception on failure. Return None if the name does not exist and
    the owner data otherwise
    """
    headers = {
        "Authorization": "Token {}".format(api_key),
        "Accept": "application/json; indent=2",
    }
    params = dict(name=name.strip())
    url = api_url.rstrip("/")
    url = "{url}/owners/".format(**locals())
    # note: we get PARAMS
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        content = response.content
        headers = response.headers
        raise Exception(
            "Failed to get owner for {name} at {url}:\n{headers}\n{content}".format(**locals())
        )

    results = response.json().get("results", [])

    if results:
        result = results[0]
        if TRACE_DEEP:
            print("Existing owner:", name)
            pprint(result)
        return result


def license_to_dict(lico):
    """
    Return a dict of license data with texts usable for API calls given a ``lico``
    ScanCode License object. Fields with empty values are not included.
    """
    licm = dict(
        key=lico.key,
        category=lico.category,
        short_name=lico.short_name,
        name=lico.name,
        owner=lico.owner,
        is_exception=lico.is_exception,
        language=lico.language or "en",
        full_text=lico.text,
        spdx_license_key=lico.spdx_license_key,
        reference_notes=lico.notes,
        homepage_url=lico.homepage_url,
        text_urls="\n".join(lico.text_urls or []),
        osi_url=lico.osi_url,
        faq_url=lico.faq_url,
        other_urls="\n".join(lico.other_urls or []),
    )
    return {k: v for k, v in sorted(licm.items()) if v}


def add_license_creation_fields(license_mapping):
    """
    Return an updated ``license_mapping`` of license data adding license status
    fields needed for license creation.
    """
    license_mapping.update(
        is_active=None,
        reviewed=False,
        license_status="NotReviewed",
    )
    return license_mapping


EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES = {
    "dejacode": DejaSource,
    "spdx": SpdxSource,
}


def merge_licenses(
    scancode_license,
    external_license,
    updatable_attributes,
    from_spdx=False,
):
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
    if TRACE_DEEP:
        print("merge_licenses:", scancode_license, external_license)

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
                f"Non mergeable licenses with different SPDX keys: "
                "scancode_license.spdx_license_key {scancode_key} <>  "
                "external_license.spdx_license_key {external_key}"
            )
    else:
        scancode_key = scancode_license.key
        external_key = external_license.key
        if scancode_key != external_key:
            raise Exception(
                "Non mergeable licenses with different keys: "
                "%(scancode_key)s <> %(external_key)s" % locals()
            )

        if scancode_license.spdx_license_key != external_license.spdx_license_key:
            if TRACE_DEEP:
                print(
                    f"Updating external SPDX key: from {external_license.spdx_license_key} to {scancode_license.spdx_license_key}"
                )
            external_license.spdx_license_key = scancode_license.spdx_license_key

    for attrib in updatable_attributes:
        scancode_value = getattr(scancode_license, attrib)
        external_value = getattr(external_license, attrib)

        # for boolean flags, the other license wins. But only for True.
        # all our flags are False by default
        if isinstance(scancode_value, bool) and isinstance(external_value, bool):
            if scancode_value is False and scancode_value != external_value:
                update_scancode(attrib, scancode_value, external_value)
            continue

        # We merge sequences
        if isinstance(scancode_value, (list, tuple)) and isinstance(external_value, (list, tuple)):
            normalized_scancode_value = set(s for s in scancode_value if s and s.strip())
            normalize_external_value = set(s for s in external_value if s and s.strip())

            # special case for URL lists, we consider all URL fields to
            # update
            if attrib.endswith(
                "_urls",
            ):
                all_sc_urls = set(
                    list(normalized_scancode_value)
                    + scancode_license.text_urls
                    + scancode_license.other_urls
                    + [
                        scancode_license.homepage_url,
                        scancode_license.osi_url,
                        scancode_license.faq_url,
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

        if isinstance(scancode_value, str) and isinstance(external_value, str):
            # make value stripped and with normalized spaces
            normalized_scancode_value = " ".join(scancode_value.split())
            normalize_external_value = " ".join(external_value.split())

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
            # unless we have SPDX ids
            if attrib == "spdx_license_key" and external_value.startswith("LicenseRef-scancode"):
                update_external(attrib, scancode_value, external_value)
            else:
                update_scancode(attrib, scancode_value, external_value)
            continue

    return updated_scancode_attributes, updated_external_attributes


def synchronize_licenses(
    scancode_licenses,
    external_source,
    use_spdx_key=False,
    match_text=False,
    match_approx=False,
    commitish=None,
    use_cache=False,
):
    """
    Return a tuple of lists of License objects:
    - a list of added_to_external
    - a list of updated_in_external

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
    if TRACE:
        print("Synchronize_licenses using SPDX keys:", use_spdx_key)

    # mappings of key -> License
    scancodes_by_key = scancode_licenses.by_key

    if TRACE_DEEP:
        start = time.time()

    externals_by_key = external_source.get_licenses(
        scancode_licenses,
        commitish=commitish,
        use_cache=use_cache,
    )

    if TRACE_DEEP:
        print("Fetched all externals_by_key licenses in:", int(time.time() - start))

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
    for matching_key, scancode_license in sorted(scancodes_by_key.items()):

        if not TRACE:
            print(".", end="")

        # does this scancode license exists in others based on the matching key?
        external_license = externals_by_key.get(matching_key)
        if not external_license:
            if TRACE_DEEP:
                print("ScanCode license not in External:", matching_key)
            unmatched_scancode_by_key[scancode_license.key] = scancode_license
            continue

        # the matching key exists on both sides: merge/update both licenses
        scancode_updated, external_updated = merge_licenses(
            scancode_license=scancode_license,
            external_license=external_license,
            updatable_attributes=external_source.updatable_attributes,
            from_spdx=use_spdx_key,
        )

        if not scancode_updated and not external_updated:
            if TRACE_DEEP:
                print("License attributes are identical:", matching_key)
            same.add(matching_key)

        if scancode_updated:
            if TRACE:
                print(
                    "ScanCode license updated: SPDX:",
                    use_spdx_key,
                    matching_key,
                    end=". Attributes: ",
                )
            for attrib, oldv, newv in scancode_updated:
                if TRACE:
                    print("  %(attrib)s: %(oldv)r -> %(newv)r" % locals())
            updated_in_scancode.add(matching_key)

        if external_updated:
            if TRACE:
                print(
                    "External license updated: SPDX:",
                    use_spdx_key,
                    matching_key,
                    end=". Attributes: ",
                )
            for attrib, oldv, newv in external_updated:
                if TRACE:
                    print("  %(attrib)s: %(oldv)r -> %(newv)r" % locals())
            updated_in_external.add(matching_key)

    # 2. iterate other licenses and compare with ScanCode
    if TRACE:
        print()
    for matching_key, external_license in sorted(externals_by_key.items()):
        # does this key exists in scancode?
        scancode_license = scancodes_by_key.get(matching_key)
        if scancode_license:
            # we already dealt with this in the first loop
            continue

        if not TRACE:
            print(".", end="")

        if match_text:

            matched_key = get_key_through_text_match(
                key=matching_key,
                text=external_license.text,
                scancode_licenses=scancode_licenses,
                match_approx=match_approx,
            )

            if TRACE:
                print(
                    "External license with different key:",
                    matching_key,
                    "and text matched to ScanCode key:",
                    matched_key,
                )

            if matched_key:
                print(
                    "External license with different key:",
                    matching_key,
                    "and text matched to ScanCode key:",
                    matched_key,
                )
                if matched_key in unmatched_scancode_by_key:
                    del unmatched_scancode_by_key[matched_key]

                scancode_license = scancodes_by_key.get(matched_key)
                if TRACE:
                    print("scancode_license:", matching_key, scancode_license)

                scancode_updated, external_updated = merge_licenses(
                    scancode_license=scancode_license,
                    external_license=external_license,
                    updatable_attributes=external_source.updatable_attributes,
                    from_spdx=use_spdx_key,
                )

                if not scancode_updated and not external_updated:
                    if TRACE_DEEP:
                        print("License attributes are identical:", matching_key)
                    same.add(matching_key)

                if scancode_updated:
                    if TRACE:
                        print(
                            "ScanCode license updated: SPDX:",
                            use_spdx_key,
                            matching_key,
                            end=". Attributes: ",
                        )
                    for attrib, oldv, newv in scancode_updated:
                        if TRACE:
                            print("  %(attrib)s: %(oldv)r -> %(newv)r" % locals())
                    updated_in_scancode.add(matching_key)

                if external_updated:
                    if TRACE:
                        print(
                            "External license updated: SPDX:",
                            use_spdx_key,
                            matching_key,
                            end=". Attributes: ",
                        )
                    for attrib, oldv, newv in external_updated:
                        if TRACE:
                            print("  %(attrib)s: %(oldv)r -> %(newv)r" % locals())
                    updated_in_external.add(matching_key)

        else:
            # Create a new ScanCode license
            external_license.key = matching_key
            external_license.dump(
                licenses_data_dir=licensedcode.models.licenses_data_dir
            )
            added_to_scancode.add(matching_key)
            scancodes_by_key[matching_key] = external_license
            if TRACE:
                print(
                    "External license key not in ScanCode:",
                    matching_key,
                    "created in ScanCode.",
                    "SPDX:",
                    use_spdx_key,
                )

    # 3. For scancode licenses that were not matched to anything in external add them in external
    if TRACE:
        print()
        print("Processing unmatched_scancode_by_key.")

    for lkey, scancode_license in sorted(unmatched_scancode_by_key.items()):
        if lkey in set(
            [
                "here-proprietary"
                # these licenses are ignored for now for some weirdness
                # invalid case
                "sun-jta-spec-1.0.1b",
                "sun-jta-spec-1.0.1B",
            ]
        ):
            continue

        if scancode_license.is_deprecated:
            continue

        scancode_license.dump(licenses_data_dir=external_source.new_dir)
        added_to_external.add(lkey)
        externals_by_key[lkey] = scancode_license

        if TRACE_DEEP:
            print("ScanCode license key not in External:", lkey, "created in External.")

    # finally write changes in place for updated and new
    for k in sorted(updated_in_scancode | added_to_scancode):
        lic = scancodes_by_key[k]
        if not lic:
            raise Exception(k)
        models.update_ignorables(lic, verbose=False)
        lic.dump(licenses_data_dir=licensedcode.models.licenses_data_dir)

    if TRACE_DEEP:
        print(
            "updated_in_external:",
            len(updated_in_external),
            "added_to_external:",
            len(added_to_external),
        )
    for k in sorted(updated_in_external | added_to_external):
        lic = externals_by_key[k]
        if not lic:
            raise Exception(f"Failed to process added or updated license: {k}")
        lic.dump(licenses_data_dir=licensedcode.models.licenses_data_dir)

    # TODO: at last: print report of incorrect OTHER licenses to submit
    # updates eg. make API calls to DejaCode to create or update
    # licenses and submit review request e.g. submit requests to SPDX
    # for addition
    for key in sorted(added_to_external):
        lic = externals_by_key[key]
        if not lic.owner:
            print("New external license without owner:", key)

    print()
    print("#####################################################")
    print("Same licenses:       ", len(same))
    print("Add to ScanCode:     ", len(added_to_scancode))
    print("Updated in ScanCode: ", len(updated_in_scancode))
    print("Added to External::  ", len(added_to_external))
    print("Updated in External: ", len(updated_in_external))
    print("#####################################################")

    added_to_external = [externals_by_key[k] for k in added_to_external]
    updated_in_external = [externals_by_key[k] for k in updated_in_external]
    external_source.externals_by_key = externals_by_key
    return sorted(added_to_external), sorted(updated_in_external)


@click.command()
@click.argument("license_dir", type=click.Path(), metavar="DIR")
@click.option(
    "-s",
    "--source",
    type=click.Choice(EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES),
    help="Select an external license source.",
)
@click.option(
    "-m",
    "--match-text",
    is_flag=True,
    default=False,
    help="Match external license texts with license detection to find a matching ScanCode license.",
)
@click.option(
    "-a",
    "--match-approx",
    is_flag=True,
    default=False,
    help="Include approximate license detection matches when matching ScanCode license.",
)
@click.option("-t", "--trace", is_flag=True, default=False, help="Print execution trace.")
@click.option(
    "--create-external",
    is_flag=True,
    default=False,
    help="Create new licenses in the remote external source if possible.",
)
@click.option(
    "--update-external",
    is_flag=True,
    default=False,
    help="Update existing licenses in the remote external source if possible.",
)
@click.option(
    "--commitish",
    type=str,
    default=None,
    help="An optional commitish to use for SPDX license data instead of the latest release.",
)
@click.option(
    "--use-cache",
    is_flag=True,
    default=False,
    help="Use cached data, do not re-fetch external licenses. Instead, reuse previously fetched external licenses if available.",
)
@click.help_option("-h", "--help")
def cli(
    license_dir,
    source,
    match_text,
    match_approx,
    trace,
    create_external,
    update_external,
    commitish=None,
    use_cache=False,
):
    """
    Synchronize ScanCode licenses with an external license source.

    DIR is the directory to store fetched external licenses (or where to load
    from already fetched licenses). Side-by-side with "DIR", three directories
    are created with new, updated or deleted licenses (with regards to ScanCode
    licenses). The ScanCode licenses are collected from the current installation.

    When using the dejacode source your need to set the 'DEJACODE_API_URL' and
    'DEJACODE_API_KEY' environment variables with your credentials.
    """
    global TRACE
    TRACE = trace

    licenses_source_class = EXTERNAL_LICENSE_SYNCHRONIZATION_SOURCES[source]
    external_source = licenses_source_class(license_dir)
    scancode_licenses = ScanCodeLicenses()

    use_spdx_key = source == "spdx"
    added_to_external, updated_in_external = synchronize_licenses(
        scancode_licenses,
        external_source,
        use_spdx_key=use_spdx_key,
        match_text=match_text,
        match_approx=match_approx,
        commitish=commitish,
        use_cache=use_cache,
    )
    print()
    if source == "dejacode":
        if create_external:
            api_url = external_source.api_base_url
            api_key = external_source.api_key
            for new_lic in added_to_external:
                if new_lic.key in dejacode_special_skippable_keys:
                    continue
                if TRACE:
                    print(f"Creating external: {new_lic}")
                create_or_update_license(api_url, api_key, lico=new_lic)

        if update_external:
            externals_by_key = external_source.externals_by_key
            for modified_lic in updated_in_external:
                if modified_lic.key in dejacode_special_skippable_keys:
                    continue
                mold = license_to_dict(modified_lic)
                original = externals_by_key[modified_lic.key]
                orld = license_to_dict(original)
                if mold != orld:
                    # we need to update
                    if TRACE:
                        print(f"Updating external: {modified_lic}")
                    create_or_update_license(api_url, api_key, lico=modified_lic, update=True)


if __name__ == "__main__":
    cli()
