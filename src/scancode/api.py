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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

from commoncode.fileutils import as_posixpath
from commoncode.fileutils import path_to_bytes
from commoncode.fileutils import path_to_unicode
from commoncode.system import on_linux
from scancode.utils import get_relative_path


"""
Main scanning functions.
Note: this API is unstable and still evolving.
"""

class Resource(object):
    """
    Store scanned details for a single resource (file or a directory)
    such as infos and path
    """

    def __init__(self, scan_cache_class, abs_path, base_is_dir, len_base_path):
        self.scan_cache_class = scan_cache_class()
        self.is_cached = False
        self.abs_path = abs_path
        self.base_is_dir = base_is_dir
        posix_path = as_posixpath(abs_path)
        # fix paths: keep the path as relative to the original
        # base_path. This is always Unicode
        self.rel_path = get_relative_path(posix_path, len_base_path, base_is_dir)
        self.infos = OrderedDict()
        self.infos['path'] = self.rel_path

    def put_info(self, infos):
        """
        Cache file info and set `is_cached` to True if already cached or false otherwise.
        """
        self.infos.update(infos)
        self.is_cached = self.scan_cache_class.put_info(self.rel_path, self.infos)

    def get_info(self):
        """
        Retrieve info from cache.
        """
        return self.scan_cache_class.get_info(self.rel_path)


def extract_archives(location, recurse=True):
    """
    Extract any archives found at `location` and yield ExtractEvents. If
    `recurse` is True, extracts nested archives-in- archives
    recursively.
    """
    from extractcode.extract import extract
    from extractcode import default_kinds
    for xevent in extract(location, kinds=default_kinds, recurse=recurse):
        yield xevent


def get_copyrights(location):
    """
    Yield mappings of copyright data detected in the file at `location`.
    """
    from cluecode.copyrights import detect_copyrights

    for copyrights, authors, _years, holders, start_line, end_line in detect_copyrights(location):
        result = OrderedDict()
        # FIXME: we should call this copyright instead, and yield one item per statement
        result['statements'] = copyrights
        result['holders'] = holders
        result['authors'] = authors
        result['start_line'] = start_line
        result['end_line'] = end_line
        yield result


def get_emails(location):
    """
    Yield mappings of emails detected in the file at `location`.
    """
    from cluecode.finder import find_emails
    for email, line_num  in find_emails(location):
        if not email:
            continue
        misc = OrderedDict()
        misc['email'] = email
        misc['start_line'] = line_num
        misc['end_line'] = line_num
        yield misc


def get_urls(location):
    """
    Yield mappings of urls detected in the file at `location`.
    """
    from cluecode.finder import find_urls
    for urls, line_num  in find_urls(location):
        if not urls:
            continue
        misc = OrderedDict()
        misc['url'] = urls
        misc['start_line'] = line_num
        misc['end_line'] = line_num
        yield misc


DEJACODE_LICENSE_URL = 'https://enterprise.dejacode.com/urn/urn:dje:license:{}'
SPDX_LICENSE_URL = 'https://spdx.org/licenses/{}'


def get_licenses(location, min_score=0, include_text=False, diag=False, license_url_template=DEJACODE_LICENSE_URL):
    """
    Yield mappings of license data detected in the file at `location`.

    `minimum_score` is a minimum score threshold from 0 to 100. The
    default is 0 means that all license matches will be returned. With
    any other value matches that have a score below minimum score with
    not be returned.

    if `include_text` is True, the matched text is included in the
    returned data.

    If `diag` is True, additional match details are returned with the
    matched_rule key of the returned mapping.
    """
    from licensedcode.cache import get_index
    from licensedcode.cache import get_licenses_db

    idx = get_index()
    licenses = get_licenses_db()

    for match in idx.match(location=location, min_score=min_score):
        if include_text:
            matched_text = match.matched_text(whole_lines=False)
        for license_key in match.rule.licenses:
            lic = licenses.get(license_key)
            result = OrderedDict()
            result['key'] = lic.key
            result['score'] = match.score()
            result['short_name'] = lic.short_name
            result['category'] = lic.category
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
            matched_rule['license_choice'] = match.rule.license_choice
            matched_rule['licenses'] = match.rule.licenses
            # FIXME: for sanity these should always be included???
            if diag:
                matched_rule['matcher'] = match.matcher
                matched_rule['rule_length'] = match.rule.length
                matched_rule['matched_length'] = match.ilen()
                matched_rule['match_coverage'] = match.coverage()
                matched_rule['rule_relevance'] = match.rule.relevance
            # FIXME: for sanity this should always be included?????
            if include_text:
                result['matched_text'] = matched_text
            yield result


def get_file_infos(location):
    """
    Return a mapping of file information collected from the file or
    directory at `location`.
    """
    from commoncode import fileutils
    from commoncode import filetype
    from commoncode.hash import multi_checksums
    from typecode import contenttype

    if on_linux:
        location = path_to_bytes(location)
    else:
        location = path_to_unicode(location)

    infos = OrderedDict()
    is_file = filetype.is_file(location)
    is_dir = filetype.is_dir(location)

    T = contenttype.get_type(location)

    infos['type'] = filetype.get_type(location, short=False)
    name = fileutils.file_name(location)
    if is_file:
        base_name, extension = fileutils.splitext(location)
    else:
        base_name = name
        extension = ''

    if on_linux:
        infos['name'] = path_to_unicode(name)
        infos['base_name'] = path_to_unicode(base_name)
        infos['extension'] = path_to_unicode(extension)
    else:
        infos['name'] = name
        infos['base_name'] = base_name
        infos['extension'] = extension

    infos['date'] = is_file and filetype.get_last_modified_date(location) or None
    infos['size'] = T.size
    infos.update(multi_checksums(location, ('sha1', 'md5',)))
    infos['files_count'] = is_dir and filetype.get_file_count(location) or None
    infos['mime_type'] = is_file and T.mimetype_file or None
    infos['file_type'] = is_file and T.filetype_file or None
    infos['programming_language'] = is_file and T.programming_language or None
    infos['is_binary'] = bool(is_file and T.is_binary)
    infos['is_text'] = bool(is_file and T.is_text)
    infos['is_archive'] = bool(is_file and T.is_archive)
    infos['is_media'] = bool(is_file and T.is_media)
    infos['is_source'] = bool(is_file and T.is_source)
    infos['is_script'] = bool(is_file and T.is_script)

    return infos


# FIXME: this smells bad
def _empty_file_infos():
    """
    Return an empty mapping of file info, used in case of failure.
    """
    infos = OrderedDict()
    infos['type'] = None
    infos['name'] = None
    infos['extension'] = None
    infos['date'] = None
    infos['size'] = None
    infos['sha1'] = None
    infos['md5'] = None
    infos['files_count'] = None
    infos['mime_type'] = None
    infos['file_type'] = None
    infos['programming_language'] = None
    infos['is_binary'] = False
    infos['is_text'] = False
    infos['is_archive'] = False
    infos['is_media'] = False
    infos['is_source'] = False
    infos['is_script'] = False
    return infos


def get_package_infos(location):
    """
    Return a list of mappings of package information collected from the
    `location` or an empty list.
    """
    from packagedcode.recognize import recognize_package
    package = recognize_package(location)
    if not package:
        return []
    return [package.to_dict()]
