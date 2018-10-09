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

from collections import OrderedDict

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP
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
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))

"""
A plugin to compute a licensing clarity score as designed in ClearlyDefined
"""


# minimum score to consider a license detection as good.
MIN_GOOD_LICENSE_SCORE = 80


@post_scan_impl
class LicenseClarityScore(PostScanPlugin):
    """
    Compute a License clarity score at the codebase level.
    """
    codebase_attributes = dict(license_score=attr.ib(default=attr.Factory(OrderedDict)))
    sort_order = 110

    options = [
        CommandLineOption(('--license-clarity-score',),
            is_flag=True,
            default=False,
            help='Compute a summary license clarity score at the codebase level.',
            help_group=POST_SCAN_GROUP,
            requires=['classify', 'license', 'copyright'],
        ),
    ]

    def is_enabled(self, license_clarity_score, **kwargs):
        return license_clarity_score

    def process_codebase(self, codebase, license_clarity_score, **kwargs):
        if TRACE:
            logger_debug('LicenseClarityScore:process_codebase')
        scoring_elements = compute_license_score(codebase, **kwargs)
        codebase.attributes.license_score.update(scoring_elements)


def compute_license_score(codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a mapping of scoring elements and a license clarity score computed at
    the codebase level.
    """

    score = 0
    scoring_elements = OrderedDict(score=score)

    # FIXME: separate the compute of each score element from applying the weights

    ############################################################################
    top_level_declared_licenses_weight = 30
    has_top_level_declared_licenses = get_top_level_declared_licenses(codebase, min_score)
    scoring_elements['has_top_level_declared_licenses'] = bool(has_top_level_declared_licenses)
    if has_top_level_declared_licenses:
        score += top_level_declared_licenses_weight
        if TRACE:
            logger_debug(
                'compute_license_score:has_top_level_declared_licenses:',
                has_top_level_declared_licenses, 'score:', score)

    ############################################################################
    file_level_license_and_copyright_weight = 25
    file_level_license_and_copyright_coverage = 0
    files_with_lic_copyr, files_count = get_other_licenses_and_copyrights_counts(codebase, min_score)
    if TRACE:
        logger_debug('compute_license_score:files_with_lic_copyr:',
                     files_with_lic_copyr, 'files_count:', files_count)

    scoring_elements['file_level_license_and_copyright_coverage'] = 0


    if files_count:
        file_level_license_and_copyright_coverage = files_with_lic_copyr / files_count
        score += int(file_level_license_and_copyright_coverage * file_level_license_and_copyright_weight)
        scoring_elements['file_level_license_and_copyright_coverage'] = file_level_license_and_copyright_coverage
        if TRACE:
            logger_debug('compute_license_score:file_level_license_and_copyright_coverage:',
                         file_level_license_and_copyright_coverage, 'score:', score)

    ############################################################################
    license_consistency_weight = 15
    has_consistent_key_and_file_level_license = False
    key_files_license_keys, other_files_license_keys = get_unique_licenses(codebase, min_score)

    if key_files_license_keys and key_files_license_keys == other_files_license_keys:
        has_consistent_key_and_file_level_license = True

    scoring_elements['has_consistent_key_and_file_level_license'] = has_consistent_key_and_file_level_license

    if has_consistent_key_and_file_level_license:
        score += license_consistency_weight
        if TRACE:
            logger_debug(
                'compute_license_score:has_consistent_key_and_file_level_license:',
                has_consistent_key_and_file_level_license, 'score:', score)


    ############################################################################
    spdx_standard_licenses_weight = 15
    has_all_spdx_licenses = all(has_spdx_licenses(res) for res in codebase.walk() if res.is_file)

    scoring_elements['has_all_spdx_licenses'] = has_all_spdx_licenses

    if has_all_spdx_licenses:
        score += spdx_standard_licenses_weight
        if TRACE:
            logger_debug(
                'compute_license_score:',
                'has_all_spdx_licenses:',
                has_all_spdx_licenses, 'score:', score)

    ############################################################################
    license_texts_weight = 15

    all_keys = key_files_license_keys & other_files_license_keys
    keys_with_license_text = get_detected_license_keys_with_full_text(codebase, min_score)

    has_all_license_texts = all_keys == keys_with_license_text
    scoring_elements['has_all_license_texts'] = has_all_license_texts

    if has_all_license_texts:
        score += license_texts_weight

    scoring_elements['score'] = score
    return scoring_elements


def get_top_level_declared_licenses(codebase, min_score=MIN_GOOD_LICENSE_SCORE):
    """
    A project has specific key file(s) at the top level of its code hierarchy
    such as LICENSE, NOTICE or similar (and/or a package manifest) containing
    structured license information such as an SPDX license expression or SPDX
    license identifier, and the file(s) contain "clearly defined" declared
    license information (a license declaration such as a license expression
    and/or a series of license statements or notices).

    Note: this ignores facets.
    """
    key_files = (res for res in codebase.walk(topdown=True) if is_key_file(res))

    detected_good_licenses = []
    for resource in key_files:
        if resource.scan_errors:
            continue
        # TODO: should we also ignore or penalize non SPDX licenses?

        for detected_license in resource.licenses:
            """
            "licenses": [
              {
                "score": 23.0,
                "start_line": 1,
                "end_line": 1,
                "matched_rule": {
                  "identifier": "lgpl-2.1_38.RULE",
                  "license_expression": "lgpl-2.1",
                  "licenses": [
                    "lgpl-2.1"
                  ]
                },
            """
            if detected_license['score'] < min_score:
                continue

            items = ('path', resource.path,)
            items += tuple((k, v) for k, v in detected_license.items()
                if (
                    k in ('score', 'start_line', 'end_line', 'matched_rule',)
                )
            )
            detected_good_licenses.append(items)
    return detected_good_licenses


def is_key_file(resource):
    """
    Return True if a Resource is considered as a "key file".
    """
    return (
        resource.is_file
        and resource.is_top_level
        and (resource.is_readme
            or resource.is_legal
            or resource.is_manifest)
    )


def is_core_facet(resource, core_facet=facet.FACET_CORE):
    """
    Return True if the resource is in the core facet.
    If we do not have facets, everything is considered as being core by default.
    """
    has_facets = hasattr(resource, 'facets')
    if not has_facets:
        return True
    # facets is a list
    return not resource.facets or core_facet in resource.facets


def has_good_licenses(resource, min_score=MIN_GOOD_LICENSE_SCORE):
    """
    Return True if a Resource licenses are all detected with a score above min_score.
    """
    if not resource.licenses:
        return False

    if resource.scan_errors:
        return False

    for detected_license in resource.licenses:
        if detected_license['score'] < min_score:
            return False
    return True


def has_spdx_licenses(resource):
    """
    Return True if a Resource licenses are all known SPDX licenses.
    """
    if resource.scan_errors:
        return False

    for detected_license in resource.licenses:
        if not detected_license.get('spdx_license_key'):
            return False
    return True


def get_unique_licenses(codebase, min_score=MIN_GOOD_LICENSE_SCORE):
    """
    Return a tuple of two sets of license keys found in the codebase with at least min_score:
    - the set license found in key files
    - the set license found in non-key files

    This is only for files in the core facet.
    """
    key_license_keys = set()
    other_license_keys = set()

    for resource in codebase.walk():
        # FIXME: consider only text, source-like files for now
        if not resource.is_file:
            continue
        if not (is_key_file(resource) or is_core_facet(resource)):
            continue

        if is_key_file(resource):
            license_keys = key_license_keys
        else:
            license_keys = other_license_keys

        for detected_license in resource.licenses:
            if detected_license['score'] < min_score:
                continue
            license_keys.add(detected_license['key'])

    return key_license_keys, other_license_keys


def get_detected_license_keys_with_full_text(codebase, min_score=MIN_GOOD_LICENSE_SCORE):
    """
    Return a set of license keys for which at least one detection includes the
    full license text.

    This is for any files in the core facet or not.
    """
    license_keys = set()

    for resource in codebase.walk():
        # FIXME: consider only text, source-like files for now
        if not resource.is_file:
            continue

        for detected_license in resource.licenses:
            if detected_license['score'] < min_score:
                continue
            if not detected_license['matched_rule']['is_license_text']:
                continue
            license_keys.add(detected_license['key'])

    return license_keys


def get_other_licenses_and_copyrights_counts(codebase, min_score=MIN_GOOD_LICENSE_SCORE):
    """
    Return a tuple of (count of files with a license/copyright, total count of
    files).

    Do files that can contain licensing and copyright information reliably carry
    such information? This is based on a percentage of files in the core facet
    of the project that have both:
    - A license statement such as a text, notice or an SPDX-License-Identifier and,
    - A copyright statement in standard format.

    Here "reliably" means that these are reliably detected by tool(s) with a
    high level of confidence This is a progressive element that is computed
    based on:

    - LICCOP:  the number of files with a license notice and copyright statement
    - TOT: the total number of files

    """
    total_files_count = 0
    files_with_good_license_and_copyright_count = 0

    for resource in codebase.walk():
        # FIXME: consider only text, source-like files for now
        if is_key_file(resource) or not resource.is_file:
            continue
        if not is_core_facet(resource):
            continue

        total_files_count += 1

        if resource.scan_errors:
            continue

        if not (resource.licenses or resource.copyrights):
            continue

        if not has_good_licenses(resource, min_score):
            continue

        files_with_good_license_and_copyright_count += 1

    return files_with_good_license_and_copyright_count, total_files_count
