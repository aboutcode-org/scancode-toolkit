#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter, defaultdict
import warnings

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from summarycode.score import compute_license_score
from summarycode.score import get_field_values_from_codebase_resources
from summarycode.score import unique
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
        PluggableCommandLineOption(('--summary',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP,
            required_options=['classify']
        )
    ]

    def is_enabled(self, summary, **kwargs):
        return summary

    def process_codebase(self, codebase, summary, **kwargs):
        if TRACE_LIGHT: logger_debug('ScanSummary:process_codebase')

        summary = summarize_codebase(codebase, keep_details=False, **kwargs)

        license_expressions_summary = summary.get('license_expressions', [])
        scoring_elements, declared_license_expression = compute_license_score(codebase)
        other_license_expressions = remove_from_summary(declared_license_expression, license_expressions_summary)

        holders_summary = summary.get('holders', [])
        declared_holders = get_declared_holders(codebase, holders_summary)
        other_holders = remove_from_summary(declared_holders, holders_summary)

        programming_language_summary = summary.get('programming_language', [])
        primary_language = get_primary_language(programming_language_summary)
        other_programming_languages = remove_from_summary(primary_language, programming_language_summary)

        # Save summary info to codebase
        codebase.attributes.summary['declared_license_expression'] = declared_license_expression
        codebase.attributes.summary['license_clarity_score'] = scoring_elements.to_dict()
        codebase.attributes.summary['declared_holders'] = declared_holders
        codebase.attributes.summary['primary_programming_language'] = primary_language
        codebase.attributes.summary['other_license_expressions'] = other_license_expressions
        codebase.attributes.summary['other_holders'] = other_holders
        codebase.attributes.summary['other_programming_languages'] = other_programming_languages


def remove_from_summary(entry, summary_data):
    """
    Return an list containing the elements of `summary_data`, without `entry`
    """
    pruned_summary_data = []
    for s in summary_data:
        if (
            isinstance(entry, dict) and s == entry
            or isinstance(entry, (list, tuple)) and s in entry
            or s.get('value') == entry
        ):
            continue
        pruned_summary_data.append(s)
    return pruned_summary_data


def summarize_codebase(codebase, keep_details, **kwargs):
    """
    Summarize a scan at the codebase level for available scans.

    If `keep_details` is True, also keep file and directory details in the
    `summary` file attribute for every file and directory.

    If `legacy` is True, summarize copyrights, authors, programming languages,
    and packages.
    """
    from summarycode.copyright_summary import holder_summarizer

    attrib_summarizers = [
        ('license_expressions', license_summarizer),
        ('holders', holder_summarizer),
        ('programming_language', language_summarizer),
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

    if TRACE: logger_debug('codebase summary:', summary)

    return summary


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
            child_sum_val = child_summary.get('value')
            if child_sum_val:
                values = [child_sum_val] * child_summary['count']
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


SUMMARIZABLE_ATTRS = set([
    'license_expressions',
    'copyrights',
    'holders',
    'authors',
    'programming_language',
    # 'packages',
])


def add_files(packages, resource):
    """
    Update in-place every package mapping in the `packages` list by updating or
    creating the the "files" attribute from the `resource`. Yield back the
    packages.
    """
    for package in packages:
        files = package['files'] = package.get('files') or []
        fil = resource.to_dict(skinny=True)
        if fil not in files:
            files.append(fil)
        yield package


def package_summarizer(resource, children, keep_details=False):
    """
    Populate a packages summary list of packages mappings.

    Note: `keep_details` is never used, as we are not keeping details of
    packages as this has no value.
    """
    packages = []

    # Collect current data
    current_packages = getattr(resource, 'packages') or []

    if TRACE_LIGHT and current_packages:
        from packagedcode.models import Package
        packs = [Package.create(**p) for p in current_packages]
        logger_debug('package_summarizer: for:', resource,
                     'current_packages are:', packs)

    current_packages = add_files(current_packages, resource)
    packages.extend(current_packages)

    if TRACE_LIGHT and packages:
        logger_debug()
        from packagedcode.models import Package  # NOQA
        packs = [Package.create(**p) for p in packages]
        logger_debug('package_summarizer: for:', resource,
                     'packages are:', packs)

    # Collect direct children packages summary
    for child in children:
        child_summaries = get_resource_summary(child, key='packages', as_attribute=False) or []
        packages.extend(child_summaries)

    # summarize proper
    set_resource_summary(resource, key='packages', value=packages, as_attribute=False)
    return packages


def get_declared_holders(codebase, holders_summary):
    key_file_holders = get_field_values_from_codebase_resources(codebase, 'holders', key_files_only=True)
    entry_by_holders = {entry.get('value'): entry for entry in holders_summary}
    key_file_holders = [entry.get('holder') for entry in key_file_holders]
    unique_key_file_holders = unique(key_file_holders)

    holder_entry_by_counts = defaultdict(list)
    for holder in unique_key_file_holders:
        entry = entry_by_holders.get(holder)
        count = entry.get('count')
        if count:
            holder_entry_by_counts[count].append(entry)

    declared_holders = []
    if holder_entry_by_counts:
        highest_count = max(holder_entry_by_counts)
        declared_holders = holder_entry_by_counts[highest_count]
    return declared_holders


def get_primary_language(programming_language_summary):
    programming_language_entry_by_count = {entry.get('count'): entry for entry in programming_language_summary}
    primary_language = {}
    if programming_language_entry_by_count:
        highest_count = max(programming_language_entry_by_count)
        primary_language = programming_language_entry_by_count[highest_count]
    return primary_language
