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
        from licensedcode.cache import get_index
        if TRACE: logger_debug('RedundantFilter:process_codebase')

        rules_by_id = {r.identifier: r for r in get_index().rules_by_rid}

        for res in codebase.walk():
            # collect ignrable clues from matched licenses if any
            # as lists of (set of lines number, set of ignorable values)
            lic_ignorable_emails = []
            lic_ignorable_urls = []
            lic_ignorable_auths = []
            lic_ignorable_holders = []
            lic_ignorable_copyrights = []

            seenl = set()
            for l in getattr(res, 'licenses', []):
                if TRACE:
                    logger_debug('collecting license match:', l['key'], l['score'])
                # build tuple of (set of lines number, license) from all licenses
                # ignore ppor partial matches
                if l['score'] < 85:
                    if TRACE: logger_debug('  skipping, score too low')
                    continue
                lr = frozenset(range(l['start_line'], l['end_line'] + 1))
                rid = l.get('matched_rule', {}).get('identifier')
                if TRACE: logger_debug('  RID:', rid)
                if not rid:
                    # we are missing the license match details, we can only skip
                    if TRACE: logger_debug('  skipping, no RID')
                    continue
                if (lr, rid) in seenl:
                    if TRACE: logger_debug('  skipping, already seen')
                    continue

                seenl.add((lr, rid))
                rule = rules_by_id[rid]
                if TRACE: logger_debug('  rule:', rule)

                if TRACE: logger_debug('  adding rule.ignorable_copyrights:', rule.ignorable_copyrights)
                if rule.ignorable_copyrights:
                    lic_ignorable_copyrights.append(
                        (lr, frozenset(rule.ignorable_copyrights))
                    )

                if TRACE: logger_debug('  adding rule.ignorable_holders:', rule.ignorable_holders)
                if rule.ignorable_holders:
                    lic_ignorable_holders.append(
                        (lr, frozenset(rule.ignorable_holders))
                    )

                if TRACE: logger_debug('  adding rule.ignorable_authors:', rule.ignorable_authors)
                if rule.ignorable_authors:
                    lic_ignorable_auths.append(
                        (lr, frozenset(rule.ignorable_authors))
                    )

                if TRACE: logger_debug('  adding rule.ignorable_emails:', rule.ignorable_emails)
                if rule.ignorable_emails:
                    lic_ignorable_emails.append(
                        (lr, frozenset(rule.ignorable_emails))
                    )

                if TRACE: logger_debug('  adding rule.ignorable_urls:', rule.ignorable_urls)
                if rule.ignorable_urls:
                    lic_ignorable_urls.append(
                        (lr, frozenset(r.rstrip('/') for r in rule.ignorable_urls))
                    )

            if TRACE:
                logger_debug('lic_ignorable_emails', lic_ignorable_emails)
                logger_debug('lic_ignorable_urls', lic_ignorable_urls)
                logger_debug('lic_ignorable_auths', lic_ignorable_auths)
                logger_debug('lic_ignorable_holders', lic_ignorable_holders)
                logger_debug('lic_ignorable_copyrights', lic_ignorable_copyrights)

            # collect tuple of matched data (set of lines number, value string)
            copy_lines = [
                (
                    frozenset(range(c['start_line'], c['end_line'] + 1)),
                    c['value']
                )
                for c in getattr(res, 'copyrights', [])]
            auth_lines = [
                (
                    frozenset(range(a['start_line'], a['end_line'] + 1)),
                    a['value']
                )
                for a in getattr(res, 'authors', [])]

            if TRACE:
                logger_debug('copy_lines', copy_lines)
                logger_debug('auth_lines', auth_lines)

            cop_auth = copy_lines + auth_lines

            # discard redundant emails
            res.emails = list(filter_values(
                attributes=getattr(res, 'emails' , []),
                ignorables=cop_auth + lic_ignorable_emails,
                attrib='email',
            ))

            # discard redundant urls
            res.urls = list(filter_values(
                attributes=getattr(res, 'urls' , []),
                ignorables=cop_auth + lic_ignorable_urls,
                attrib='url',
                strip='/'
            ))

            # discard redundant authors
            res.authors = list(filter_values(
                attributes=getattr(res, 'authors' , []),
                ignorables=lic_ignorable_auths,
                attrib='value',
            ))

            # discard redundant holders
            res.holders = list(filter_values(
                attributes=getattr(res, 'holders' , []),
                ignorables=lic_ignorable_holders,
                attrib='value',
            ))

            # discard redundant copyrights
            res.copyrights = list(filter_values(
                attributes=getattr(res, 'copyrights' , []),
                ignorables=lic_ignorable_copyrights,
                attrib='value',
            ))

            res.save(codebase)


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
