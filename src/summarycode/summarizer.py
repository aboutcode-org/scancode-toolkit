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

from collections import Counter
from collections import OrderedDict

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP
from summarycode.utils import get_resource_summary
from summarycode.utils import set_resource_summary

# Tracing flags
TRACE = False


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

"""
toplevel:
    - license_expression: gpl-2.0
    - license_expressions:
        - count: 1
          value: gpl-2.0

    - copyright_holders:
        - count: 1
          value: RedHat Inc.

facet: core
    - license_expression: (gpl-2.0 or bsd-new) and mit
    - license_expressions:
        - count: 10
          value: gpl-2.0 or bsd-new
        - count: 2
          value: mit

    - programming_language:
        - count: 10
          value: java
        - count: 2
          value: javascript

    - copyright_holders:
        - count: 10
          value: RedHat Inc.
        - count: 2
          value: RedHat Inc.and others.

facet: dev
    - license_expression: gpl-2.0
    - license_expressions:
        - count: 23
          value: gpl-2.0
        - count: 10
          value: none
    - copyright_holders:
        - count: 20
          value: RedHat Inc.
        - count: 10
          value: none

    - programming_languages:
        - count: 34
          value: java
"""


@post_scan_impl
class ScanSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level.
    """
    sort_order = 12

    options = [
        CommandLineOption(('--summary',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary, **kwargs):
        return summary

    def process_codebase(self, codebase, summary, **kwargs):
        summarize_codebase(codebase, keep_details=False, **kwargs)


@post_scan_impl
class ScanSummaryWithDetails(PostScanPlugin):
    """
    Summarize a scan at the codebase level and keep file and directory details.
    """
    # store summaries at the file and directory level in this attribute when
    # keep details is True
    attributes = dict(summary=attr.ib(default=attr.Factory(OrderedDict)))
    sort_order = 13

    options = [
        CommandLineOption(('--summary-with-details',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level, '
                 'keeping intermediate details at the file and directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary_with_details, **kwargs):
        return summary_with_details

    def process_codebase(self, codebase, summary_with_details, **kwargs):
        summarize_codebase(codebase, keep_details=True, **kwargs)


def summarize_codebase(codebase, keep_details, **kwargs):
    """
    Summarize a scan at the codebase level for available scans.

    If `keep_details` is True, also keep file and directory details in the
    `summary` file attribute for every file and directory.
    """
    from summarycode.copyright_summary import author_summarizer
    from summarycode.copyright_summary import copyright_summarizer
    from summarycode.copyright_summary import holder_summarizer

    attrib_summarizers = [
        ('license_expressions', license_summarizer),
        ('copyrights', copyright_summarizer),
        ('holders', holder_summarizer),
        ('authors', author_summarizer),
        ('programming_language', language_summarizer),
    ]

    root = codebase.root
    summarizers = [s for a, s in attrib_summarizers if hasattr(root, a)]
    if TRACE: logger_debug('summarizers:', summarizers)

    # collect and set resource-level summaries
    for resource in codebase.walk(topdown=False):
        children = resource.children(codebase)

        for summarizer in summarizers:
            _summary_data = summarizer(resource, children, keep_details=keep_details)
            if TRACE: logger_debug('summary for:', resource.path, 'after summarizer:', summarizer, 'is:', _summary_data)

        codebase.save_resource(resource)

    # set the summary from the root resource at the codebase level
    if keep_details:
        summary = root.summary
    else:
        summary = root.extra_data.get('summary', {})
    codebase.summary = summary or {}

    if TRACE: logger_debug('codebase summary:', summary)


def license_summarizer(resource, children, keep_details=False):
    """
    Populate a license_expressions list of mappings such as
        {value: "expression", count: "count of occurences"}
    sorted by decreasing count.
    """
    LIC_EXP = 'license_expressions'
    licenses = Counter()

    # Collect current data
    exp = getattr(resource, LIC_EXP  , [])
    if not exp:
        # also count files with no detection
        licenses.update({None: 1})
    else:
        licenses.update(exp)

    # Collect direct children expression summary
    for child in children:
        child_summaries = get_resource_summary(child, LIC_EXP, as_attribute=keep_details)
        for child_summary in child_summaries:
            licenses.update({child_summary['value']:  child_summary['count']})

    summarized = []
    for value, count in licenses.most_common():
        item = OrderedDict([('value', value), ('count', count), ])
        summarized.append(item)

    set_resource_summary(resource, key=LIC_EXP, value=summarized, as_attribute=keep_details)
    return summarized


def language_summarizer(resource, children, keep_details=False):
    """
    Populate a programming_language summary list of mappings such as
        {value: "programming_language", count: "count of occurences"}
    sorted by decreasing count.
    """
    PROG_LANG = 'programming_language'
    languages = Counter()
    exp = getattr(resource, PROG_LANG , [])
    if not exp:
        # also count files with no detection
        languages.update({None: 1})
    else:
        # note: this is abre string, hence why we wrap in a list
        languages.update([exp])

    # Collect direct children expression summaries
    for child in children:
        child_summaries = get_resource_summary(child, PROG_LANG, as_attribute=keep_details)
        for child_summary in child_summaries:
            languages.update({child_summary['value']: child_summary['count']})

    summarized = []
    for value, count in languages.most_common():
        item = OrderedDict([('value', value), ('count', count), ])
        summarized.append(item)

    set_resource_summary(resource, key=PROG_LANG, value=summarized, as_attribute=keep_details)
    return summarized
