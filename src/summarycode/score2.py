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

from license_expression import Licensing


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
        scoring_elements = compute_license_score(codebase)
        codebase.attributes.license_clarity_score.update(scoring_elements)


def compute_license_score(codebase):
    """
    Return a mapping of scoring elements and a license clarity score computed at
    the codebase level.
    """

    scoring_elements = ScoringElements()
    declared_licenses = get_declared_license_info_from_top_level_key_files(codebase)
    declared_license_expressions = get_declared_license_expressions_from_top_level_key_files(codebase)
    declared_license_categories = get_license_categories(declared_licenses)
    copyrights = get_copyrights_from_key_files(codebase)
    other_licenses = get_other_licenses(codebase)

    scoring_elements.declared_license = bool(declared_licenses)
    if declared_licenses:
        scoring_elements.score += 40

    precise_license_detection = check_declared_licenses(declared_licenses)
    scoring_elements.precise_license_detection = precise_license_detection
    if precise_license_detection:
        scoring_elements.score += 40

    has_license_text = check_for_license_texts(declared_licenses)
    scoring_elements.has_license_text = has_license_text
    if has_license_text:
        scoring_elements.score += 10

    scoring_elements.declared_copyrights = bool(copyrights)
    if copyrights:
        scoring_elements.score += 10

    is_permissively_licensed = check_declared_license_categories(declared_license_categories)
    if is_permissively_licensed:
        contains_conflicting_license = check_for_conflicting_licenses(other_licenses)
        scoring_elements.conflicting_license_categories = contains_conflicting_license
        if contains_conflicting_license and scoring_elements.score > 0:
            scoring_elements.score -= 20

    ambigous_compound_licensing = check_ambiguous_license_expression(declared_license_expressions)
    scoring_elements.ambigous_compound_licensing = ambigous_compound_licensing
    if ambigous_compound_licensing and scoring_elements.score > 0:
        scoring_elements.score -= 10

    return scoring_elements.to_dict()


@attr.s()
class ScoringElements:
    score = attr.ib(default=0)
    declared_license = attr.ib(default=False)
    precise_license_detection = attr.ib(default=False)
    has_license_text = attr.ib(default=False)
    declared_copyrights = attr.ib(default=False)
    conflicting_license_categories = attr.ib(default=False)
    ambigous_compound_licensing = attr.ib(default=False)

    def to_dict(self):
        return {
            'score': self.score,
            'declared_license': self.declared_license,
            'precise_license_detection': self.precise_license_detection,
            'has_license_text': self.has_license_text,
            'declared_copyrights': self.declared_copyrights,
            'conflicting_license_categories': self.conflicting_license_categories,
            'ambigous_compound_licensing': self.ambigous_compound_licensing
        }


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


def get_declared_license_info_from_top_level_key_files(codebase):
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


def get_declared_license_expressions_from_top_level_key_files(codebase):
    """
    Return a list of "declared" license expressions as detected in key files
    from top-level directories.

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
            for detected_license_expression in getattr(child, 'license_expressions', []) or []:
                declared.append(detected_license_expression)
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
    Check if at least one of the licenses in `declared_licenses` is good.

    If so, return True. Otherwise, return False.
    """
    return any(
        is_good_license(declared_license)
        for declared_license
        in declared_licenses
    )


CONFLICTING_LICENSE_CATEGORIES = (
    'Commercial',
    'Copyleft',
    'Proprietary Free',
    'Source Available',
)


def check_declared_license_categories(declared_licenses):
    """
    Check whether or not if the licenses in `declared_licenses` are permissively
    licensed, or compatible with permissive licenses.

    If so, return True. Otherwise, return False.
    """

    for category in CONFLICTING_LICENSE_CATEGORIES:
        if category in declared_licenses:
            return False
    return True


def check_for_conflicting_licenses(other_licenses):
    """
    Check if there is a license in `other_licenses` that conflicts with
    permissive licenses.

    If so, return True. Otherwise, return False.
    """
    for license_info in other_licenses:
        if (
            license_info.get('category', '')
            in CONFLICTING_LICENSE_CATEGORIES
        ):
            return True
    return False


def group_license_expressions(declared_license_expressions):
    """
    Return a tuple that contains two list of license expressions.

    The first list in the tuple contains unique license expressions with "AND",
    "OR, or "WITH" in it.

    The second list in the tuple contains unique license
    expressions without "AND", "OR", or "WITH".
    """
    unique_declared_license_expressions = set(declared_license_expressions)
    joined_expressions = []
    single_expressions = []
    for declared_license_expression in unique_declared_license_expressions:
        if (
            'AND' in declared_license_expression
            or 'OR' in declared_license_expression
            or 'WITH' in declared_license_expression
        ):
            joined_expressions.append(declared_license_expression)
        else:
            single_expressions.append(declared_license_expression)

    licensing = Licensing()
    unique_joined_expressions = []
    seen_joined_expression = []
    len_joined_expressions = len(joined_expressions)
    for i, j in enumerate(joined_expressions):
        starting_index = i + 1
        if starting_index > len_joined_expressions:
            break
        for j1 in joined_expressions[starting_index:]:
            if licensing.is_equivalent(j, j1):
                if (
                    j not in unique_joined_expressions
                    and j not in seen_joined_expression
                ):
                    unique_joined_expressions.append(j)
                    seen_joined_expression.append(j1)

    return unique_joined_expressions, single_expressions


def check_ambiguous_license_expression(declared_license_expressions):
    # Get lists of unique license expressions
    unique_joined_expressions, single_expressions = group_license_expressions(
        declared_license_expressions
    )
    if not unique_joined_expressions and not single_expressions:
        return True

    # Group single expressions to joined expressions to see if single
    # expressions are accounted for in a joined expression
    single_expressions_by_joined_expressions = {
        joined_expression: []
        for joined_expression
        in unique_joined_expressions
    }
    not_in_joined_expressions = []
    # check to see if the single expression is in the joined expression
    for joined_expression in unique_joined_expressions:
        for expression in single_expressions:
            if expression not in joined_expression:
                not_in_joined_expressions.append(expression)
            else:
                single_expressions_by_joined_expressions[joined_expression].append(expression)

    if len(single_expressions_by_joined_expressions) == 1 and not not_in_joined_expressions:
        return False
    else:
        return True
