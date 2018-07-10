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
TRACE_FP = False
TRACE_DEEP = False
TRACE_TEXT = False
TRACE_CANO = False


def logger_debug(*args):
    pass


if TRACE or TRACE_CANO:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))

# TODO: keep the original order of statements as much as possible


@post_scan_impl
class CopyrightSummary(PostScanPlugin):
    """
    Summarize copyrights and holders
    """

    attributes = OrderedDict([
        ('copyrights_summary', attr.ib(default=attr.Factory(list))),
        ('holders_summary', attr.ib(default=attr.Factory(list))),
        ('authors_summary', attr.ib(default=attr.Factory(list))),
    ])

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
        Populate a copyright_summary, holder_summary and author_summary mapping
        each as list of mappings {value: 'xzy', count: 12} at the file and
        directory levels.

        The returned summaries has this form in the JSON results:
        "copyright_summary": [
                {"value": "Copyright (c) 2017 nexB Inc. and others.", "count": 12},
                {"value": "Copyright (c) 2017 You and I.", "count": 11}
            ],
        "holder_summary": [
                {"value": "nexB Inc. and others.", "count": 13},
                {"value": "MyCo Inc. and others.", "count": 13}
            ],
        "author_summary": [
                {"value": "nexB Inc. and others.", "count": 13},
                {"value": "MyCo Inc. and others.", "count": 13}
            ],
        """

        if not copyright_summary:
            return

        def _collect_existing_summary_text_objects(_summaries):
            for _summary in _summaries:
                if TRACE_DEEP:
                    logger_debug('process_codebase:_collect_existing_summaries:', _summary)
                _count = _summary['count']
                _value = _summary['value']
                yield Text(_value, _value, _count)

        for resource in codebase.walk(topdown=False):
            copyrights_summary = []
            holders_summary = []
            authors_summary = []
            try:
                # Collect values from this file/resource if any.
                copyrights_summary = [entry.get('value') for entry in getattr(resource, 'copyrights', [])]
                holders_summary = [entry.get('value', []) for entry in getattr(resource, 'holders', [])]
                authors_summary = [entry.get('value') for entry in getattr(resource, 'authors', [])]

                if TRACE_DEEP:
                    logger_debug('process_codebase:1:from self:copyrights_summary:')
                    for s in copyrights_summary:
                        logger_debug('  ', s)

                    logger_debug('process_codebase:1:from self:holders_summary:')
                    for s in holders_summary:
                        logger_debug('  ', s)

                    logger_debug('process_codebase:1:from self:authors_summary:')
                    for s in authors_summary:
                        logger_debug('  ', s)

                # Collect direct children pre-summarized Texts
                for child in resource.children(codebase):
                    copyrights_summary.extend(
                        _collect_existing_summary_text_objects(child.copyrights_summary))
                    holders_summary.extend(
                        _collect_existing_summary_text_objects(child.holders_summary))
                    authors_summary.extend(
                        _collect_existing_summary_text_objects(child.authors_summary))

                if TRACE_DEEP:
                    logger_debug('process_codebase:2:self+children:copyrights_summary:')
                    for s in copyrights_summary:
                        logger_debug('  ', s)

                    logger_debug('process_codebase:2:self+children:holders_summary:')
                    for s in holders_summary:
                        logger_debug('  ', s)

                    logger_debug('process_codebase:2:self+children:authors_summary:')
                    for s in authors_summary:
                        logger_debug('  ', s)

                # 3. summarize proper and save: expansion, cleaning and deduplication
                resource.copyrights_summary = summarize_copyrights(copyrights_summary, ignore_years=True)
                resource.holders_summary = summarize_holders(holders_summary, expand=False)
                resource.authors_summary = summarize_holders(authors_summary, expand=False)
                codebase.save_resource(resource)

            except Exception as _e:
                msg = 'Failed to create copyrights, authors or holders summary '
                'for resource:\n{}\n'.format(repr(resource))
                msg += 'with copyrights_summary:{}\n'.format(repr(copyrights_summary))
                msg += 'with holders_summary:{}\n'.format(repr(holders_summary))
                msg += 'with authors_summary:{}\n'.format(repr(authors_summary))
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
        if TRACE_TEXT:
            logger_debug('Text.normalize:', self)
        self.key = self.key.lower()
        self.key = ' '.join(self.key.split())
        self.key = self.key.strip('.,').strip()
        self.key = clean(self.key)
        self.key = self.key.strip('.,').strip()

    def transliterate(self):
        self.key = toascii(self.key, translit=True)

    def fingerprint(self):
        if TRACE_TEXT or TRACE_FP:
            logger_debug('Text.fingerprint:key: ', unidecode(self.key))
            logger_debug('Text.fingerprint:fp :    ', fingerprints.generate(unidecode(self.key)))

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


def summarize_copyrights(texts, ignore_years=True, _detector=CopyrightDetector()):
    """
    Return a summarized list of mapping of {value:string, count:int} given a
    list of copyright strings or Text() objects.
    """
    summary_texts = []
    for text in texts:
        # Keep Text objects as-is
        if isinstance(text, Text):
            summary_texts.append(text)
            continue

        if ignore_years:
            # FIXME: redetect to strip year should not be needed!!
            statements_without_years = _detector.detect([(1, text)], copyrights=True,
                holders=False, authors=False, include_years=False)

            for _type, copyr, _start, _end in statements_without_years:
                summary_texts.append(Text(copyr, copyr))
        else:
            summary_texts.append(Text(text, text))

    return summarize(summary_texts)


def summarize_holders(texts, expand=False,):
    """
    Return a summarized list of mapping of {value:string, count:int} given a
    list of holders strings or Text() objects.
    """
    summary_texts = []
    for text in texts:
        # Keep Text objects as-is
        if isinstance(text, Text):
            summary_texts.append(text)
            continue

        if expand:
            for t in itertools.chain.from_iterable(t.expand() for t in text):
                cano = canonical_holder(t)
                summary_texts.append(Text(cano, cano))
        else:
            cano = canonical_holder(text)
            summary_texts.append(Text(cano, cano))

    return summarize(summary_texts)


def summarize(summary_texts):
    """
    Return a summarized list of mapping of {value:string, count:int} given a
    list of Text objects (representing either copyright statements or holders).

    If `expand` is True the texts are further expanded breaking on commad and
    "and" conjunctions.
    """

    if TRACE:
        logger_debug('summarize: INITIAL texts:')
        for s in summary_texts:
            logger_debug('    ', s)

    for text in summary_texts:
        text.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: NORMALIZED 1 texts:')
        for s in summary_texts:
            logger_debug('      ', s)

    texts = list(filter_junk(summary_texts))

    if TRACE_DEEP:
        logger_debug('summarize: DEJUNKED texts:')
        for s in summary_texts:
            logger_debug('        ', s)

    for t in texts:
        t.normalize()

    if TRACE_DEEP:
        logger_debug('summarize: NORMALIZED 2 texts:')
        for s in summary_texts:
            logger_debug('          ', s)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: NON-EMPTY 1 texts:')
        for s in summary_texts:
            logger_debug('            ', s)

    # convert to plain ASCII, then fingerprint
    for t in texts:
        t.transliterate()

    if TRACE_DEEP:
        logger_debug('summarize: ASCII texts:')
        for s in summary_texts:
            logger_debug('              ', s)

    for t in texts:
        t.fingerprint()

    if TRACE_DEEP or TRACE_FP:
        logger_debug('summarize: FINGERPRINTED texts:')
        for s in summary_texts:
            logger_debug('                ', s)

    # keep non-empties
    texts = list(t for t in texts if t.key)

    if TRACE_DEEP:
        logger_debug('summarize: NON-EMPTY 2 texts:')
        for s in summary_texts:
            logger_debug('                  ', s)

    # cluster and sort by decreasing count
    clusters = list(cluster(texts))
    if TRACE_DEEP:
        logger_debug('summarize: CLUSTERS:')
        for c in clusters:
            logger_debug('                    ', c)

    clustered = []

    # TODO: we should sort somehow by text and/or better keep when possible the
    # original relative order and therefore have a stable ordering

    # clusters.sort(key=lambda x: (x[1], x[0]), reverse=True)
    clusters.sort(key=lambda x: x[1], reverse=True)
    for text, count in clusters:
        clustered.append(
            OrderedDict([('value', text.original), ('count', count), ])
        )

    if TRACE:
        logger_debug('summarize: FINAL SUMMARIZED:')
        for c in clustered:
            logger_debug('      ', c)
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
    return text


# set of common prefixes that can be trimmed from a name
prefixes = frozenset([
    'his',
    'by',
    'from',
    'and',
    'of',
    'for',
    '<p>',
])


def strip_prefixes(s, prefixes=prefixes):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped from the left. Normalize and strip spaces.

    For example:
    >>> s = u'by AND for the Free Software Foundation'
    >>> strip_prefixes(s)
    u'the Free Software Foundation'
    """
    s = s.split()
    while s and s[0].lower().strip().strip('.,') in prefixes:
        s = s[1:]
    return u' '.join(s)


