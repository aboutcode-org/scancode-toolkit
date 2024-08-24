#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from license_expression import Licensing
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl

from packagedcode.utils import combine_expressions
from licensedcode.cache import get_cache
from licensedcode.detection import get_matches_from_detection_mappings
from licensedcode.detection import LicenseMatchFromResult

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
class LicenseClarityScore(PostScanPlugin):
    """
    Compute a License clarity score at the codebase level.
    """

    codebase_attributes = dict(summary=attr.ib(default=attr.Factory(dict)))

    run_order = 5
    sort_order = 2

    options = [
        PluggableCommandLineOption(
            ('--license-clarity-score',),
            is_flag=True,
            default=False,
            help='Compute a summary license clarity score at the codebase level.',
            help_group=POST_SCAN_GROUP,
            required_options=[
                'classify',
            ],
        )
    ]

    def is_enabled(self, license_clarity_score, **kwargs):
        return license_clarity_score

    def process_codebase(self, codebase, license_clarity_score, **kwargs):
        if TRACE:
            logger_debug('LicenseClarityScore:process_codebase')
        codebase_resources= get_codebase_resources(codebase)
        scoring_elements,_, declared_license_expression = compute_license_score(resources= codebase_resources)
        codebase.attributes.summary['declared_license_expression'] = declared_license_expression
        codebase.attributes.summary['license_clarity_score'] = scoring_elements.to_dict()


