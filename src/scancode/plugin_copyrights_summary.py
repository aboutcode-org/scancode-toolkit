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


@post_scan_impl
class CopyrightSummary(PostScanPlugin):
    """
    Set the "is_source" flag to true for directories that contain
    over 90% of source files as direct children.
    Has no effect unless the --info scan is requested.
    """

    attributes = dict(copyrights_summary=attr.ib(default=attr.Factory(OrderedDict)))

    sort_order = 9

    options = [
        CommandLineOption(('--copyrights-summary',),
            is_flag=True, default=False,
            requires=['copyright'],
            help='Summarize copyrights, holders and authors at the file and '
                 'directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, copyrights_summary, copyright, **kwargs):  # NOQA
        return copyrights_summary and copyright

    def process_codebase(self, codebase, copyrights_summary, **kwargs):
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

        The copyrights_summary hast his form:
            "copyrights": {
                "statements": [
                  "Copyright (c) 2017 nexB Inc. and others."
                ],
                "holders": [
                  "nexB Inc. and others."
                ],
                "authors": [],
            },
        """
        keys = 'statements', 'holders', 'authors'
        for resource in codebase.walk(topdown=False):
            summary = OrderedDict([
                ('statements', []),
                ('holders', []),
                ('authors', []),
            ])
            # 1. Collect self data
            for entry in resource.copyrights:
                for key in keys:
                    summary[key].extend(entry[key])

            # 2. Collect direct children data
            for child in resource.children(codebase):
                child_summary = child.copyrights_summary
                for key in keys:
                    summary[key].extend(child_summary[key])

            # 3. expansion, cleaning and deduplication
            summarized = summarize(summary)

            resource.copyrights_summary = summarized
            codebase.save_resource(resource)


def summarize(summary):
    """
    Given a mapping of key -> list of values (either statements, authors or
    holders) return a new summarzied mapping.
    """
    summarized = OrderedDict()
    for key, items in summary.items():
        if key in ('holders', 'authors'):
            items = (clean(t) for t in items)
            items = (trim(t) for t in items)
            items = itertools.chain.from_iterable(expand(t) for t in items)
            items = (trim(t) for t in items)

        items = (' '.join(t.split()) for t in items if t and t.strip())
        items = (t.strip().strip('.,') for t in items)
        items = filter_junk(items)
        items = (t.strip().strip('.,') for t in items)
        items = (' '.join(t.split()) for t in items if t and t.strip())
        items = (t for t in items if t)

        items = (transliterate(t) for t in items)
        items = cluster(items)
        items = unique(items)
        summarized[key] = list(items)
    return summarized


def cluster(texts):
    """
    Give an iterable of texts, cluster texts and return an iterable keeping the
    string with the largest length in a cluster.
    """
    fings = OrderedDict()
    for text in texts:
        text = unidecode(text)
        fp = fingerprints.generate(text)
        if fp in fings:
            fings[fp].append(text)
        else:
            fings[fp] = [text]

    for cluster in fings.values():
        longest = sorted(cluster, key=len)[-1]
        yield longest


def unique(iterable):
    """
    Yield unique hashable items in `iterable` keeping their original order.
    """
    uniques = set()
    for item in iterable:
        if item and item not in uniques:
            uniques.add(item)
            yield item


def clean(text):
    """
    Return cleaned text.
    """
    if not text:
        return text
    text = text.strip('.,').strip()
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
    return text.strip('.,').strip()


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


def strip_prefixes(s, prefixes):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped from the left. Normalize and strip spaces.
    """
    s = s.split()
    while s and s[0].lower().strip().strip('.,') in prefixes:
        s = s[1:]
    return u' '.join(s)


suffixes = frozenset([
    'inc',
    'corp',
    'co',
    'ltd',
    'corporation',
    'limited',
    'incorporated',
    'llc',
])


def strip_suffixes(s, suffixes=suffixes):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped from the right. Normalize and strip spaces.
    """
    s = s.split()
    while s and s[-1].lower().strip().strip('.,') in suffixes:
        s = s[:-1]
    return u' '.join(s)


def trim(text):
    """
    Return trimmed text removing leading and trailing junk.
    """
    if text:
        text = strip_prefixes(text, prefixes)
    if text:
        text = strip_suffixes(text, suffixes)
    return text


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


def expand(text):
    """
    Yield expanded items from text.
    """
    if text:
        tlow = text.lower()
        if tlow.startswith(no_expand) or tlow.endswith(no_expand):
            yield text
        else:
            for item in re.split(' [Aa]nd | & |,and|,', text):
                yield item


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
        if text:
            if text.lower() in JUNK_HOLDERS:
                continue
            if text.isdigit():
                continue
            if len(text) == 1:
                continue
            yield text


def transliterate(text):
    return toascii(text, translit=True)
