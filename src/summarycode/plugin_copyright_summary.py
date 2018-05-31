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

from collections import defaultdict
from collections import OrderedDict
import itertools
from operator import itemgetter
import re

import attr
import fingerprints
from text_unidecode import unidecode

from commoncode.text import toascii
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP

# Tracing flags
TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))


@post_scan_impl
class CopyrightSummary(PostScanPlugin):
    """
    Summarize copyrights and holders
    """

    attributes = dict(copyright_summary=attr.ib(default=attr.Factory(OrderedDict)))

    sort_order = 12

    options = [
        CommandLineOption(('--copyright-summary',),
            is_flag=True, default=False,
            help='Summarize copyrights, holders and authors at the file and '
                 'directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, copyright_summary, **kwargs):  # NOQA
        return copyright_summary

    def process_codebase(self, codebase, copyright_summary, **kwargs):
        """
        Populate a copyrights_summary mapping with three attributes: statements,
        holders and authors; at the file and directory levels.
        The copyrights have this form:
            "copyrights": [
              {
                "statements": [
                  "Copyright (c) 2017 nexB Inc. and others."
                ],
                "holders": [
                  "nexB Inc. and others."
                ],
                "authors": [],
                "start_line": 4,
                "end_line": 4
              }
            ],

        The copyrights_summary has this form:
            "copyright_summary": {
                "statements": [
                    {"value": "Copyright (c) 2017 nexB Inc. and others.", "count": 12}
                ],
                "holders": [
                    {"value": "nexB Inc. and others.", "count": 13}
                ],
                "authors": [],
            },
        """
        keys = 'statements', 'holders', 'authors'
        for resource in codebase.walk(topdown=False):
            if not hasattr(resource, 'copyrights'):
                continue

            summaries = OrderedDict([
                ('statements', []),
                ('holders', []),
                ('authors', []),
            ])

            try:
                # 1. Collect self Texts
                for entry in resource.copyrights:
                    for key in keys:
                        summaries[key].extend(Text(e, e) for e in entry[key])

                if TRACE_DEEP:
                    logger_debug('process_codebase:1:summaries:', summaries)

                # 2. Collect direct children summarized Texts
                for child in resource.children(codebase):
                    for key, key_summaries in child.copyright_summary.items():
                        if TRACE:
                            logger_debug('process_codebase:2:key_summaries:', key_summaries)
                        for key_summary in key_summaries:
                            count = key_summary['count']
                            value = key_summary['value']
                            summaries[key].append(Text(value, value, count))

                if TRACE_DEEP:
                    logger_debug('process_codebase:3:summaries:', summaries)

                # 3. collect any preexisting
                # 3. expansion, cleaning and deduplication
                summarized = summarize(summaries)
                resource.copyright_summary = summarized
                codebase.save_resource(resource)

            except Exception as e:
                msg = 'Failed to create copyright_summary for resource:\n{}\n'.format(repr(resource))
                msg += 'with summaries:{}\n'.format(repr(summaries))
                import traceback
                msg += traceback.format_exc()
                raise Exception(msg)


# keep track of an original text value and the corresponding clustering "key"
@attr.attributes(slots=True)
class Text(object):
    # cleaned, normalized, clustering text for a copyright holder
    key = attr.attrib()
    # original text for a copyright holder
    original = attr.attrib()
    # count of occurences of a text
    count = attr.attrib(default=1)

    def normalize(self):
        if TRACE_DEEP:
            logger_debug('Text.normalize:', self)
        self.key = self.key.lower()
        self.key = ' '.join(self.key.split())
        self.key = self.key.strip('.,').strip()
        self.key = clean(self.key)
        self.key = self.key.strip('.,').strip()
        self.key = trim(self.key)
        self.key = self.key.strip('.,').strip()

    def transliterate(self):
        self.key = toascii(self.key, translit=True)

    def fingerprint(self):
        if TRACE_DEEP:
            logger_debug('fingerprint:', self.key)
            logger_debug('fingerprint:unidecode(self.key):', unidecode(self.key))
            logger_debug('fingerprint:fingerprints.generate(unidecode(self.key)):', fingerprints.generate(unidecode(self.key)))

        self.key = fingerprints.generate(unidecode(self.key))

    def expand(self):
        """
        Yield new expanded items from text such as multiple holders separated by
        an "and" or comma conjunction.
        """
        no_expand = tuple([
            'glyph & cog',
            'bigelow & holmes',
            'reporters & editors',
            'kevin & siji',
            'arts and sciences',
            'science and technology',
            'science and technology.',
            'computer systems and communication',
        ])

        tlow = self.key.lower()
        if tlow.startswith(no_expand) or tlow.endswith(no_expand):
            yield self
        else:
            for expanded in re.split(' [Aa]nd | & |,and|,', self.original):
                yield Text(original=expanded, key=expanded, count=self.count)

    def remove_dates(self):
        """
        Remove dates and date ranges from copyright statement text.
        """
        pass


def summarize(summaries):
    """
    Given a mapping of key -> list of values (either statements, authors or
    holders) return a new summarized mapping.
    """
    summarized = OrderedDict()
    if TRACE:
        logger_debug('')
        logger_debug('SUMMARIZE')

    for key, texts in summaries.items():

        if key in ('holders', 'authors'):
            texts = list(itertools.chain.from_iterable(t.expand() for t in texts))

        if TRACE_DEEP:
            logger_debug('\n\nsummarize: texts: for:', key)
            for t in texts:
                logger_debug(t)

        for t in texts:
            t.normalize()

        if TRACE_DEEP:
            logger_debug('summarize: texts2:')
            for t in texts:
                logger_debug(t)

        texts = list(filter_junk(texts))

        if TRACE_DEEP:
            logger_debug('summarize: texts3:')
            for t in texts:
                logger_debug(t)

        for t in texts:
            t.normalize()

        if TRACE_DEEP:
            logger_debug('summarize: texts4:')
            for t in texts:
                logger_debug(t)

        # keep non-empties
        texts = list(t for t in texts if t.key)

        if TRACE_DEEP:
            logger_debug('summarize: texts5:')
            for t in texts:
                logger_debug(t)

        # convert to plain ASCII, then fingerprint
        for t in texts:
            t.transliterate()

        if TRACE_DEEP:
            logger_debug('summarize: texts6:')
            for t in texts:
                logger_debug(t)

        for t in texts:
            t.fingerprint()

        if TRACE_DEEP:
            logger_debug('summarize: texts7:')
            for t in texts:
                logger_debug(t)

        # keep non-empties
        texts = list(t for t in texts if t.key)

        if TRACE_DEEP:
            logger_debug('summarize: texts8:')
            for t in texts:
                logger_debug(t)

        key_summaries = []
        summarized[key] = key_summaries
        # cluster and sort by biggets count
        clusters = list(cluster(texts))
        if TRACE_DEEP:
            logger_debug('summarize: texts9:')
            for t in texts:
                logger_debug(' ', t)

            logger_debug('\n\nsummarize: clusters:')
            for c in clusters:
                logger_debug(' ', c)

        clusters.sort(key=itemgetter(1), reverse=True)
        for text, count in clusters:
            clustered = OrderedDict([
                ('value', text.original),
                ('count', count),
            ])
            key_summaries.append(clustered)

        if TRACE_DEEP:
            logger_debug('summarize: texts10')
            for t in texts:
                logger_debug(t)

    if TRACE:
        logger_debug('summarize:summarized:', summarized)
    return summarized


def cluster(texts):
    """
    Given an iterable of text objects, group these objects when they have the
    same key. Yield a text and a count of its occurences sorted from most
    frequent to least frequent.
    """
    clusters = defaultdict(list)
    for text in texts:
        clusters[text.key].append(text)

    # Find the representative value for each cluster e.g. the longest
    for cluster_key, cluster_texts in clusters.items():
        try:
            cluster_texts.sort(key=lambda x:-len(x.key))
            representative = cluster_texts[0]
            count = sum(t.count for t in cluster_texts)
            if TRACE_DEEP:
                logger_debug('cluster: representative, count', representative, count)
            yield representative, count
        except Exception as e:
            msg = ('Error in cluster(): cluster_key: %(cluster_key)r, cluster_texts: %(cluster_texts)r\n' % locals())
            import traceback
            msg += traceback.format_exc()
            raise Exception(msg)


def clean(text):
    """
    Return an updated and cleaned Text object from a `text` Text object
    normalizing some pucntuations around some name and acronyms.
    """
    if not text:
        return text
    text = text.replace('A. M.', 'A.M.')
    text = text.replace(', Inc', ' Inc')
    text = text.replace(' Inc.', ' Inc, ')
    text = text.replace(', Corp', ' Corp')
    text = text.replace('Company, ', 'Company ')
    text = text.replace(', Ltd', ' Ltd')
    text = text.replace(', LTD', ' LTD')
    text = text.replace(', S.L', ' S.L')
    text = text.replace(' Co ', ' Co , ')
    text = text.replace(' Co. ', ' Co , ')
    return text


# set of common prefixes that can be trimmed from a name
prefixes = frozenset([
    'his',
    'by',
    'from',
    'and',
    'of',
    'the',
    'for',
    '<p>',
])


def strip_prefixes(s, prefixes=prefixes):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped from the left. Normalize and strip spaces.

    For example:
    >>> s = u'the Free Software Foundation'
    >>> strip_prefixes(s)
    u'Free Software Foundation'
    """
    s = s.split()
    while s and s[0].lower().strip().strip('.,') in prefixes:
        s = s[1:]
    return u' '.join(s)


# set of common coprp suffixes that can be trimmed from a name
suffixes = frozenset([
    'inc',
    'incorporated',
    'co',
    'corp',
    'corporation',
    'ltd',
    'limited',
    'llc',
])


def strip_suffixes(s, suffixes=suffixes):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped from the right. Normalize and strip spaces.

    For example:
    >>> s = u'RedHat Inc corp'
    >>> strip_suffixes(s)
    u'RedHat'
    """
    s = s.split()
    while s and s[-1].lower().strip().strip('.,') in suffixes:
        s = s[:-1]
    return u' '.join(s)


def trim(text, prefixes=prefixes, suffixes=suffixes):
    """
    Return trimmed text removing leading and trailing junk.
    """
    if text:
        text = strip_prefixes(text, prefixes)
    if text:
        text = strip_suffixes(text, suffixes)
    return text


# TODO: we need a gazeteer of places and or use usaddress and probablepeople or
# refine the POS tagging to catch these better
JUNK_HOLDERS = frozenset([
    'advanced computing',
    'inc',
    'llc',
    'ltd',
    'berlin',
    'munich',
    'massachusetts',
    'maynard',
    'cambridge',
    'norway',
    'and',
    'is',
    'a',
    'cedar rapids',
    'iowa',
    'u.s.a',
    'u.s.a.',
    'usa',
    'source code',
    'mountain view',
    'england',
    'web applications',
    'menlo park',
    'california',
    'irvine',
    'pune',
    'india',
    'stockholm',
    'sweden',
    'sweden)',
    'software',
    'france',
    'concord',
    'date here',
    'software',
    'not',
])


def filter_junk(texts):
    """
    Filter junk from an iterable of texts.
    """
    for text in texts:
        if not text.key:
            continue
        if text.key.lower() in JUNK_HOLDERS:
            continue
        if text.key.isdigit():
            continue
        if len(text.key) == 1:
            continue
        yield text
