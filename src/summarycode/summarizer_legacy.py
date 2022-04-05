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


class SummaryLegacyPluginDeprecationWarning(DeprecationWarning):
    pass


@post_scan_impl
class ScanSummaryLegacy(PostScanPlugin):
    """
    Summarize a scan at the codebase level.
    """
    sort_order = 10

    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(dict)))

    options = [
        PluggableCommandLineOption(('--summary-legacy',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary_legacy, **kwargs):
        return summary_legacy

    def process_codebase(self, codebase, summary_legacy, **kwargs):
        deprecation_message = "The --summary-legacy option will be deprecated in a future version of scancode-toolkit."
        warnings.simplefilter('always', SummaryLegacyPluginDeprecationWarning)
        warnings.warn(
            deprecation_message,
            SummaryLegacyPluginDeprecationWarning,
            stacklevel=2,
        )
        codebase_header = codebase.get_or_create_current_header()
        codebase_header.warnings.append(deprecation_message)
        if TRACE_LIGHT: logger_debug('ScanSummaryLegacy:process_codebase')
        summarize_codebase_legacy(codebase, keep_details=False, **kwargs)


class SummaryWithDetailsDeprecationWarning(DeprecationWarning):
    pass


@post_scan_impl
class ScanSummaryWithDetails(PostScanPlugin):
    """
    Summarize a scan at the codebase level and keep file and directory details.
    """
    # mapping of summary data at the codebase level for the whole codebase
    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(dict)))
    # store summaries at the file and directory level in this attribute when
    # keep details is True
    resource_attributes = dict(summary=attr.ib(default=attr.Factory(dict)))
    sort_order = 100

    options = [
        PluggableCommandLineOption(('--summary-with-details',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans at the codebase level, '
                 'keeping intermediate details at the file and directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary_with_details, **kwargs):
        return summary_with_details

    def process_codebase(self, codebase, summary_with_details, **kwargs):
        deprecation_message = "The --summary-with-details option will be deprecated in a future version of scancode-toolkit."
        warnings.simplefilter('always', SummaryWithDetailsDeprecationWarning)
        warnings.warn(
            deprecation_message,
            SummaryWithDetailsDeprecationWarning,
            stacklevel=2,
        )
        codebase_header = codebase.get_or_create_current_header()
        codebase_header.warnings.append(deprecation_message)
        summarize_codebase_legacy(codebase, keep_details=True, **kwargs)


def summarize_codebase(codebase, keep_details, legacy=False, **kwargs):
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

    if legacy:
        from summarycode.copyright_summary import author_summarizer
        from summarycode.copyright_summary import copyright_summarizer

        attrib_summarizers.extend([
            ('copyrights', copyright_summarizer),
            ('authors', author_summarizer),
            ('programming_language', language_summarizer),
            ('packages', package_summarizer),
        ])


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


def summarize_codebase_legacy(codebase, keep_details, legacy=False, **kwargs):
    """
    Summarize a scan at the codebase level for available scans.

    If `keep_details` is True, also keep file and directory details in the
    `summary` file attribute for every file and directory.

    If `legacy` is True, summarize copyrights, authors, programming languages,
    and packages.
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
        ('packages', package_summarizer),
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


def summarize_values(values, attribute):
    """
    Given a list of `values` for a given `attribute`, return a mapping of
    {value: count of occurences} using a summarization specific to the attribute.
    """
    if attribute not in SUMMARIZABLE_ATTRS:
        return {}
    from summarycode.copyright_summary import summarize_persons
    from summarycode.copyright_summary import summarize_copyrights

    value_summarizers_by_attr = dict(
        license_expressions=summarize_licenses,
        copyrights=summarize_copyrights,
        holders=summarize_persons,
        authors=summarize_persons,
        programming_language=summarize_languages,
    )
    return value_summarizers_by_attr[attribute](values)


class SummaryKeyFilesDeprecationWarning(DeprecationWarning):
    pass


@post_scan_impl
class ScanKeyFilesSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level for only key files.
    """
    sort_order = 150

    # mapping of summary data at the codebase level for key files
    codebase_attributes = dict(summary_of_key_files=attr.ib(default=attr.Factory(dict)))

    options = [
        PluggableCommandLineOption(('--summary-key-files',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans for key, '
                 'top-level files. Key files are top-level codebase files such '
                 'as COPYING, README and package manifests as reported by the '
                 '--classify option "is_legal", "is_readme", "is_manifest" '
                 'and "is_top_level" flags.',
            help_group=POST_SCAN_GROUP,
            required_options=['classify', 'summary_legacy']
        )
    ]

    def is_enabled(self, summary_key_files, **kwargs):
        return summary_key_files

    def process_codebase(self, codebase, summary_key_files, **kwargs):
        deprecation_message = "The --summary-key-files option will be deprecated in a future version of scancode-toolkit."
        warnings.simplefilter('always', SummaryKeyFilesDeprecationWarning)
        warnings.warn(
            deprecation_message,
            SummaryKeyFilesDeprecationWarning,
            stacklevel=2,
        )
        codebase_header = codebase.get_or_create_current_header()
        codebase_header.warnings.append(deprecation_message)
        summarize_codebase_key_files(codebase, **kwargs)


def summarize_codebase_key_files(codebase, **kwargs):
    """
    Summarize codebase key files.
    """
    summarizables = codebase.attributes.summary.keys()
    if TRACE: logger_debug('summarizables:', summarizables)

    # TODO: we cannot summarize packages with "key files" for now
    summarizables = [k for k in summarizables if k in SUMMARIZABLE_ATTRS]

    # create one counter for each summarized attribute
    summarizable_values_by_key = dict([(key, []) for key in summarizables])

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
                sum_value = summary.get('value')
                if sum_value:
                    values.extend([sum_value] * summary['count'])

    summary_counters = []
    for key, values in summarizable_values_by_key.items():
        if key not in SUMMARIZABLE_ATTRS:
            continue
        summarized = summarize_values(values, key)
        summary_counters.append((key, summarized))

    sorted_summaries = dict(
        [(key, sorted_counter(counter)) for key, counter in summary_counters])

    codebase.attributes.summary_of_key_files = sorted_summaries

    if TRACE: logger_debug('codebase summary_of_key_files:', sorted_summaries)


class SummaryByFacetPluginDeprecationWarning(DeprecationWarning):
    pass


@post_scan_impl
class ScanByFacetSummary(PostScanPlugin):
    """
    Summarize a scan at the codebase level groupping by facets.
    """
    sort_order = 200
    codebase_attributes = dict(summary_by_facet=attr.ib(default=attr.Factory(list)))

    options = [
        PluggableCommandLineOption(('--summary-by-facet',),
            is_flag=True, default=False,
            help='Summarize license, copyright and other scans and group the '
                 'results by facet.',
            help_group=POST_SCAN_GROUP,
            required_options=['facet', 'summary_legacy']
        )
    ]

    def is_enabled(self, summary_by_facet, **kwargs):
        return summary_by_facet

    def process_codebase(self, codebase, summary_by_facet, **kwargs):
        deprecation_message = "The --summary-by-facet option will be deprecated in a future version of scancode-toolkit."
        warnings.simplefilter('always', SummaryByFacetPluginDeprecationWarning)
        warnings.warn(
            deprecation_message,
            SummaryByFacetPluginDeprecationWarning,
            stacklevel=2,
        )
        codebase_header = codebase.get_or_create_current_header()
        codebase_header.warnings.append(deprecation_message)
        if TRACE_LIGHT: logger_debug('ScanByFacetSummary:process_codebase')
        summarize_codebase_by_facet(codebase, **kwargs)


def summarize_codebase_by_facet(codebase, **kwargs):
    """
    Summarize codebase by facte.
    """
    from summarycode import facet as facet_module

    summarizable = codebase.attributes.summary.keys()
    if TRACE:
        logger_debug('summarize_codebase_by_facet for attributes:', summarizable)

    # create one group of by-facet values lists for each summarized attribute
    summarizable_values_by_key_by_facet = dict([
        (facet, dict([(key, []) for key in summarizable]))
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
                    sum_value = summary.get('value')
                    if sum_value:
                        values.extend([sum_value] * summary['count'])

    final_summaries = []
    for facet, summarizable_values_by_key in summarizable_values_by_key_by_facet.items():
        summary_counters = (
            (key, summarize_values(values, key))
            for key, values in summarizable_values_by_key.items()
        )

        sorted_summaries = dict(
            [(key, sorted_counter(counter)) for key, counter in summary_counters])

        facet_summary = dict(facet=facet)
        facet_summary['summary'] = sorted_summaries
        final_summaries.append(facet_summary)

    codebase.attributes.summary_by_facet.extend(final_summaries)

    if TRACE: logger_debug('codebase summary_by_facet:', final_summaries)


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


def get_declared_holders(codebase, summary):
    holders_summary = summary.get('holders', [])
    entry_by_holders = {entry.get('value'): entry for entry in holders_summary}
    key_file_holders = get_field_values_from_codebase_resources(codebase, 'holders', key_files_only=True)
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


def get_primary_language(summary):
    programming_language_summary = summary.get('programming_language')

    programming_language_entry_by_count = {entry.get('count'): entry for entry in programming_language_summary}
    primary_language = {}
    if programming_language_entry_by_count:
        highest_count = max(programming_language_entry_by_count)
        primary_language = programming_language_entry_by_count[highest_count]

    return primary_language


def remove_declared_from_fields(codebase, summary):
    license_expressions = summary.get('license_expressions', [])
    holders = summary.get('holders', [])
    programming_languages = summary.get('programming_language', [])

    declared_license_expression = codebase.attributes.summary.get('declared_license_expression', '')
    declared_holders = codebase.attributes.summary.get('declared_holders', [])
    primary_programming_language = codebase.attributes.summary.get('primary_programming_language', {})

    other_license_expressions = [
        entry
        for entry in license_expressions
        if entry.get('value') != declared_license_expression
    ]

    other_holders = [
        entry
        for entry in holders
        if entry not in declared_holders
    ]

    other_programming_languages = [
        entry
        for entry in programming_languages
        if entry != primary_programming_language
    ]

    codebase.attributes.summary['other_license_expressions'] = other_license_expressions
    codebase.attributes.summary['other_holders'] = other_holders
    codebase.attributes.summary['other_programming_languages'] = other_programming_languages