def compute_license_score(resources):
    """
    Return a mapping of scoring elements and a license clarity score computed at
    the codebase/package level.

    The license clarity score is a value from 0-100 calculated by combining the
    weighted values determined for each of the scoring elements:

    Declared license:
    - When true, indicates that the software package licensing is documented at
      top-level or well-known locations in the software project, typically in a
      package manifest, NOTICE, LICENSE, COPYING or README file.
    - Scoring Weight = 40

    Identification precision:
    - Indicates how well the license statement(s) of the software identify known
      licenses that can be designated by precise keys (identifiers) as provided in
      a publicly available license list, such as the ScanCode LicenseDB, the SPDX
      license list, the OSI license list, or a URL pointing to a specific license
      text in a project or organization website.
    - Scoring Weight = 40

    License texts:
    - License texts are provided to support the declared license expression in
      files such as a package manifest, NOTICE, LICENSE, COPYING or README.
    - Scoring Weight = 10

    Declared copyright:
    - When true, indicates that the software package copyright is documented at
      top-level or well-known locations in the software project, typically in a
      package manifest, NOTICE, LICENSE, COPYING or README file.
    - Scoring Weight = 10

    Ambiguous compound licensing
    - When true, indicates that the software has a license declaration that
      makes it difficult to construct a reliable license expression, such as in
      the case of multiple licenses where the conjunctive versus disjunctive
      relationship is not well defined.
    - Scoring Weight = -10

    Conflicting license categories
    - When true, indicates the declared license expression of the software is in
      the permissive category, but that other potentially conflicting categories,
      such as copyleft and proprietary, have been detected in lower level code.
    - Scoring Weight = -20
    """

    scoring_elements = ScoringElements()
    license_detections = get_field_values_from_resources(
        resources,
        field_name='license_detections',
        key_files_only=True,
    )
    license_match_mappings = get_matches_from_detection_mappings(license_detections)
    license_matches = LicenseMatchFromResult.from_dicts(license_match_mappings)
    declared_license_expressions = get_field_values_from_resources(
        resources,
        field_name='detected_license_expression',
        key_files_only=True,
        is_string=True,
    )
    declared_license_expressions_spdx=get_field_values_from_resources(
        resources,
        field_name='detected_license_expression_spdx',
        key_files_only=True,
        is_string=True,
    )

    unique_declared_license_expressions = unique(declared_license_expressions)
    unique_declared_license_expressions_spdx= unique(declared_license_expressions_spdx)
    declared_license_categories = get_license_categories(license_matches)

    copyrights = get_field_values_from_resources(
        resources,
        field_name='copyrights',
        key_files_only=True,
    )
    holders = get_field_values_from_resources(
        resources,
        field_name='holders',
        key_files_only=True,
    )
    notice_texts = get_field_values_from_resources(
        resources,
        field_name='notice_text',
        key_files_only=True,
    )
    other_license_expressions = get_field_values_from_resources(
        resources,
        field_name='detected_license_expression',
        key_files_only=False,
        is_string=True,
    )
    other_license_expressions_spdx= get_field_values_from_resources(
        resources,
        field_name='detected_license_expression_spdx',
        key_files_only=False,
        is_string=True,
    )
    
    # Populating the Package Attributes 
    copyright_values = [copyright.get('copyright') for copyright in copyrights if copyright.get('copyright')]
    joined_copyrights = ", ".join(copyright_values) if copyright_values else None
    
    holder_values = [holder.get('holder') for holder in holders if holder.get('holder')]
    joined_holders = ", ".join(holder_values) if holder_values else None
    
    notice_text_values = [notice_text.get('notice_text') for notice_text in notice_texts if notice_text.get('notice_text')]
    joined_notice_text = ", ".join(notice_text_values) if notice_text_values else None
    
    unique_other_license_expressions = unique(other_license_expressions)
    unique_other_license_expressions_spdx= unique(other_license_expressions_spdx)
    other_license_expressions=[]
    other_license_expressions_spdx=[]
    for other_license_expression in unique_other_license_expressions:
        if other_license_expression not in unique_declared_license_expressions:
            other_license_expressions.append(other_license_expression)
    
    for other_license_expression_spdx in unique_other_license_expressions_spdx:
        if other_license_expression_spdx not in unique_declared_license_expressions_spdx:
            other_license_expressions_spdx.append(other_license_expression_spdx)
            
    joined_other_license_expressions = ", ".join(other_license_expressions) if other_license_expressions else None
    joined_other_license_expressions_spdx = ", ".join(other_license_expressions_spdx) if other_license_expressions_spdx else None

    if not joined_other_license_expressions:
        joined_other_license_expressions = None
    
    packageAttrs= PackageSummaryAttributes(
        copyright = joined_copyrights,
        holder = joined_holders,
        notice_text = joined_notice_text,
        other_license_expression= joined_other_license_expressions,
        other_license_expression_spdx= joined_other_license_expressions_spdx
    )

    other_license_detections = get_field_values_from_resources(
        resources,
        field_name='license_detections',
        key_files_only=False,
    )
    other_license_match_mappings = get_matches_from_detection_mappings(other_license_detections)
    other_license_matches = LicenseMatchFromResult.from_dicts(other_license_match_mappings)

    scoring_elements.declared_license = bool(license_matches)
    if scoring_elements.declared_license:
        scoring_elements.score += 40

    scoring_elements.identification_precision = check_declared_licenses(license_matches)
    if scoring_elements.identification_precision:
        scoring_elements.score += 40

    scoring_elements.has_license_text = check_for_license_texts(license_matches)
    if scoring_elements.has_license_text:
        scoring_elements.score += 10

    scoring_elements.declared_copyrights = bool(copyrights)
    if scoring_elements.declared_copyrights:
        scoring_elements.score += 10

    is_permissively_licensed = check_declared_license_categories(declared_license_categories)
    if is_permissively_licensed:
        scoring_elements.conflicting_license_categories = check_for_conflicting_licenses(
            other_license_matches
        )
        if scoring_elements.conflicting_license_categories and scoring_elements.score > 0:
            scoring_elements.score -= 20

    declared_license_expression = get_primary_license(unique_declared_license_expressions)

    if not declared_license_expression:
        # If we cannot get a single primary license, then we combine and simplify the license expressions from key files
        combined_declared_license_expression = combine_expressions(
            unique_declared_license_expressions
        )
        if combined_declared_license_expression:
            declared_license_expression = str(
                Licensing().parse(combined_declared_license_expression).simplify()
            )
        scoring_elements.ambiguous_compound_licensing = True
        if scoring_elements.score > 0:
            scoring_elements.score -= 10
            
    return scoring_elements, packageAttrs, declared_license_expression or None


