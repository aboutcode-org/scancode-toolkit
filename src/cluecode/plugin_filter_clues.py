#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Filter out or ignore, as in "remove" redundant or irrelevant detected clues such as copyrights,
authors, emails, and urls that are already contained in a matched license text or license rule and
treated as ignorable.
"""

from itertools import chain

import attr

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
        logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


@post_scan_impl
class RedundantCluesFilter(PostScanPlugin):
    """
    Filter redundant clues (copyrights, authors, emails, and urls) that are
    already contained in a matched license text.
    """
    run_order = 1
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
        rules_by_id = get_index().rules_by_id

        for resource in codebase.walk():
            filtered = filter_ignorable_resource_clues(resource=resource, rules_by_id=rules_by_id)
            if filtered:
                filtered.save(codebase)


def filter_ignorable_resource_clues(resource, rules_by_id):
    """
    Filter ignorable clues from the ``resource`` Resource object using all the
    scan details attached to that ``resource`` and the ``rules_by_id`` mapping of
    {identifier: license Rule object}. Return the ``resource`` object modified in-
    place if it was modified, or None otherwise.
    """
    detections = Detections.from_resource(resource)
    filtered = filter_ignorable_clues(detections=detections, rules_by_id=rules_by_id)
    logger_debug(f'filter_ignorable_resource_clues: {filtered}')
    if filtered:
        if hasattr(resource, 'emails'):
            resource.emails = filtered.emails
        if hasattr(resource, 'urls'):
            resource.urls = filtered.urls
        if hasattr(resource, 'authors'):
            resource.authors = filtered.authors
        if hasattr(resource, 'holders'):
            resource.holders = filtered.holders
        if hasattr(resource, 'copyrights'):
            resource.copyrights = filtered.copyrights
        return resource


@attr.s(slots=True, frozen=True, eq=True, order=True)
class Ignorable(object):
    # a frozenset of matched line numbers
    lines_range = attr.ib()
    # either a string or a frozenset of strings, such that we can test for `x in value`
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

    license_matches = attr.ib(default=attr.Factory(list))

    # this is the same as author and copyrights, but restructured to be in the
    # same format as ignorables and is used to filter emails and urls in authors
    # and copyright
    copyrights_as_ignorable = attr.ib(default=attr.Factory(list))
    holders_as_ignorable = attr.ib(default=attr.Factory(list))
    authors_as_ignorable = attr.ib(default=attr.Factory(list))

    @staticmethod
    def from_scan_data(data):
        detected_copyrights = data.get('copyrights', [])
        detected_authors = data.get('authors', [])
        detected_holders = data.get('holders', [])
        detected_emails = data.get('emails', [])
        detected_urls = data.get('urls', [])

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

        license_matches = list(
            chain.from_iterable(
                d.get('matches', [])
                for d in data.get('license_detections', {})
            )
        )

        detections = Detections(
            copyrights=detected_copyrights,
            emails=detected_emails,
            urls=detected_urls,
            holders=detected_holders,
            authors=detected_authors,

            copyrights_as_ignorable=copyrights_as_ignorable,
            holders_as_ignorable=holders_as_ignorable,
            authors_as_ignorable=authors_as_ignorable,

            license_matches=license_matches,
        )
        detections.debug()
        return detections

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

    def debug(self):
        if TRACE:
            logger_debug('Detections')
            for nv in self.as_iterable():
                logger_debug('    ', nv),

            logger_debug('     copyrights_as_ignorable:', self.copyrights_as_ignorable)
            logger_debug('     holders_as_ignorable:   ', self.holders_as_ignorable)
            logger_debug('     authors_as_ignorable:   ', self.authors_as_ignorable)
            logger_debug('     license_matches:        ', self.license_matches)


def is_empty(clues):
    if clues:
        return not any([clues.copyrights, clues.holders, clues.authors, clues.urls, clues.emails])
    else:
        # The logic is reversed, so a false or None "clues" object returns None, which
        # is interpreted as False (i.e., the object is *not* empty).
        return True


def filter_ignorable_clues(detections, rules_by_id):
    """
    Filter ignorable clues from the `detections` Detections using the
    `rules_by_id` mapping of {identifier: license Rule object}. Return a new
    filtered Detections object or None if nothing was filtered.
    """
    if is_empty(detections):
        return
    if TRACE:
        logger_debug('filter_ignorable_clues: detections')
        detections.debug()

    no_detected_ignorables = not detections.copyrights and not detections.authors

    ignorables = collect_ignorables(license_matches=detections.license_matches, rules_by_id=rules_by_id)
    no_ignorables = not detections.license_matches or is_empty(ignorables)

    if TRACE:
        logger_debug('ignorables', ignorables)
        # logger_debug('detections', detections)

    if no_ignorables and no_detected_ignorables:
        if TRACE:
            logger_debug('filter_ignorable_clues: NO IGNORABLES')
        return

    # discard redundant emails if ignorable or in a detections copyright or author
    emails = list(filter_values(
        attributes=detections.emails,
        ignorables=ignorables.emails.union(
            detections.copyrights_as_ignorable,
            detections.authors_as_ignorable,
        ),
        value_key='email',
    ))

    # discard redundant urls if ignorable or in a detected copyright or author
    urls = list(filter_values(
        attributes=detections.urls,
        ignorables=ignorables.urls.union(
            detections.copyrights_as_ignorable,
            detections.authors_as_ignorable,
        ),
        value_key='url',
        strip='/',
    ))

    # discard redundant authors if ignorable or in detected holders or copyrights
    authors = list(filter_values(
        attributes=detections.authors,
        ignorables=ignorables.authors.union(
            detections.copyrights_as_ignorable,
            detections.holders_as_ignorable,
        ),
        value_key='author',
    ))

    # discard redundant holders if ignorable
    holders = list(filter_values(
        attributes=detections.holders,
        ignorables=ignorables.holders,
        value_key='holder',
    ))

    # discard redundant copyrights if ignorable
    copyrights = list(filter_values(
        attributes=detections.copyrights,
        ignorables=ignorables.copyrights,
        value_key='copyright',
    ))

    return Detections(
        copyrights=copyrights,
        holders=holders,
        authors=authors,
        urls=urls,
        emails=emails,
    )


def filter_values(attributes, ignorables, value_key='copyright', strip=''):
    """
    Yield filtered ``attributes`` based on line positions and values found in a
    ``ignorables`` Ignorables object. Use the ``value_key`` key for getting the
    value.

    ``attributes`` is a list of mappings that contain a `start_line`, `end_line`
    and a ``value_key`` key as one of: email, url, copyright, holder or author.

    Optionally strip the ``strip`` characters from the values.
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
    Collect and return an Ignorables object built from ``license_matches`` list of license matches
    as returned in ScanCode results license_detection and the ``rules_by_id`` mapping of Rule
    objects by rule identifier.

    The value of each ignorable list of clues is a set of (set of lines number,
    set of ignorable values).
    """
    emails = set()
    urls = set()
    authors = set()
    holders = set()
    copyrights = set()

    if not license_matches:
        if TRACE:
            logger_debug('collect_ignorables: No ignorables!!!!')
        return Ignorables(
            copyrights=frozenset(copyrights),
            holders=frozenset(holders),
            authors=frozenset(authors),
            urls=frozenset(urls),
            emails=frozenset(emails),
        )

    # build tuple of (set of lines number, set of ignorable values)
    for licmat in license_matches:

        if TRACE:
            logger_debug('collect_ignorables: license_match:', licmat['license_expression'], licmat['score'])

        rid = licmat['rule_identifier']
        if not rid:
            # we are missing the license match details, we can only skip
            if TRACE: logger_debug('  collect_ignorables: skipping, no RID')
            continue

        # ignore poor partial matches
        # TODO: there must be a better way using coverage
        match_coverage = float(licmat['match_coverage'])
        if match_coverage < 90:
            if TRACE:
                logger_debug('  collect_ignorables: skipping, match_coverage under 90%')
            continue

        rule = rules_by_id[rid]

        lines_range = frozenset(range(licmat['start_line'], licmat['end_line'] + 1))

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

        if TRACE:
            logger_debug('  collect_ignorables: rule:', rule)

    ignorables = Ignorables(
        copyrights=frozenset(copyrights),
        holders=frozenset(holders),
        authors=frozenset(authors),
        urls=frozenset(urls),
        emails=frozenset(emails),
    )

    if TRACE:
        logger_debug('  collect_ignorables: ignorables:', ignorables)

    return ignorables
