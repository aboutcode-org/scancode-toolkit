#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import defaultdict

import attr
import fingerprints
from commoncode.cliutils import POST_SCAN_GROUP, PluggableCommandLineOption
from license_expression import Licensing
from plugincode.post_scan import PostScanPlugin, post_scan_impl

from cluecode.copyrights import CopyrightDetector
from packagedcode.utils import combine_expressions
from packagedcode import models
from summarycode.copyright_tallies import canonical_holder
from summarycode.score import compute_license_score
from summarycode.score import get_field_values_from_codebase_resources
from summarycode.score import unique
from summarycode.tallies import compute_codebase_tallies

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
        PluggableCommandLineOption(
            ('--summary',),
            is_flag=True,
            default=False,
            help='Summarize scans by providing declared origin '
            'information and other detected origin info at the '
            'codebase attribute level.',
            help_group=POST_SCAN_GROUP,
            required_options=['classify'],
        )
    ]

    def is_enabled(self, summary, **kwargs):
        return summary

    def process_codebase(self, codebase, summary, **kwargs):
        if TRACE_LIGHT:
            logger_debug('ScanSummary:process_codebase')

        # Get tallies
        tallies = compute_codebase_tallies(codebase, keep_details=False, **kwargs)
        license_expressions_tallies = tallies.get('license_expressions') or []
        holders_tallies = tallies.get('holders') or []
        programming_language_tallies = tallies.get('programming_language') or []

        # Determine declared license expression, declared holder, and primary
        # language from Package data at the top level.

        declared_license_expression = None
        declared_holders = None
        primary_language = None

        # use top level packages
        if hasattr(codebase.attributes, 'packages'):
            top_level_packages = codebase.attributes.packages
            (
                declared_license_expression,
                declared_holders,
                primary_language,
            ) = get_origin_info_from_top_level_packages(
                top_level_packages=top_level_packages,
                codebase=codebase,
            )

        if declared_license_expression:
            scoring_elements, _ = compute_license_score(codebase)
        else:
            # If we did not get a declared license expression from detected
            # package data, then we use the results from `compute_license_score`
            scoring_elements, declared_license_expression = compute_license_score(codebase)
        other_license_expressions = remove_from_tallies(
            declared_license_expression, license_expressions_tallies
        )

        if not declared_holders:
            declared_holders = get_declared_holders(codebase, holders_tallies)
        other_holders = remove_from_tallies(declared_holders, holders_tallies)
        declared_holder = ', '.join(declared_holders)

        if not primary_language:
            primary_language = get_primary_language(programming_language_tallies)
        other_languages = remove_from_tallies(primary_language, programming_language_tallies)

        # Save summary info to codebase
        codebase.attributes.summary['declared_license_expression'] = declared_license_expression
        codebase.attributes.summary['license_clarity_score'] = scoring_elements.to_dict()
        codebase.attributes.summary['declared_holder'] = declared_holder
        codebase.attributes.summary['primary_language'] = primary_language
        codebase.attributes.summary['other_license_expressions'] = other_license_expressions
        codebase.attributes.summary['other_holders'] = other_holders
        codebase.attributes.summary['other_languages'] = other_languages


def remove_from_tallies(entry, tallies):
    """
    Return an list containing the elements of `tallies`, without `entry`
    """
    pruned_tallies = []
    for t in tallies:
        if (
            isinstance(entry, dict)
            and t == entry
            or isinstance(entry, (list, tuple))
            and t in entry
            or isinstance(entry, (list, tuple))
            and t.get('value') in entry
            or t.get('value') == entry
        ):
            continue
        pruned_tallies.append(t)
    return pruned_tallies


def get_declared_holders(codebase, holders_tallies):
    """
    Return a list of declared holders from a codebase using the holders
    detected from key files.

    A declared holder is a copyright holder present in the key files who has the
    highest amount of refrences throughout the codebase.
    """
    entry_by_holders = {
        fingerprints.generate(entry['value']): entry for entry in holders_tallies if entry['value']
    }
    key_file_holders = get_field_values_from_codebase_resources(
        codebase, 'holders', key_files_only=True
    )
    entry_by_key_file_holders = {
        fingerprints.generate(canonical_holder(entry['holder'])): entry
        for entry in key_file_holders
        if entry['holder']
    }
    unique_key_file_holders = unique(entry_by_key_file_holders.keys())
    unique_key_file_holders_entries = [
        entry_by_holders[holder] for holder in unique_key_file_holders
    ]

    holder_by_counts = defaultdict(list)
    for holder_entry in unique_key_file_holders_entries:
        count = holder_entry.get('count')
        if count:
            holder = holder_entry.get('value')
            holder_by_counts[count].append(holder)

    declared_holders = []
    if holder_by_counts:
        highest_count = max(holder_by_counts)
        declared_holders = holder_by_counts[highest_count]

    # If we could not determine a holder, then we return a list of all the
    # unique key file holders
    if not declared_holders:
        declared_holders = [entry['value'] for entry in unique_key_file_holders_entries]

    return declared_holders


