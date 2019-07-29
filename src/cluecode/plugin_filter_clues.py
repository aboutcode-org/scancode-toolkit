#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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


from commoncode import compat
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


def logger_debug(*args):
    pass


TRACE = True

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        logger.debug(' '.join(isinstance(a, compat.string_types) and a or repr(a) for a in args))


@post_scan_impl
class RedundantCluesFilter(PostScanPlugin):
    """
    Filter redundant clues (copyrights, authors, emails, and urls) that are already
    contained in another more important scan result.
    """
    sort_order = 1

    options = [
        CommandLineOption(('--filter-clues',),
            is_flag=True, default=False,
            help='Filter redundant duplicated clues already contained in '
                 'detected license and copyright texts and notices.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, filter_clues, **kwargs):
        return filter_clues

    def process_codebase(self, codebase, **kwargs):
        """
        Update detected clues to remove redundant clues already found in another
        detected clue for all the resources of codebase.
        """
        if TRACE: logger_debug('RedundantFilter:process_codebase')

        from licensedcode.cache import get_index

        rules_by_id = {r.identifier: r for r in get_index().rules_by_rid}

        for resource in codebase.walk():
            resource = filter_ignorables(resource, rules_by_id)
            resource.save(codebase)


def filter_ignorables(resource, rules_by_id):
    """
    Filter ignorable clues from the `resource` Resource objects using all
    the scan details attached to that `resource` and the `rules_by_id`
    mapping of {identifier: license Rule object}. Retune the modified
    resouce. Update is in-place.
    """

    iemails, iurls, iauths, iholders, icopyrights = collect_ignorables(resource, rules_by_id)

    detected_copyrights = getattr(resource, 'copyrights', [])
    detected_emails = getattr(resource, 'emails', [])
    detected_urls = getattr(resource, 'urls', [])
    detected_holders = getattr(resource, 'holders', [])
    detected_authors = getattr(resource, 'authors', [])

    idetected_copyrights = [
        (frozenset(range(c['start_line'], c['end_line'] + 1)), c['value'])
            for c in detected_copyrights]
    idetected_authors = [
        (frozenset(range(a['start_line'], a['end_line'] + 1)), a['value'])
            for a in detected_authors]

    if TRACE:
        logger_debug('iemails', iemails)
        logger_debug('iurls', iurls)
        logger_debug('iauths', iauths)
        logger_debug('iholders', iholders)
        logger_debug('icopyrights', icopyrights)
        logger_debug('idetected_copyrights', idetected_copyrights)
        logger_debug('idetected_authors', idetected_authors)

    # discard redundant emails if ignorable or in a detected copyright or author
    resource.emails = list(filter_values(attributes=detected_emails,
            ignorables=idetected_copyrights + idetected_authors + iemails,
            attrib='email'))

    # discard redundant urls if ignorable or in a detected copyright or author
    resource.urls = list(filter_values(attributes=detected_urls,
            ignorables=idetected_copyrights + idetected_authors + iurls,
            attrib='url', strip='/'))

    # discard redundant authors if ignorable or in a detected copyright
    resource.authors = list(filter_values(attributes=detected_authors,
            ignorables=idetected_copyrights + iauths,
            attrib='value'))

    # discard redundant holders if ignorable
    resource.holders = list(filter_values(attributes=detected_holders,
            ignorables=iholders,
            attrib='value'))

    # discard redundant copyrights if ignorable
    resource.copyrights = list(filter_values(attributes=detected_copyrights,
            ignorables=icopyrights,
            attrib='value'))

    return resource


def filter_values(attributes, ignorables, attrib='value', strip=''):
    """
    Yield filtered `attributes` based on line positions and values found in
    ignorables.
    """
    for item in attributes:
        if TRACE:
            logger_debug('filter_values: item:', item)
        ls = item['start_line']
        el = item['end_line']
        val = item[attrib].strip(strip)
        ignored = False
        for lines, value in ignorables:
            if (ls in lines or el in lines) and val in value:
                ignored = True
                if TRACE: logger_debug('   filter_values: skipped')
                break
        if not ignored:
            yield item


def collect_ignorables(resource, rules_by_id):
    """
    Collect and return ignorable clues from matched licenses in the Resource
    `resource`. Each ignorable emails, urls, authors, holders, copyrights is
    a set of (set of lines number, set of ignorable values)
    """
    emails = set()
    urls = set()
    authors = set()
    holders = set()
    copyrights = set()

    # build tuple of (set of lines number, set of ignorbale values)
    for lic in getattr(resource, 'licenses', []):

        if TRACE: logger_debug('collect_ignorables: license:', lic['key'], lic['score'])
        lines_range = frozenset(range(lic['start_line'], lic['end_line'] + 1))
        matched_rule = lic.get('matched_rule', {})
        rid = matched_rule.get('identifier')
        match_coverage = matched_rule.get('match_coverage', 0)

        # ignore poor partial matches
        # TODO: there must be a better way using coverage
        if match_coverage < 90:
            if TRACE: logger_debug('  collect_ignorables: skipping, match_coverage under 90%')
            continue

        if not rid:
            # we are missing the license match details, we can only skip
            if TRACE: logger_debug('  collect_ignorables: skipping, no RID')
            continue

        rule = rules_by_id[rid]
        ign_copyrights = rule.ignorable_copyrights
        ign_holders = rule.ignorable_holders
        ign_authors = rule.ignorable_authors
        ign_emails = rule.ignorable_emails
        ign_urls = rule.ignorable_urls

        if ign_copyrights:
            copyrights.add((lines_range, frozenset(ign_copyrights)))
        if ign_holders:
            holders.add((lines_range, frozenset(ign_holders)))
        if ign_authors:
            authors.add((lines_range, frozenset(ign_authors)))
        if ign_emails:
            emails.add((lines_range, frozenset(ign_emails)))
        if ign_urls:
            urls.add((lines_range, frozenset(r.rstrip('/') for r in ign_urls)))

        if TRACE:
            logger_debug('  collect_ignorables: rule:', rule)
            logger_debug('  collect_ignorables: adding rule.ignorable_copyrights:', ign_copyrights)
            logger_debug('  collect_ignorables: adding rule.ignorable_holders:', ign_holders)
            logger_debug('  collect_ignorables: adding rule.ignorable_authors:', ign_authors)
            logger_debug('  collect_ignorables: adding rule.ignorable_emails:', ign_emails)
            logger_debug('  collect_ignorables: adding rule.ignorable_urls:', ign_urls)

    return emails, urls, authors, holders, copyrights
