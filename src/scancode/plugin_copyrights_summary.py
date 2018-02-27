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

            # 3. basic expansion, cleaning and deduplication
            for key, items in summary.items():
                if key in ('holders', 'authors'):
                    items = itertools.chain.from_iterable(expand(t) for t in items)
                items = (trim(t) for t in items)
                items = (clean(t) for t in items)
                items = (t for t in items if t)
                items = filter_junk(items)
                items = unique(items)
                summary[key] = list(items)

            resource.copyrights_summary = summary
            codebase.save_resource(resource)


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
    return text and text.strip('.').strip()


def trim(text):
    """
    Return trimmed text
    """
    if text and text.lower().startswith(('the ', 'and ')):
        return text[4:]
    return text


def expand(text):
    """
    Yield expanded items from text.
    """
    if text:
        for item in re.split(' and |,and|,', text):
            yield item


def filter_junk(texts):
    """
    Filter junk from an iterable of texts.
    """
    for text in texts:
        if text and text.lower() in ('inc',):
            continue
        yield text
