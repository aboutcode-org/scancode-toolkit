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
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))

"""
top_level:
    - license_expressions:
        - count: 1
          value: gpl-2.0
    - holders:
        - count: 1
          value: RedHat Inc.

by_facet:
    facet: core
        - license_expressions:
            - count: 10
              value: gpl-2.0 or bsd-new
            - count: 2
              value: mit
        - programming_language:
            - count: 10
              value: java
        - holders:
            - count: 10
              value: RedHat Inc.
    facet: dev
        - license_expressions:
            - count: 23
              value: gpl-2.0
        - holders:
            - count: 20
              value: RedHat Inc.
            - count: 10
              value: none
        - programming_languages:
            - count: 34
              value: java
all:
    - license_expressions:
        - count: 10
          value: gpl-2.0 or bsd-new
    - programming_language:
        - count: 10
          value: java
    - holders:
        - count: 10
          value: RedHat Inc.
"""


@post_scan_impl
class ScanSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level.
    """
    sort_order = 10
    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(OrderedDict)))

    options = [
        CommandLineOption(('--summary',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary, **kwargs):
        return summary

    def process_codebase(self, codebase, summary, **kwargs):
        if TRACE_LIGHT: logger_debug('ScanSummary:process_codebase')
        summarize_codebase(codebase, keep_details=False, **kwargs)


@post_scan_impl
class ScanSummaryWithDetails(PostScanPlugin):
    """
    Summarize a scan at the codebase level and keep file and directory details.
    """
    # mapping of summary data at the codebase level for the whole codebase
    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(OrderedDict)))
    # store summaries at the file and directory level in this attribute when
    # keep details is True
    resource_attributes = dict(summary=attr.ib(default=attr.Factory(OrderedDict)))
    sort_order = 100

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
            values = [child_summary['value']] * child_summary['count']
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


def language_summarizer(resource, children, keep_details=False):
    """
    Populate a programming_language summary list of mappings such as
        {value: "programming_language", count: "count of occurences"}
    sorted by decreasing count.
    """
    PROG_LANG = 'programming_language'
    languages = []
    prog_lang = getattr(resource, PROG_LANG , [])
    if not prog_lang:
        if resource.is_file:
            # also count files with no detection
            languages.append(None)
    else:
        languages.append(prog_lang)

    # Collect direct children expression summaries
    for child in children:
        child_summaries = get_resource_summary(child, key=PROG_LANG, as_attribute=keep_details) or []
        for child_summary in child_summaries:
            values = [child_summary['value']] * child_summary['count']
            languages.extend(values)

    # summarize proper
    languages_counter = summarize_languages(languages)
    summarized = sorted_counter(languages_counter)
    set_resource_summary(resource, key=PROG_LANG, value=summarized, as_attribute=keep_details)
    return summarized


def summarize_languages(languages):
    """
    Given a list of languages, return a mapping of {language: count
    of occurences}
    """
    # TODO: consider aggregating related langauges (C/C++, etc)
    return Counter(languages)


def summarize_values(values, attribute):
    """
    Given a list of `values` for a given `attribute`, return a mapping of
    {value: count of occurences} using a summarization specific to the attribute.
    """
    from summarycode.copyright_summary import summarize_holders
    from summarycode.copyright_summary import summarize_copyrights

    value_summarizers_by_attr = dict(
        license_expressions=summarize_licenses,
        copyrights=summarize_copyrights,
        holders=summarize_holders,
        authors=summarize_holders,
        programming_language=summarize_languages,
    )
    return value_summarizers_by_attr[attribute](values)


@post_scan_impl
class ScanKeyFilesSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level for only key files.
    """
    sort_order = 150

    # mapping of summary data at the codebase level for key files
    codebase_attributes = dict(summary_of_key_files=attr.ib(default=attr.Factory(OrderedDict)))

    options = [
        CommandLineOption(('--summary-key-files',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans for key, '
                 'top-level files. Key files are top-level codebase files such '
                 'as COPYING, README and package manifests as reported by the '
                 '--classify option "is_legal", "is_readme", "is_manifest" '
                 'and "is_top_level" flags.',
            help_group=POST_SCAN_GROUP,
            requires=['classify', 'summary']
            )
    ]

    def is_enabled(self, summary_key_files, **kwargs):
        return summary_key_files

    def process_codebase(self, codebase, summary_key_files, **kwargs):
        summarize_codebase_key_files(codebase, **kwargs)


def summarize_codebase_key_files(codebase, **kwargs):
    """
    Summarize codebase key files.
    """
    summarizable_attributes = codebase.attributes.summary.keys()
    if TRACE: logger_debug('summarizable_attributes:', summarizable_attributes)

    # create one counter for each summarized attribute
    summarizable_values_by_key = OrderedDict([(key, []) for key in summarizable_attributes])

    # filter to get only key files
    key_files = (res for res in codebase.walk(topdown=True)
                 if (res.is_file and res.is_top_level
                     and (res.is_readme or res.is_legal or res.is_manifest)))

    for resource in key_files:
        for key, values in summarizable_values_by_key.items():
            # note we assume things are stored as extra-data, not as direct
            # Resource attributes
            res_summaries = get_resource_summary(resource, key=key, as_attribute=False) or []
            for summary in res_summaries:
                # each summary is a mapping with value/count: we transform back to values
                values.extend([summary['value']] * summary['count'])

    summary_counters = []
    for key, values in summarizable_values_by_key.items():
        summarized = summarize_values(values, key)
        summary_counters.append((key, summarized))

    sorted_summaries = OrderedDict(
        [(key, sorted_counter(counter)) for key, counter in summary_counters])

    codebase.attributes.summary_of_key_files = sorted_summaries

    if TRACE: logger_debug('codebase summary_of_key_files:', sorted_summaries)


@post_scan_impl
class ScanByFacetSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level groupping by facets.
    """
    sort_order = 200
    codebase_attributes = dict(summary_by_facet=attr.ib(default=attr.Factory(list)))

    options = [
        CommandLineOption(('--summary-by-facet',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans and group the '
                 'results by facet.',
            help_group=POST_SCAN_GROUP,
            requires=['facet', 'summary']
        )
    ]

    def is_enabled(self, summary_by_facet, **kwargs):
        return summary_by_facet

    def process_codebase(self, codebase, summary_by_facet, **kwargs):
        if TRACE_LIGHT: logger_debug('ScanByFacetSummary:process_codebase')
        summarize_codebase_by_facet(codebase, **kwargs)


def summarize_codebase_by_facet(codebase, **kwargs):
    """
    Summarize codebase by facte.
    """
    from summarycode import facet as facet_module

    summarizable_attributes = codebase.attributes.summary.keys()
    if TRACE:
        logger_debug('summarize_codebase_by_facet for attributes:', summarizable_attributes)

    # create one group of by-facet values lists for each summarized attribute
    summarizable_values_by_key_by_facet = OrderedDict([
        (facet, OrderedDict([(key, []) for key in summarizable_attributes]))
        for facet in facet_module.FACETS
    ])

    for resource in codebase.walk(topdown=True):
        if not resource.is_file:
            continue

        for facet in resource.facets:
            # note: this will fail loudly if the facet is not a known one
            values_by_attribute = summarizable_values_by_key_by_facet[facet]
            for key, values in values_by_attribute.items():
                # note we assume things are stored as extra-data, not as direct
                # Resource attributes
                res_summaries = get_resource_summary(resource, key=key, as_attribute=False) or []
                for summary in res_summaries:
                    # each summary is a mapping with value/count: we transform back to discrete values
                    values.extend([summary['value']] * summary['count'])

    final_summaries = []
    for facet, summarizable_values_by_key in summarizable_values_by_key_by_facet.items():
        summary_counters = (
            (key, summarize_values(values, key))
            for key, values in summarizable_values_by_key.items()
        )

        sorted_summaries = OrderedDict(
            [(key, sorted_counter(counter)) for key, counter in summary_counters])

        facet_summary = OrderedDict(facet=facet)
        facet_summary['summary'] = sorted_summaries
        final_summaries.append(facet_summary)

    codebase.attributes.summary_by_facet.extend(final_summaries)

    if TRACE: logger_debug('codebase summary_by_facet:', final_summaries)
