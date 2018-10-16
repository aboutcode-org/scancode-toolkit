#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from itertools import islice
from os.path import getsize

from commoncode.filetype import get_last_modified_date
from commoncode.hash import multi_checksums
from typecode.contenttype import get_type

"""
Main scanning functions.

Each scanner is a function that accepts a location and returns a sequence of
mappings as results.

Note: this API is unstable and still evolving.
"""


def get_copyrights(location, **kwargs):
    """
    Return a mapping with a single 'copyrights' key with a value that is a list
    of mappings for copyright detected in the file at `location`.
    """
    from cluecode.copyrights import detect_copyrights

    copyrights = []
    holders = []
    authors = []

    for dtype, value, start, end in detect_copyrights(location):

        if dtype == 'copyrights':
            copyrights.append(
                OrderedDict([
                    ('value', value),
                    ('start_line', start),
                    ('end_line', end)
                ])
            )
        elif dtype == 'holders':
            holders.append(
                OrderedDict([
                    ('value', value),
                    ('start_line', start),
                    ('end_line', end)
                ])
            )
        elif dtype == 'authors':
            authors.append(
                OrderedDict([
                    ('value', value),
                    ('start_line', start),
                    ('end_line', end)
                ])
            )

    results = OrderedDict([
        ('copyrights', copyrights),
        ('holders', holders),
        ('authors', authors),
    ])

    return results


def get_emails(location, threshold=50, **kwargs):
    """
    Return a mapping with a single 'emails' key with a value that is a list of
    mappings for emails detected in the file at `location`.
    Return only up to `threshold` values. Return all values if `threshold` is 0.
    """
    from cluecode.finder import find_emails
    results = []

    found_emails = ((em, ln) for (em, ln) in find_emails(location) if em)
    if threshold:
        found_emails = islice(found_emails, threshold)

    for email, line_num in found_emails:
        result = OrderedDict()
        results.append(result)
        result['email'] = email
        result['start_line'] = line_num
        result['end_line'] = line_num
    return dict(emails=results)


def get_urls(location, threshold=50, **kwargs):
    """
    Return a mapping with a single 'urls' key with a value that is a list of
    mappings for urls detected in the file at `location`.
    Return only up to `threshold` values. Return all values if `threshold` is 0.
    """
    from cluecode.finder import find_urls
    results = []

    found_urls = ((u, ln) for (u, ln) in find_urls(location) if u)
    if threshold:
        found_urls = islice(found_urls, threshold)

    for urls, line_num in found_urls:
        result = OrderedDict()
        results.append(result)
        result['url'] = urls
        result['start_line'] = line_num
        result['end_line'] = line_num
    return dict(urls=results)


DEJACODE_LICENSE_URL = 'https://enterprise.dejacode.com/urn/urn:dje:license:{}'
SPDX_LICENSE_URL = 'https://spdx.org/licenses/{}'


