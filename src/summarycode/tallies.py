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
from commoncode.cliutils import POST_SCAN_GROUP, PluggableCommandLineOption
from plugincode.post_scan import PostScanPlugin, post_scan_impl

from summarycode.utils import (get_resource_tallies, set_resource_tallies,
                               sorted_counter)

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
class Tallies(PostScanPlugin):
    """
    Compute tallies for license, copyright and other scans at the codebase level
    """
    sort_order = 10

    codebase_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))

    options = [
        PluggableCommandLineOption(('--tallies',),
            is_flag=True, default=False,
            help='Compute tallies for license, copyright and other scans at the codebase level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, tallies, **kwargs):
        return tallies

    def process_codebase(self, codebase, tallies, **kwargs):
        if TRACE_LIGHT: logger_debug('Tallies:process_codebase')
        tallies = compute_codebase_tallies(codebase, keep_details=False, **kwargs)
        codebase.attributes.tallies.update(tallies)


@post_scan_impl
class TalliesWithDetails(PostScanPlugin):
    """
    Compute tallies of different scan attributes of a scan at the codebase level and
    keep file and directory details.

    The scan attributes that are tallied are:
    - license_expressions
    - copyrights
    - holders
    - authors
    - programming_language
    - packages
    """
    # mapping of tally data at the codebase level for the whole codebase
    codebase_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))
    # store tallies at the file and directory level in this attribute when
    # keep details is True
    resource_attributes = dict(tallies=attr.ib(default=attr.Factory(dict)))
    sort_order = 100

    options = [
        PluggableCommandLineOption(('--tallies-with-details',),
            is_flag=True, default=False,
            help='Compute tallies of license, copyright and other scans at the codebase level, '
                 'keeping intermediate details at the file and directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, tallies_with_details, **kwargs):
        return tallies_with_details

    def process_codebase(self, codebase, tallies_with_details, **kwargs):
        tallies = compute_codebase_tallies(codebase, keep_details=True, **kwargs)
        codebase.attributes.tallies.update(tallies)


def compute_codebase_tallies(codebase, keep_details, **kwargs):
    """
    Compute tallies of a scan at the codebase level for available scans.

    If `keep_details` is True, also keep file and directory details in the
    `tallies` file attribute for every file and directory.
    """
    from summarycode.copyright_tallies import (author_tallies,
                                               copyright_tallies,
                                               holder_tallies)

    attrib_summarizers = [
        ('license_expressions', license_tallies),
        ('copyrights', copyright_tallies),
        ('holders', holder_tallies),
        ('authors', author_tallies),
        ('programming_language', language_tallies),
        ('packages', package_tallies),
    ]

    # find which attributes are available for summarization by checking the root
    # resource
    root = codebase.root
    summarizers = [s for a, s in attrib_summarizers if hasattr(root, a)]
    if TRACE: logger_debug('compute_codebase_tallies with:', summarizers)

    # collect and set resource-level summaries
    for resource in codebase.walk(topdown=False):
        children = resource.children(codebase)

        for summarizer in summarizers:
            _summary_data = summarizer(resource, children, keep_details=keep_details)
            if TRACE: logger_debug('tallies for:', resource.path, 'after tallies:', summarizer, 'is:', _summary_data)

        codebase.save_resource(resource)

    # set the tallies from the root resource at the codebase level
    if keep_details:
        tallies = root.tallies
    else:
        tallies = root.extra_data.get('tallies', {})

    if TRACE: logger_debug('codebase tallies:', tallies)
    return tallies


def license_tallies(resource, children, keep_details=False):
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

    # Collect direct children expression tallies
    for child in children:
        child_tallies = get_resource_tallies(child, key=LIC_EXP, as_attribute=keep_details) or []
        for child_tally in child_tallies:
            # TODO: review this: this feels rather weird
            child_sum_val = child_tally.get('value')
            if child_sum_val:
                values = [child_sum_val] * child_tally['count']
                license_expressions.extend(values)

    # summarize proper
    licenses_counter = tally_licenses(license_expressions)
    tallied = sorted_counter(licenses_counter)
    set_resource_tallies(resource, key=LIC_EXP, value=tallied, as_attribute=keep_details)
    return tallied


def tally_licenses(license_expressions):
    """
    Given a list of license expressions, return a mapping of {expression: count
    of occurences}
    """
    # TODO: we could normalize and/or sort each license_expression before
    # summarization and consider other equivalence or containment checks
    return Counter(license_expressions)


def language_tallies(resource, children, keep_details=False):
    """
    Populate a programming_language tallies list of mappings such as
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
        child_tallies = get_resource_tallies(child, key=PROG_LANG, as_attribute=keep_details) or []
        for child_tally in child_tallies:
            child_sum_val = child_tally.get('value')
            if child_sum_val:
                values = [child_sum_val] * child_tally['count']
                languages.extend(values)

    # summarize proper
    languages_counter = tally_languages(languages)
    tallied = sorted_counter(languages_counter)
    set_resource_tallies(resource, key=PROG_LANG, value=tallied, as_attribute=keep_details)
    return tallied


def tally_languages(languages):
    """
    Given a list of languages, return a mapping of {language: count
    of occurences}
    """
    # TODO: consider aggregating related langauges (C/C++, etc)
    return Counter(languages)


TALLYABLE_ATTRS = set([
    'license_expressions',
    'copyrights',
    'holders',
    'authors',
    'programming_language',
    # 'packages',
])


def tally_values(values, attribute):
    """
    Given a list of `values` for a given `attribute`, return a mapping of
    {value: count of occurences} using a tallier specific to the attribute.
    """
    if attribute not in TALLYABLE_ATTRS:
        return {}
    from summarycode.copyright_tallies import tally_copyrights, tally_persons

    value_talliers_by_attr = dict(
        license_expressions=tally_licenses,
        copyrights=tally_copyrights,
        holders=tally_persons,
        authors=tally_persons,
        programming_language=tally_languages,
    )
    return value_talliers_by_attr[attribute](values)


@post_scan_impl
class KeyFilesTallies(PostScanPlugin):
    """
    Compute tallies of a scan at the codebase level for only key files.
    """
    sort_order = 150

    # mapping of tally data at the codebase level for key files
    codebase_attributes = dict(tallies_of_key_files=attr.ib(default=attr.Factory(dict)))

    options = [
        PluggableCommandLineOption(('--tallies-key-files',),
            is_flag=True, default=False,
            help='Compute tallies for license, copyright and other scans for key, '
                 'top-level files. Key files are top-level codebase files such '
                 'as COPYING, README and package manifests as reported by the '
                 '--classify option "is_legal", "is_readme", "is_manifest" '
                 'and "is_top_level" flags.',
            help_group=POST_SCAN_GROUP,
            required_options=['classify', 'tallies']
        )
    ]

    def is_enabled(self, tallies_key_files, **kwargs):
        return tallies_key_files

    def process_codebase(self, codebase, tallies_key_files, **kwargs):
        tally_codebase_key_files(codebase, **kwargs)


def tally_codebase_key_files(codebase, field='tallies', **kwargs):
    """
    Summarize codebase key files.
    """
    talliables = codebase.attributes.tallies.keys()
    if TRACE: logger_debug('tallieables:', talliables)

    # TODO: we cannot summarize packages with "key files" for now
    talliables = [k for k in talliables if k in TALLYABLE_ATTRS]

    # create one counter for each summarized attribute
    talliable_values_by_key = dict([(key, []) for key in talliables])

    # filter to get only key files
    key_files = (res for res in codebase.walk(topdown=True)
                 if (res.is_file and res.is_top_level
                     and (res.is_readme or res.is_legal or res.is_manifest)))

    for resource in key_files:
        for key, values in talliable_values_by_key.items():
            # note we assume things are stored as extra-data, not as direct
            # Resource attributes
            res_tallies = get_resource_tallies(resource, key=key, as_attribute=False) or []
            for tally in res_tallies:
                # each tally is a mapping with value/count: we transform back to values
                tally_value = tally.get('value')
                if tally_value:
                    values.extend([tally_value] * tally['count'])

    tally_counters = []
    for key, values in talliable_values_by_key.items():
        if key not in TALLYABLE_ATTRS:
            continue
        tallied = tally_values(values, key)
        tally_counters.append((key, tallied))

    sorted_tallies = dict(
        [(key, sorted_counter(counter)) for key, counter in tally_counters])

    codebase.attributes.tallies_of_key_files = sorted_tallies

    if TRACE: logger_debug('codebase tallies_of_key_files:', sorted_tallies)


@post_scan_impl
class FacetTallies(PostScanPlugin):
    """
    Compute tallies for a scan at the codebase level, grouping by facets.
    """
    sort_order = 200
    codebase_attributes = dict(tallies_by_facet=attr.ib(default=attr.Factory(list)))

    options = [
        PluggableCommandLineOption(('--tallies-by-facet',),
            is_flag=True, default=False,
            help='Compute tallies for license, copyright and other scans and group the '
                 'results by facet.',
            help_group=POST_SCAN_GROUP,
            required_options=['facet', 'tallies']
        )
    ]

    def is_enabled(self, tallies_by_facet, **kwargs):
        return tallies_by_facet

    def process_codebase(self, codebase, tallies_by_facet, **kwargs):
        if TRACE_LIGHT: logger_debug('FacetTallies:process_codebase')
        tally_codebase_by_facet(codebase, **kwargs)


def tally_codebase_by_facet(codebase, **kwargs):
    """
    Summarize codebase by facte.
    """
    from summarycode import facet as facet_module

    talliable = codebase.attributes.tallies.keys()
    if TRACE:
        logger_debug('tally_codebase_by_facet for attributes:', talliable)

    # create one group of by-facet values lists for each summarized attribute
    talliable_values_by_key_by_facet = dict([
        (facet, dict([(key, []) for key in talliable]))
        for facet in facet_module.FACETS
    ])

    for resource in codebase.walk(topdown=True):
        if not resource.is_file:
            continue

        for facet in resource.facets:
            # note: this will fail loudly if the facet is not a known one
            values_by_attribute = talliable_values_by_key_by_facet[facet]
            for key, values in values_by_attribute.items():
                # note we assume things are stored as extra-data, not as direct
                # Resource attributes
                res_tallies = get_resource_tallies(resource, key=key, as_attribute=False) or []
                for tally in res_tallies:
                    # each tally is a mapping with value/count: we transform back to discrete values
                    tally_value = tally.get('value')
                    if tally_value:
                        values.extend([tally_value] * tally['count'])

    final_tallies = []
    for facet, talliable_values_by_key in talliable_values_by_key_by_facet.items():
        tally_counters = (
            (key, tally_values(values, key))
            for key, values in talliable_values_by_key.items()
        )

        sorted_tallies = dict(
            [(key, sorted_counter(counter)) for key, counter in tally_counters])

        facet_tally = dict(facet=facet)
        facet_tally['tallies'] = sorted_tallies
        final_tallies.append(facet_tally)

    codebase.attributes.tallies_by_facet.extend(final_tallies)

    if TRACE: logger_debug('codebase tallies_by_facet:', final_tallies)


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


def package_tallies(resource, children, keep_details=False):
    """
    Populate a packages tally list of packages mappings.

    Note: `keep_details` is never used, as we are not keeping details of
    packages as this has no value.
    """
    packages = []

    # Collect current data
    current_packages = getattr(resource, 'packages') or []

    if TRACE_LIGHT and current_packages:
        from packagedcode.models import Package
        packs = [Package.create(**p) for p in current_packages]
        logger_debug('package_tallier: for:', resource,
                     'current_packages are:', packs)

    current_packages = add_files(current_packages, resource)
    packages.extend(current_packages)

    if TRACE_LIGHT and packages:
        logger_debug()
        from packagedcode.models import Package  # NOQA
        packs = [Package.create(**p) for p in packages]
        logger_debug('package_tallier: for:', resource,
                     'packages are:', packs)

    # Collect direct children packages tallies
    for child in children:
        child_tallies = get_resource_tallies(child, key='packages', as_attribute=False) or []
        packages.extend(child_tallies)

    # summarize proper
    set_resource_tallies(resource, key='packages', value=packages, as_attribute=False)
    return packages
