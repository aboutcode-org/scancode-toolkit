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

from itertools import chain

import attr
from six import string_types

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl


def logger_debug(*args):
    pass


TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


@post_scan_impl
class RedundantCluesFilter(PostScanPlugin):
    """
    Filter redundant clues (copyrights, authors, emails, and urls) that are already
    contained in another more important scan result.
    """
    sort_order = 1

    options = [
        PluggableCommandLineOption(('--filter-clues',),
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
            filtered = filter_ignorable_resource_clues(resource, rules_by_id)
            if filtered:
                filtered.save(codebase)


def filter_ignorable_resource_clues(resource, rules_by_id):
    """
    Filter ignorable clues from the `resource` Resource objects using all the
    scan details attached to that `resource` and the `rules_by_id` mapping of
    {identifier: license Rule object}. Return the `resource` object modified in-
    place if it was modified.
    """
    detections = Detections.from_resource(resource)
    filtered = filter_ignorable_clues(detections, rules_by_id)
    if filtered:
        resource.emails = filtered.emails
        resource.urls = filtered.urls
        resource.authors = filtered.authors
        resource.holders = filtered.holders
        resource.copyrights = filtered.copyrights
        return resource


@attr.s(slots=True, frozen=True, eq=True, order=True)
class Ignorable(object):
    # a frozenset of matched line numbers
    lines_range = attr.ib()
    # either a string or a frozenset of strings, such that we can test for `x in
    # value`
    value = attr.ib()


@attr.s(slots=True, frozen=True, eq=True, order=True)
class Ignorables(object):
    copyrights = attr.ib(default=attr.Factory(frozenset))
    holders = attr.ib(default=attr.Factory(frozenset))
    authors = attr.ib(default=attr.Factory(frozenset))
    urls = attr.ib(default=attr.Factory(frozenset))
    emails = attr.ib(default=attr.Factory(frozenset))


@attr.s(slots=True, frozen=True, eq=True, order=True)
class Detections(object):
    copyrights = attr.ib(default=attr.Factory(list))
    holders = attr.ib(default=attr.Factory(list))
    authors = attr.ib(default=attr.Factory(list))
    urls = attr.ib(default=attr.Factory(list))
    emails = attr.ib(default=attr.Factory(list))

    licenses = attr.ib(default=attr.Factory(list))

    # this is the same as author and copyrights, but restructured to be in the
    # same format as ignorables and is used to filter emails and urls in authors
    # and copyright
    copyrights_as_ignorable = attr.ib(default=attr.Factory(list), repr=False)
    holders_as_ignorable = attr.ib(default=attr.Factory(list), repr=False)
    authors_as_ignorable = attr.ib(default=attr.Factory(list), repr=False)

    @staticmethod
    def from_scan_data(data):
        detected_copyrights = data.get('copyrights', [])
        detected_authors = data.get('authors', [])
        detected_holders = data.get('holders', [])

        copyrights_as_ignorable = frozenset(
            Ignorable(
                lines_range=frozenset(range(c['start_line'], c['end_line'] + 1)),
                value=c['copyright']
            )
            for c in detected_copyrights)

        holders_as_ignorable = frozenset(
            Ignorable(
                lines_range=frozenset(range(c['start_line'], c['end_line'] + 1)),
                value=c['holder']
            )
            for c in detected_holders)

        authors_as_ignorable = frozenset(
            Ignorable(
                lines_range=frozenset(range(a['start_line'], a['end_line'] + 1)),
                value=a['author'])
            for a in detected_authors
        )

        return Detections(
            copyrights=detected_copyrights,
            emails=data.get('emails', []),
            urls=data.get('urls', []),
            holders=detected_holders,
            authors=detected_authors,

            authors_as_ignorable=authors_as_ignorable,
            copyrights_as_ignorable=copyrights_as_ignorable,
            holders_as_ignorable=holders_as_ignorable,

            licenses=data.get('licenses', []),
        )

    @staticmethod
    def from_resource(resource):
        return Detections.from_scan_data(resource.to_dict())

    def as_iterable(self):
        """
        Return all the detections chained as a single iterable of tuples (type, value).
        """
        return chain(
            (('copyright', c) for c in self.copyrights),
            (('author', c) for c in self.authors),
            (('holder', c) for c in self.holders),
            (('email', c) for c in self.emails),
            (('url', c) for c in self.urls),
        )


def is_empty(clues):
    if clues:
        return not any([
            clues.copyrights, clues.holders, clues.authors, clues.urls, clues.emails])


def filter_ignorable_clues(detections, rules_by_id):
    """
    Filter ignorable clues from the `detections` Detections using the
    `rules_by_id` mapping of {identifier: license Rule object}. Return a new
    filtered Detections object or None if nothing was filtered.
    """
    if is_empty(detections):
        return

    no_detected_ignorables = not detections.copyrights and not detections.authors

    if detections.licenses:
        ignorables = collect_ignorables(detections.licenses, rules_by_id)
    else:
        ignorables = None

    no_ignorables = not detections.licenses or is_empty(ignorables)

    if TRACE:
        logger_debug('ignorables', ignorables)
        # logger_debug('detections', detections)

    if no_ignorables and no_detected_ignorables:
        return

    # discard redundant emails if ignorable or in a detections copyright or author
    emails = list(filter_values(
        attributes=detections.emails,
        ignorables=ignorables.emails.union(
            detections.copyrights_as_ignorable,
            detections.authors_as_ignorable),
        value_key='email'))

    # discard redundant urls if ignorable or in a detected copyright or author
    urls = list(filter_values(
        attributes=detections.urls,
        ignorables=ignorables.urls.union(
            detections.copyrights_as_ignorable,
            detections.authors_as_ignorable),
        value_key='url', strip='/'))

    # discard redundant authors if ignorable or in detected holders or copyrights
    authors = list(filter_values(
        attributes=detections.authors,
        ignorables=ignorables.authors.union(
            detections.copyrights_as_ignorable,
            detections.holders_as_ignorable),
        value_key='author'))

    # discard redundant holders if ignorable
    holders = list(filter_values(
        attributes=detections.holders,
        ignorables=ignorables.holders,
        value_key='holder'))

    # discard redundant copyrights if ignorable
    copyrights = list(filter_values(
        attributes=detections.copyrights,
        ignorables=ignorables.copyrights,
        value_key='copyright'))

    return Detections(
        copyrights=copyrights,
        holders=holders,
        authors=authors,
        urls=urls,
        emails=emails,
    )


def filter_values(attributes, ignorables, value_key='value', strip=''):
    """
    Yield filtered `attributes` based on line positions and values found in a
    ignorables.

    `attributes` is a list of mappings that contain a `start_line`, `end_line`
    and a `value_key` key.

    Optionally strip `strip` from the the values.
    """
    for item in attributes:
        if TRACE:
            logger_debug('filter_values: item:', item)
        ls = item['start_line']
        el = item['end_line']
        val = item[value_key].strip(strip)
        ignored = False
        if TRACE:
            logger_debug('   filter_values: ignorables:', ignorables)
        for ign in ignorables:
            if TRACE: logger_debug('   filter_values: ign:', ign)
            if (ls in ign.lines_range or el in ign.lines_range) and val in ign.value:
                ignored = True
                if TRACE: logger_debug('   filter_values: skipped')
                break
        if not ignored:
            yield item


def collect_ignorables(license_matches, rules_by_id):
    """
    Collect and return an ignorable Clues object built from `license_matches` matched licenses
    which is the list of "licenses" objects returned in JSON results.

    The value of each ignorable list of clues is a set of (set of
    lines number, set of ignorable values). The return values is a mapping
    {label: ignorables}.
    """
    emails = set()
    urls = set()
    authors = set()
    holders = set()
    copyrights = set()

    # build tuple of (set of lines number, set of ignorbale values)
    for lic in license_matches:

        if TRACE: logger_debug('collect_ignorables: license:', lic['key'], lic['score'])

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

        lines_range = frozenset(range(lic['start_line'], lic['end_line'] + 1))

        ign_copyrights = frozenset(rule.ignorable_copyrights or [])
        if ign_copyrights:
            copyrights.add(Ignorable(lines_range=lines_range, value=ign_copyrights))

        ign_holders = frozenset(rule.ignorable_holders or [])
        if ign_holders:
            holders.add(Ignorable(lines_range=lines_range, value=ign_holders))

        ign_authors = frozenset(rule.ignorable_authors or [])
        if ign_authors:
            authors.add(Ignorable(lines_range=lines_range, value=ign_authors))

        ign_emails = frozenset(rule.ignorable_emails or [])
        if ign_emails:
            emails.add(Ignorable(lines_range=lines_range, value=ign_emails))

        ign_urls = frozenset(r.rstrip('/') for r in (rule.ignorable_urls or []))
        if ign_urls:
            urls.add(Ignorable(lines_range=lines_range, value=ign_urls))

    ignorables = Ignorables(
        copyrights=frozenset(copyrights),
        holders=frozenset(holders),
        authors=frozenset(authors),
        urls=frozenset(urls),
        emails=frozenset(emails),
    )

    if TRACE:
        logger_debug('  collect_ignorables: rule:', rule)
        logger_debug('  collect_ignorables: ignorables:', ignorables)

    return ignorables