def get_licenses(location, min_score=0, include_text=False, diag=False,
                 license_url_template=DEJACODE_LICENSE_URL,
                 cache_dir=None, **kwargs):
    """
    Return a mapping or detected_licenses for licenses detected in the file at `location`.
    This mapping contains two keys:
     - 'licenses' with a value that is list of mappings of license information.
     - 'license_expressions' with a value that is list of license expression
       strings.

    `minimum_score` is a minimum score threshold from 0 to 100. The default is 0
    means that all license matches are returned. Otherwise, matches with a score
    below `minimum_score` are returned.

    if `include_text` is True, matched text is included in the returned
    `licenses` data.

    If `diag` is True, additional license match details are returned with the
    "matched_rule" key of the returned `licenses` data.
    """
    from scancode_config import SCANCODE_DEV_MODE
    if not cache_dir:
        from scancode_config import scancode_cache_dir as cache_dir

    from licensedcode.cache import get_index
    from licensedcode.cache import get_licenses_db

    idx = get_index(cache_dir, SCANCODE_DEV_MODE)
    licenses = get_licenses_db()

    detected_licenses = []
    detected_expressions = []
    for match in idx.match(location=location, min_score=min_score):

        if include_text:
            # TODO: handle whole lines with the case of very long lines
            matched_text = match.matched_text(whole_lines=False)

        detected_expressions.append(match.rule.license_expression)

        for license_key in match.rule.license_keys():
            lic = licenses.get(license_key)
            result = OrderedDict()
            detected_licenses.append(result)
            result['key'] = lic.key
            result['score'] = match.score()
            result['name'] = lic.name
            result['short_name'] = lic.short_name
            result['category'] = lic.category
            result['is_exception'] = lic.is_exception
            result['owner'] = lic.owner
            result['homepage_url'] = lic.homepage_url
            result['text_url'] = lic.text_urls[0] if lic.text_urls else ''
            result['reference_url'] = license_url_template.format(lic.key)
            spdx_key = lic.spdx_license_key
            result['spdx_license_key'] = spdx_key
            if spdx_key:
                spdx_key = lic.spdx_license_key.rstrip('+')
                spdx_url = SPDX_LICENSE_URL.format(spdx_key)
            else:
                spdx_url = ''
            result['spdx_url'] = spdx_url
            result['start_line'] = match.start_line
            result['end_line'] = match.end_line
            matched_rule = result['matched_rule'] = OrderedDict()
            matched_rule['identifier'] = match.rule.identifier
            matched_rule['license_expression'] = match.rule.license_expression
            matched_rule['licenses'] = match.rule.license_keys()

            matched_rule['is_license_text'] = match.rule.is_license_text
            matched_rule['is_license_notice'] = match.rule.is_license_notice
            matched_rule['is_license_reference'] = match.rule.is_license_reference
            matched_rule['is_license_tag'] = match.rule.is_license_tag

            # FIXME: for sanity these should always be included??? or returned as a flat item sset?
            if diag:
                matched_rule['matcher'] = match.matcher
                matched_rule['rule_length'] = match.rule.length
                matched_rule['matched_length'] = match.ilen()
                matched_rule['match_coverage'] = match.coverage()
                matched_rule['rule_relevance'] = match.rule.relevance
            # FIXME: for sanity this should always be included?????
            if include_text:
                result['matched_text'] = matched_text

    return OrderedDict([
        ('licenses', detected_licenses),
        ('license_expressions', detected_expressions),
    ])


def get_package_info(location, **kwargs):
    """
    Return a mapping of package manifest information detected in the
    file at `location`.

    Note that all exceptions are caught if there are any errors while parsing a
    package manifest.
    """
    from packagedcode.recognize import recognize_package
    try:
        manifest = recognize_package(location)
        if manifest:
            return dict(packages=[manifest.to_dict()])
    except Exception:
        # FIXME: this should be logged somehow, but for now we avoid useless
        # errors per #983
        pass
    return dict(packages=[])


def get_file_info(location, **kwargs):
    """
    Return a mapping of file information collected for the file at `location`.
    """
    result = OrderedDict()

    # TODO: move date and size these to the inventory collection step???
    result['date'] = get_last_modified_date(location) or None
    result['size'] = getsize(location) or 0

    sha1, md5 = multi_checksums(location, ('sha1', 'md5',)).values()
    result['sha1'] = sha1
    result['md5'] = md5

    collector = get_type(location)
    result['mime_type'] = collector.mimetype_file or None
    result['file_type'] = collector.filetype_file or None
    result['programming_language'] = collector.programming_language or None
    result['is_binary'] = bool(collector.is_binary)
    result['is_text'] = bool(collector.is_text)
    result['is_archive'] = bool(collector.is_archive)
    result['is_media'] = bool(collector.is_media)
    result['is_source'] = bool(collector.is_source)
    result['is_script'] = bool(collector.is_script)
    return result


def extract_archives(location, recurse=True):
    """
    Yield ExtractEvent while extracting archive(s) and compressed files at
    `location`. If `recurse` is True, extract nested archives-in-archives
    recursively.
    Archives and compressed files are extracted in a directory named
    "<file_name>-extract" created in the same directory as the archive.
    Note: this API is returning an iterable and NOT a sequence.
    """
    from extractcode.extract import extract
    from extractcode import default_kinds
    for xevent in extract(location, kinds=default_kinds, recurse=recurse):
        yield xevent