def unique(objects):
    """
    Return a list of unique objects keeping the original order.
    """
    uniques = []
    seen = set()
    for obj in objects:
        if obj not in seen:
            uniques.append(obj)
            seen.add(obj)
    return uniques


@attr.s()
class ScoringElements:
    score = attr.ib(default=0)
    declared_license = attr.ib(default=False)
    identification_precision = attr.ib(default=False)
    has_license_text = attr.ib(default=False)
    declared_copyrights = attr.ib(default=False)
    conflicting_license_categories = attr.ib(default=False)
    ambiguous_compound_licensing = attr.ib(default=False)

    def to_dict(self):
        return {
            'score': self.score,
            'declared_license': self.declared_license,
            'identification_precision': self.identification_precision,
            'has_license_text': self.has_license_text,
            'declared_copyrights': self.declared_copyrights,
            'conflicting_license_categories': self.conflicting_license_categories,
            'ambiguous_compound_licensing': self.ambiguous_compound_licensing,
        }

@attr.s()
class PackageSummaryAttributes:
    copyright= attr.ib(default=None)
    holder= attr.ib(default=None)
    notice_text= attr.ib(default=None)
    other_license_expression= attr.ib(default=None)
    other_license_expression_spdx= attr.ib(default=None)
    
    def to_dict(self):
        return attr.asdict(self, dict_factory=dict)

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
    is_license_clue=LicenseFilter(min_score=100, min_coverage=100),
)


def is_good_license(license_match_object):
    """
    Return True if a `detected license` mapping is considered to be a high quality
    conclusive match.
    """
    score = license_match_object.score()
    coverage = license_match_object.coverage()
    relevance = license_match_object.rule.relevance
    match_types = dict(
        [
            ('is_license_text', license_match_object.rule.is_license_text),
            ('is_license_notice', license_match_object.rule.is_license_notice),
            ('is_license_reference', license_match_object.rule.is_license_reference),
            ('is_license_tag', license_match_object.rule.is_license_tag),
            ('is_license_intro', license_match_object.rule.is_license_intro),
            ('is_license_clue', license_match_object.rule.is_license_clue),
        ]
    )
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
        if (
            score >= thresholds.min_score
            and coverage >= thresholds.min_coverage
            and relevance >= thresholds.min_relevance
        ):
            return True

    return False


def check_declared_licenses(license_match_objects):
    """
    Check if at least one of the licenses in `license_match_objects` is good.

    If so, return True. Otherwise, return False.
    """
    return any(is_good_license(license_match_object) for license_match_object in license_match_objects)

def get_field_values_from_resources(
    resources,
    field_name,
    key_files_only=False,
    is_string=False,
):
    """
    Return a list of values from the `field_name` field of the Resources from
    the provided `resources`.
    
    If `key_files_only` is True, then we only return the field values from
    Resources classified as key files.

    If `key_files_only` is False, then we return the field values from Resources
    that are not classified as key files.
    """
    values = []
    
    for resource in resources:
        if key_files_only:
            if not resource.get('is_key_file', False):
                continue
        else:
            if resource.get('is_key_file', False):
                continue
        if is_string:
            value = resource.get(field_name)
            if value:
                values.append(value)
        else:
            for value in resource.get(field_name, []):
                values.append(value)
                    
    return values

def get_codebase_resources(codebase):
    """
    Get resources for the codebase.
    """
    codebase_resources= []
    for resource in codebase.walk(topdown=True):
        codebase_resources.append(resource.to_dict())
        
    return codebase_resources

def get_categories_from_match(license_match, licensing=Licensing()):
    """
    Return a list of license category strings from a single LicenseMatch mapping.
    """
    license_keys = licensing.license_keys(license_match.rule.license_expression)
    cache = get_cache()
    return [
        cache.db[license_key].category
        for license_key in license_keys
    ]