# set of suffixes that can be stripped from a name
suffixes = frozenset([
    '(minizip)',
])


def strip_suffixes(s, suffixes=suffixes):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped from the right. Normalize and strip spaces.

    For example:
    >>> s = u'RedHat Inc corp'
    >>> strip_suffixes(s, set(['corp']))
    u'RedHat Inc'
    """
    s = s.split()
    while s and s[-1].lower().strip().strip('.,') in suffixes:
        s = s[:-1]
    return u' '.join(s)


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
    Filter junk from an iterable of texts objects.
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


# mapping of commonly abbreviated names to their expanded, canonical forms.
COMMON_NAMES = {
    '3dfxinteractiveinc.': '3dfx Interactive, Inc.',
    'cern': 'CERN - European Organization for Nuclear Research',
    'ciscosystemsinc': 'Cisco Systems, Inc.',
    'ciscosystems': 'Cisco Systems, Inc.',
    'cisco': 'Cisco Systems, Inc.',
    'daisy': 'Daisy Ltd.',
    'fsf': 'Free Software Foundation, Inc.',
    'freesoftwarefoundation': 'Free Software Foundation, Inc.',
    'thefreesoftwarefoundation': 'Free Software Foundation, Inc.',
    'thefreesoftwarefoundationinc': 'Free Software Foundation, Inc.',
    'freesoftwarefoundationinc': 'Free Software Foundation, Inc.',
    'hp': 'Hewlett-Packard, Inc.',
    'hewlettpackard': 'Hewlett-Packard, Inc.',
    'hewlettpackardco': 'Hewlett-Packard, Inc.',
    'hpcompany': 'Hewlett-Packard, Inc.',
    'hpdevelopmentcompanylp': 'Hewlett-Packard, Inc.',
    'hpdevelopmentcompany': 'Hewlett-Packard, Inc.',
    'hewlettpackardcompany': 'Hewlett-Packard, Inc.',

    'ibm': 'IBM Corporation',
    'redhat': 'Red Hat, Inc.',
    'redhatinc': 'Red Hat, Inc.',
    'softwareinthepublicinterest': 'Software in the Public Interest, Inc.',
    'spiinc': 'Software in the Public Interest, Inc.',
    'suse': 'SuSE, Inc.',
    'suseinc': 'SuSE, Inc.',
    'sunmicrosystems': 'Sun Microsystems, Inc.',
    'sunmicrosystemsinc': 'Sun Microsystems, Inc.',
    'sunmicro': 'Sun Microsystems, Inc.',
    'thaiopensourcesoftwarecenter': 'Thai Open Source Software Center Ltd.',
    'apachefoundation': 'The Apache Software Foundation',
    'apachegroup': 'The Apache Software Foundation',
    'apache': 'The Apache Software Foundation',
    'apachesoftwarefoundation': 'The Apache Software Foundation',
    'theapachegroup': 'The Apache Software Foundation',
    'eclipse': 'The Eclipse Foundation',
    'eclipsefoundation': 'The Eclipse Foundation',
    'regentsoftheuniversityofcalifornia': 'The Regents of the University of California',
    # 'mit': 'the Massachusetts Institute of Technology',
    'borland': 'Borland Corp.',
    'microsoft': 'Microsoft Corp.',
    'microsoftcorp': 'Microsoft Corp.',
    'google': 'Google Inc.',
    'intel': 'Intel Corporation',
}

# Remove everything except letters and numbers
_keep_only_chars = re.compile('[_\W]+', re.UNICODE).sub


def keep_only_chars(s):
    return _keep_only_chars('', s)


def canonical_holder(s):
    """
    Return a canonical holder for string `s` or s.
    """
    key = keep_only_chars(s).lower()
    cano = COMMON_NAMES.get(key)
    if TRACE_CANO:
        logger_debug('cano: for s:', s, 'with key:', key, 'is cano:', cano)
    s = cano or s
    s = strip_suffixes(s)
    return s