def get_primary_language(programming_language_tallies):
    """
    Return the most common detected programming language as the primary language.
    """
    programming_languages_by_count = {
        entry['count']: entry['value'] for entry in programming_language_tallies
    }
    primary_language = None
    if programming_languages_by_count:
        highest_count = max(programming_languages_by_count)
        primary_language = programming_languages_by_count[highest_count] or None
    return primary_language


def get_origin_info_from_top_level_packages(top_level_packages, codebase):
    """
    Return a 3-tuple containing the declared license expression string, a list
    of copyright holder, and primary programming language string from a
    ``top_level_packages`` list of detected top-level packages mapping and a
    ``codebase``.
    """
    if not top_level_packages:
        return None, [], None

    license_expressions = []
    programming_languages = []
    copyrights = []

    top_level_packages = [
        models.Package.from_dict(package_mapping)
        for package_mapping in top_level_packages
    ]
    key_file_packages = [p for p in top_level_packages if is_key_package(p, codebase)]
    for package in key_file_packages:
        license_expression = package.license_expression
        if license_expression:
            license_expressions.append(license_expression)

        programming_language = package.primary_language
        if programming_language:
            programming_languages.append(programming_language)

        copyright_statement = package.copyright
        if copyright_statement:
            copyrights.append(copyright_statement)

    # Combine license expressions
    unique_license_expressions = unique(license_expressions)
    combined_declared_license_expression = combine_expressions(
        expressions=unique_license_expressions,
        relation='AND',
    )

    declared_license_expression = None
    if combined_declared_license_expression:
        declared_license_expression = str(
            Licensing().parse(combined_declared_license_expression).simplify()
        )

    # Get holders
    holders = list(get_holders_from_copyright(copyrights))
    declared_holders = []
    if holders:
        declared_holders = holders
    else:
        # If the package data does not contain an explicit copyright, check the
        # key files where the package data was detected from and see if there
        # are any holder detections that can be used.
        for package in key_file_packages:
            for datafile_path in package.datafile_paths:
                key_file_resource = codebase.get_resource(path=datafile_path)
                if not key_file_resource:
                    continue

                if not hasattr(key_file_resource, 'holders'):
                    break

                holders = [h['holder'] for h in key_file_resource.holders]
                declared_holders.extend(holders)
    # Normalize holder names before collecting them
    # This allows us to properly remove declared holders from `other_holders` later
    declared_holders = [canonical_holder(h) for h in declared_holders]
    declared_holders = unique(declared_holders)

    # Programming language
    unique_programming_languages = unique(programming_languages)
    primary_language = None
    if len(unique_programming_languages) == 1:
        primary_language = unique_programming_languages[0]

    return declared_license_expression, declared_holders, primary_language


def get_holders_from_copyright(copyright):
    """
    Yield holders detected from a `copyright` string or list.
    """
    numbered_lines = []
    if isinstance(copyright, list):
        for i, c in enumerate(copyright):
            numbered_lines.append((i, c))
    else:
        numbered_lines.append((0, copyright))

    holder_detections = CopyrightDetector().detect(
        numbered_lines,
        include_copyrights=False,
        include_holders=True,
        include_authors=False,
    )

    for holder_detection in holder_detections:
        yield holder_detection.holder


def is_key_package(package, codebase):
    """
    Return True if the ``package`` Package is a key, top-level package.
    """
    # get the datafile_paths of the package
    # get the top level files in the codebase
    # return True if any datafile_paths is also a top level files? or key file?

    datafile_paths = set(package.datafile_paths or [])
    for resource in codebase.walk(topdown=True):
        if not resource.is_top_level:
            break
        if resource.path in datafile_paths:
            return True

    return False
