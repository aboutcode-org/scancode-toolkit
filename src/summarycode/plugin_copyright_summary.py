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
from cluecode.copyrights import CopyrightDetector

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

    attributes = OrderedDict([
        ('copyrights_summary', attr.ib(default=attr.Factory(list))),
        ('holders_summary', attr.ib(default=attr.Factory(list))),
    ])

    sort_order = 12

    options = [
        CommandLineOption(('--copyrights-summary',),
            is_flag=True, default=False,
            help='Summarize copyrights and holders at the file and '
                 'directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, copyrights_summary, **kwargs):  # NOQA
        return copyrights_summary

    def process_codebase(self, codebase, copyrights_summary, **kwargs):
        """
        Populate a copyrights_summary  and holders_summary mapping each as list of
        mappings {value: 'xzy', count: 12} at the file and directory levels.

        The returned summaries has this form in the JSON results:
        "copyrights_summary": [
                {"value": "Copyright (c) 2017 nexB Inc. and others.", "count": 12},
                {"value": "Copyright (c) 2017 You and I.", "count": 11}
            ],
        "holders_summary": [
                {"value": "nexB Inc. and others.", "count": 13},
                {"value": "MyCo Inc. and others.", "count": 13}
            ],
        """
        detector = CopyrightDetector()

        def _collect_existing_summary_text_objects(_summaries):
            for _summary in _summaries:
                if TRACE_DEEP:
                    logger_debug('process_codebase:_collect_existing_summaries:', _summary)
                _count = _summary['count']
                _value = _summary['value']
                yield Text(_value, _value, _count)

        for resource in codebase.walk(topdown=False):
            if not hasattr(resource, 'copyrights'):
                continue
            copyrights_summary = []
            holders_summary = []
            try:
                # 1. Collect statements and holders from this file/resource if any.

                resource_copyrights = resource.copyrights

                statements = (entry.get('statements', []) for entry in resource_copyrights)
                for statem in itertools.chain.from_iterable(statements):
                    # FIXME: redetect to strip year should not be needed!!
                    lines =[(1, statem)]
                    statements_with_years = detector.detect2(lines, copyrights=True, 
                        holders=False, authors=False, include_years=False)
                    for _type, copyr, _start, _end in statements_with_years: 
                        copyrights_summary.append(Text(copyr, copyr))
                        if TRACE:
                            logger_debug('########################process_codebase:statement:', statem)
                            logger_debug('########################process_codebase:statement no year:', copyr)

                holders = (entry.get('holders', []) for entry in resource_copyrights)
                for hold in itertools.chain.from_iterable(holders):
                    holders_summary.append(Text(hold, hold))

                if TRACE_DEEP:
                    logger_debug('process_codebase:1:from self:copyrights_summary:', copyrights_summary)
                    logger_debug('process_codebase:1:from self:holders_summary:', holders_summary)

                # 2. Collect direct children summarized Texts
                for child in resource.children(codebase):
                    copyrights_summary.extend(_collect_existing_summary_text_objects(child.copyrights_summary))
                    holders_summary.extend(_collect_existing_summary_text_objects(child.holders_summary))

                if TRACE_DEEP:
                    logger_debug('process_codebase:3:self+children:copyrights_summary:', copyrights_summary)
                    logger_debug('process_codebase:3:self+children:holders_summary:', holders_summary)

                # 3. summarize proper and save: expansion, cleaning and deduplication
                summarized_copyright = summarize(copyrights_summary)
                summarized_holder = summarize(holders_summary, expand=True)
                resource.copyrights_summary = summarized_copyright
                resource.holders_summary = summarized_holder
                codebase.save_resource(resource)

            except Exception as _e:
                msg = 'Failed to create copyrights_summary or holders_summary for resource:\n{}\n'.format(repr(resource))
                msg += 'with copyrights_summary:{}\n'.format(repr(copyrights_summary))
                msg += 'with holders_summary:{}\n'.format(repr(holders_summary))
                import traceback
                msg += traceback.format_exc()
                raise Exception(msg)


def summarize_strings(srtings):
    pass


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
            logger_debug('Text.fingerprint:', self.key)
            logger_debug('Text.fingerprint:unidecode(self.key):', unidecode(self.key))
            logger_debug('Text.fingerprint:fingerprints.generate(unidecode(self.key)):', fingerprints.generate(unidecode(self.key)))

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
            'search and networking',
        ])

        tlow = self.key.lower()
        if tlow.startswith(no_expand) or tlow.endswith(no_expand):
            yield self
        else:
            for expanded in re.split(' [Aa]nd | & |,and|,', self.original):
                expanded = expanded.strip()
                yield Text(original=expanded, key=expanded, count=self.count)

    def remove_dates(self):
        """
        Remove dates and date ranges from copyright statement text.
        """
        pass


def summarize(summary_texts, expand=False):
    """
    Return a summarized list of mapping of {value:string, count:int} given a list of
    Text objects (representing either copyright statements or holders).

    If `expand` is True the texts are further expanded breaking on commad and
    "and" conjunctions.
    """

    if TRACE:
        logger_debug('summarize: summary_texts:', summary_texts)

    if expand:
        summary_texts = list(itertools.chain.from_iterable(t.expand() for t in summary_texts))

    if TRACE:
        logger_debug('summarize')

    if TRACE_DEEP:
        logger_debug('\n\nsummarize: texts1:')
        for t in summary_texts: logger_debug(t)

    for text in summary_texts:
        text.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: texts2:')
        for t in summary_texts: logger_debug(t)

    texts = list(filter_junk(summary_texts))

    if TRACE_DEEP:
        logger_debug('summarize: texts3:')
        for t in texts: logger_debug(t)

    for t in texts:
        t.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: texts4:')
        for t in texts: logger_debug(t)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: texts5:')
        for t in texts: logger_debug(t)

    # convert to plain ASCII, then fingerprint
    for t in texts:
        t.transliterate()

    if TRACE_DEEP:
        logger_debug('summarize: texts6:')
        for t in texts: logger_debug(t)

    for t in texts:
        t.fingerprint()

    if TRACE_DEEP:
        logger_debug('summarize: texts7:')
        for t in texts: logger_debug(t)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: texts8:')
        for t in texts: logger_debug(t)

    # cluster and sort by decreasing count
    clusters = list(cluster(texts))
    if TRACE_DEEP:
        logger_debug('\n\nsummarize: clusters:')
        for c in clusters:
            logger_debug(' ', c)

    clustered = []
    clusters.sort(key=itemgetter(1), reverse=True)
    for text, count in clusters:
        clustered.append(
            OrderedDict([('value', text.original), ('count', count), ])
        )

    if TRACE:
        logger_debug('summarize:summarized:', clustered)
    return clustered


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


# set of common corp suffixes that can be trimmed from a name
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