def get_license_categories(license_match_objects):
    """
    Return a list of license category strings from `license_match_objects`
    """
    license_categories = []

    for match in license_match_objects:
        for category in get_categories_from_match(match):
            if category not in license_categories:
                license_categories.append(category)
    return license_categories


def check_for_license_texts(license_match_objects):
    """
    Check if any license in `license_match_objects` is from a license text or notice.

    If so, return True. Otherwise, return False.
    """
    for license_match_object in license_match_objects:
        if any(
            [
                license_match_object.rule.is_license_text,
                license_match_object.rule.is_license_notice,
            ]
        ):
            return True
    return False


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


def check_for_conflicting_licenses(other_license_match_objects):
    """
    Check if there is a license in `other_licenses` that conflicts with
    permissive licenses.

    If so, return True. Otherwise, return False.
    """
    for license_match_object in other_license_match_objects:
        for category in get_categories_from_match(license_match_object):
            if category in CONFLICTING_LICENSE_CATEGORIES:
                return True
    return False


def group_license_expressions(unique_license_expressions):
    """
    Return a tuple that contains two list of license expressions.

    The first list in the tuple contains unique license expressions with "AND",
    "OR, or "WITH" in it.

    The second list in the tuple contains unique license
    expressions without "AND", "OR", or "WITH".
    """
    joined_expressions = []
    single_expressions = []
    for license_expression in unique_license_expressions:
        if (
            'AND' in license_expression
            or 'OR' in license_expression
            or 'WITH' in license_expression
        ):
            joined_expressions.append(license_expression)
        else:
            single_expressions.append(license_expression)

    licensing = Licensing()
    unique_joined_expressions = []
    seen_joined_expression = []
    len_joined_expressions = len(joined_expressions)
    if len_joined_expressions > 1:
        for i, j in enumerate(joined_expressions, start=1):
            if i > len_joined_expressions:
                break
            for j1 in joined_expressions[i:]:
                if licensing.is_equivalent(j, j1):
                    if j not in unique_joined_expressions and j not in seen_joined_expression:
                        unique_joined_expressions.append(j)
                        seen_joined_expression.append(j1)
    else:
        unique_joined_expressions = joined_expressions

    return unique_joined_expressions, single_expressions


def get_primary_license(declared_license_expressions):
    """
    Return a primary license expression string from
    `declared_license_expressions` or an empty string if a primary license
    expression cannot be determined.

    We determine if a list of `declared_license_expressions` has a primary
    license if we can resolve the `declared_license_expressions` into one
    expression.
    """
    unique_declared_license_expressions = unique(declared_license_expressions)
    # If we only have a single unique license expression, then we do not have
    # any ambiguity about the licensing
    if len(unique_declared_license_expressions) == 1:
        return unique_declared_license_expressions[0]

    unique_joined_expressions, single_expressions = group_license_expressions(
        unique_declared_license_expressions
    )

    if not unique_joined_expressions:
        # If we do not have any joined expressions, but multiple single
        # expressions remaining, then we have license ambiguity
        if len(single_expressions) == 1:
            return single_expressions[0]
        else:
            return None

    # Group single expressions to joined expressions to see if single
    # expressions are accounted for in a joined expression
    single_expressions_by_joined_expressions = {
        joined_expression: [] for joined_expression in unique_joined_expressions
    }
    not_in_joined_expressions = []
    # Check to see if the single expression is in the joined expression
    for joined_expression in unique_joined_expressions:
        for expression in single_expressions:
            if expression not in joined_expression:
                not_in_joined_expressions.append(expression)
            else:
                single_expressions_by_joined_expressions[joined_expression].append(expression)

    # If we have a single joined license expression and no license expressions
    # that have not been associated with a joined license expression, then we do
    # not have any ambiguity about the license
    if len(single_expressions_by_joined_expressions) == 1 and not not_in_joined_expressions:
        return next(iter(single_expressions_by_joined_expressions))
    else:
        return None