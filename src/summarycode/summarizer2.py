#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from summarycode.utils import sorted_counter
from summarycode.utils import get_resource_summary
from summarycode.utils import set_resource_summary

# Tracing flags
TRACE = False
TRACE_LIGHT = False


def logger_debug(*args):
    pass


if TRACE or TRACE_LIGHT:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

"""
Create summarized scan data.
"""


@post_scan_impl
class ScanSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level.
    """
    sort_order = 10

    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(dict)))

    options = [
        PluggableCommandLineOption(('--summary2',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary2, **kwargs):
        return summary2

    def process_codebase(self, codebase, summary2, **kwargs):
        if TRACE_LIGHT: logger_debug('ScanSummary:process_codebase')
        summarize_codebase(codebase, keep_details=False, **kwargs)



def summarize_codebase(codebase, keep_details, **kwargs):
    """
    Summarize a scan at the codebase level for available scans.

    If `keep_details` is True, also keep file and directory details in the
    `summary` file attribute for every file and directory.
    """
    from summarycode.copyright_summary import holder_summarizer

    attrib_summarizers = [
        ('license_expressions', license_summarizer),
        ('holders', holder_summarizer),
    ]

    # find which attributes are available for summarization by checking the root
    # resource
    root = codebase.root
    summarizers = [s for a, s in attrib_summarizers if hasattr(root, a)]
    if TRACE: logger_debug('summarize_codebase with summarizers:', summarizers)

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
    codebase.attributes.summary.update(summary)

    if TRACE: logger_debug('codebase summary:', summary)


def license_summarizer(resource, children, keep_details=False):
    """
    Populate a license_expressions list of mappings such as
        {value: "expression", count: "count of occurences"}
    sorted by decreasing count.
    """
    LIC_EXP = 'license_expressions'
    license_expressions = []

    # Collect current data
    lic_expressions = getattr(resource, LIC_EXP  , [])
    if not lic_expressions and resource.is_file:
        # also count files with no detection
        license_expressions.append(None)
    else:
        license_expressions.extend(lic_expressions)

    # Collect direct children expression summary
    for child in children:
        child_summaries = get_resource_summary(child, key=LIC_EXP, as_attribute=keep_details) or []
        for child_summary in child_summaries:
            # TODO: review this: this feels rather weird
            child_sum_val = child_summary.get('value')
            if child_sum_val:
                values = [child_sum_val] * child_summary['count']
                license_expressions.extend(values)

    # summarize proper
    licenses_counter = summarize_licenses(license_expressions)
    summarized = sorted_counter(licenses_counter)
    set_resource_summary(resource, key=LIC_EXP, value=summarized, as_attribute=keep_details)
    return summarized


def summarize_licenses(license_expressions):
    """
    Given a list of license expressions, return a mapping of {expression: count
    of occurences}
    """
    # TODO: we could normalize and/or sort each license_expression before
    # summarization and consider other equivalence or containment checks
    return Counter(license_expressions)
