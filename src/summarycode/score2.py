#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from itertools import chain

import attr
from license_expression import Licensing

from commoncode.datautils import Mapping
from licensedcode.cache import get_licenses_db
from licensedcode import models
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from summarycode import facet


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

    score = 0
    scoring_elements = dict(score=score)

    for element in SCORING_ELEMENTS:
        element_score = element.scorer(codebase)
        if element.is_binary:
            scoring_elements[element.name] = bool(element_score)
            element_score = 1 if element_score else 0
        else:
            scoring_elements[element.name] = round(element_score, 2) or 0

        score += int(element_score * element.weight)
        if TRACE:
            logger_debug(
                'compute_license_score: element:', element, 'element_score: ',
                element_score, ' new score:', score)

    scoring_elements['score'] = score or 0
    return scoring_elements


def get_declared_license_keys_in_key_files_from_top_level_dir(codebase):
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
                if not is_good_license(detected_license):
                    declared.append('unknown')
                else:
                    declared.append(detected_license['key'])
    return declared


def get_license_text_from_key_files(codebase):
    """
    Return a list of license keys that were detected from license text.
    """
    license_keys_with_text = []
    for resource in codebase.walk(topdown=True):
        if not (resource.is_dir and resource.is_top_level):
            continue
        for child in resource.walk(codebase):
            if not child.is_key_file:
                continue
            for detected_license in getattr(child, 'licenses', []) or []:
                matched_rule = detected_license.get('matched_rule', {})
                is_license_text = matched_rule.get('is_license_text')
                if not is_license_text:
                    continue
                license_keys_with_text.append(detected_license['key'])
    return license_keys_with_text


def get_copyrights_from_key_files(codebase):
    """
    Return a list of copyright statements from key files
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


@attr.s
class ScoringElement(object):
    is_binary = attr.ib()
    name = attr.ib()
    scorer = attr.ib()
    weight = attr.ib()


declared = ScoringElement(
    is_binary=True,
    name='declared',
    scorer=get_declared_license_keys_in_key_files_from_top_level_dir,
    weight=40)


license_text = ScoringElement(
    is_binary=True,
    name='license_text',
    scorer=get_license_text_from_key_files,
    weight=10)


copyrights = ScoringElement(
    is_binary=True,
    name='copyrights',
    scorer=get_copyrights_from_key_files,
    weight=10)


SCORING_ELEMENTS = [
    declared,
    license_text,
    copyrights,
]
