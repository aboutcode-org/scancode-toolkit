#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr

from commoncode.datautils import Mapping
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP


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
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


"""
A plugin to compute a licensing clarity score as designed in ClearlyDefined
"""


@post_scan_impl
class LicenseClarityScore2(PostScanPlugin):
    """
    Compute a License clarity score at the codebase level.
    """
    codebase_attributes = dict(license_clarity_score=Mapping(
        help='Computed license clarity score as mapping containing the score '
             'proper and each scoring elements.'))

    sort_order = 110

    options = [
        PluggableCommandLineOption(('--license-clarity-score-2',),
            is_flag=True,
            default=False,
            help='Compute a summary license clarity score at the codebase level.',
            help_group=POST_SCAN_GROUP,
            required_options=[
                'classify',
            ],
        )
    ]

    def is_enabled(self, license_clarity_score_2, **kwargs):
        return license_clarity_score_2

    def process_codebase(self, codebase, license_clarity_score_2, **kwargs):
        if TRACE:
            logger_debug('LicenseClarityScore2:process_codebase')
        score = calculate(codebase)
        codebase.attributes.license_clarity_score['score'] = score


def calculate(codebase):
    """
    Return a score for how well a codebase defined it's license
    """
    score = 0
    declared_licenses = get_declared_license_info_in_key_files_from_top_level_dir(codebase)
    declared_license_categories = get_license_categories(declared_licenses)
    copyrights = get_copyrights_from_key_files(codebase)
    other_licenses = get_other_licenses(codebase)

    if declared_licenses:
        score += 40

    if check_declared_licenses(declared_licenses):
        score += 40

    if check_for_license_texts(declared_licenses):
        score += 10

    if copyrights:
        score += 10

    is_permissively_licensed = 'Copyleft' not in declared_license_categories
    if is_permissively_licensed:
        contains_copyleft_licenses = check_for_copyleft(other_licenses)
        if contains_copyleft_licenses:
            score -= 20

    return score


# minimum score to consider a license detection as good.

# MIN_GOOD_LICENSE_SCORE = 80


@attr.s(slots=True)
class LicenseFilter(object):
    min_score = attr.ib(default=0)
    min_coverage = attr.ib(default=0)
    min_relevance = attr.ib(default=0)


FILTERS = dict(
    is_license_text=LicenseFilter(min_score=70, min_coverage=80),
    is_license_notice=LicenseFilter(min_score=80, min_coverage=80),
    is_license_tag=LicenseFilter(min_coverage=100),
    is_license_reference=LicenseFilter(min_score=50, min_coverage=100),
    is_license_intro=LicenseFilter(min_score=100, min_coverage=100),
)


def is_good_license(detected_license):
    """
    Return True if a `detected license` mapping is consider to a high quality
    conclusive match.
    """
    score = detected_license['score']
    rule = detected_license['matched_rule']
    coverage = rule.get('match_coverage') or 0
    relevance = rule.get('rule_relevance') or 0
    match_types = dict([
        ('is_license_text', rule['is_license_text']),
        ('is_license_notice', rule['is_license_notice']),
        ('is_license_reference', rule['is_license_reference']),
        ('is_license_tag', rule['is_license_tag']),
        ('is_license_intro', rule['is_license_intro']),
    ])
    matched = False
    for match_type, mval in match_types.items():
        if mval:
            matched = True
            break
    if not matched:
        return False

    thresholds = FILTERS[match_type]

    if not coverage or not relevance:
        if score >= thresholds.min_score:
            return True
    else:
        if (score >= thresholds.min_score
        and coverage >= thresholds.min_coverage
        and relevance >= thresholds.min_relevance):
            return True

    return False


def get_declared_license_info_in_key_files_from_top_level_dir(codebase):
    """
    Return a list of "declared" license keys from the expressions as detected in
    key files from top-level directories.

    A project has specific key file(s) at the top level of its code hierarchy
    such as LICENSE, NOTICE or similar (and/or a package manifest) containing
    structured license information such as an SPDX license expression or SPDX
    license identifier: when such a file contains "clearly defined" declared
    license information, we return this.
    """
    declared = []
    for resource in codebase.walk(topdown=True):
        if not (resource.is_dir and resource.is_top_level):
            continue
        for child in resource.walk(codebase):
            if not child.is_key_file:
                continue
            for detected_license in getattr(child, 'licenses', []) or []:
                declared.append(detected_license)
    return declared


def get_other_licenses(codebase):
    """
    Return a list of detected licenses from non-key files under a top-level directory
    """
    other_licenses = []
    for resource in codebase.walk(topdown=True):
        if not (resource.is_dir and resource.is_top_level):
            continue
        for child in resource.walk(codebase):
            if child.is_key_file:
                continue
            for detected_license in getattr(child, 'licenses', []) or []:
                other_licenses.append(detected_license)
    return other_licenses


def get_copyrights_from_key_files(codebase):
    """
    Return a list of copyright statements from key files from a top-level directory
    """
    copyright_statements = []
    for resource in codebase.walk(topdown=True):
        if not (resource.is_dir and resource.is_top_level):
            continue
        for child in resource.walk(codebase):
            if not child.is_key_file:
                continue
            for detected_copyright in getattr(child, 'copyrights', []) or []:
                copyright_statement = detected_copyright.get('copyright')
                if copyright_statement:
                    copyright_statements.append(copyright_statement)
    return copyright_statements


def get_license_categories(license_infos):
    """
    Return a list of license category strings from `license_infos`
    """
    license_categories = []
    for license_info in license_infos:
        category = license_info.get('category', '')
        if category not in license_categories:
            license_categories.append(category)
    return license_categories


def check_for_license_texts(declared_licenses):
    """
    Check if any license in `declared_licenses` is from a license text or notice.

    If so, return True. Otherwise, return False.
    """
    for declared_license in declared_licenses:
        matched_rule = declared_license.get('matched_rule', {})
        if any([
            matched_rule.get('is_license_text', False),
            matched_rule.get('is_license_notice', False),
        ]):
            return True
    return False


def check_declared_licenses(declared_licenses):
    """
    Check whether or not all the licenses in `declared_licenses` are good.

    If so, return True. Otherwise, return False.
    """
    return all(
        is_good_license(declared_license)
        for declared_license
        in declared_licenses
    )


def check_for_copyleft(other_licenses):
    """
    Check if there is a copyleft license in `other_licenses`.

    If so, return True. Otherwise, return False.
    """
    for license_info in other_licenses:
        if license_info.get('category', '') in ('Copyleft',):
            return True
    return False
