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
from itertools import chain

import attr
from license_expression import Licensing

from commoncode.datautils import Mapping
from licensedcode.cache import get_licenses_db
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
    codebase_attributes = dict(license_clarity_score=Mapping(
        help='Computed license clarity score as mapping containing the score '
             'proper and each scoring elements.'))

    sort_order = 110

    options = [
        CommandLineOption(('--license-clarity-score',),
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
        scoring_elements = compute_license_score(codebase, **kwargs)
        codebase.attributes.license_clarity_score.update(scoring_elements)


def compute_license_score(codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a mapping of scoring elements and a license clarity score computed at
    the codebase level.
    """

    score = 0
    scoring_elements = OrderedDict(score=score)

    kwargs.update(dict(min_score=min_score))

    for element in SCORING_ELEMENTS:
        element_score = element.scorer(codebase, **kwargs)
        if element.is_binary:
            scoring_elements[element.name] = bool(element_score)
            element_score = 1 if element_score else 0
        else:
            scoring_elements[element.name] = round(element_score, 2)

        score += int(element_score * element.weight)
        if TRACE:
            logger_debug(
                'compute_license_score: element:', element, 'element_score: ',
                element_score, ' new score:', score)

    scoring_elements['score'] = score
    return scoring_elements


def get_declared_license_keys(codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a list of declared license keys found in packages and key files.
    """
    return (
        get_declared_license_keys_in_key_files(codebase, min_score)
      +get_declared_license_keys_in_packages(codebase)
    )


def get_declared_license_keys_in_packages(codebase, **kwargs):
    """
    Return a list of declared license keys found in packages.

    A package manifest (such as Maven POM file or an npm package.json file)
    contains structured declared license information. This is further normalized
    as a license_expression. We extract the list of licenses from the normalized
    license expressions.
    """
    packages = chain.from_iterable(
        getattr(res, 'packages', []) or [] for res in codebase.walk(topdown=True))

    licensing = Licensing()
    detected_good_licenses = []
    for package in packages:
        expression = package.get('license_expression')
        if expression:
            exp = licensing.parse(expression, validate=False, strict=False, simple=True)
            keys = licensing.license_keys(exp, unique=True)
            detected_good_licenses.extend(keys)
    return detected_good_licenses


def get_declared_license_keys_in_key_files(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a list of "declared" license keys from the expressions as detected in
    key files.

    A project has specific key file(s) at the top level of its code hierarchy
    such as LICENSE, NOTICE or similar (and/or a package manifest) containing
    structured license information such as an SPDX license expression or SPDX
    license identifier: when such a file contains "clearly defined" declared
    license information, we return this.

    Note: this ignores facets.
    """
    declared = []
    for resource in codebase.walk(topdown=True):
        if not resource.is_key_file:
            continue

        for detected_license in getattr(resource, 'licenses', []) or []:
            if detected_license['score'] < min_score:
                declared.append('unknown')
            else:
                declared.append(detected_license['key'])
    return declared


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
    Return True if a Resource licenses are all detected with a score above
    min_score and is generally a "good license" detection-wise.
    """
    licenses = getattr(resource, 'licenses', []) or []

    if not licenses:
        return False

    for detected_license in licenses:
        # the license score must be above some threshold
        if detected_license['score'] < min_score:
            return False

        # and not an "unknown" license
        if is_unknown_license(detected_license['key']):
            return False

    return True


def has_spdx_licenses(resource):
    """
    Return True if a Resource licenses are all known SPDX licenses.
    """
    for detected_license in getattr(resource, 'licenses', []) or []:
        if detected_license and detected_license.get('spdx_license_key'):
            return True
    return False


def get_spdx_keys():
    """
    Return a set of ScanCode license keys for licenses that are listed in SPDX.
    """
    licenses = get_licenses_db()
    spdx = {}
    for lic in licenses.values():
        if (lic.spdx_license_key or lic.other_spdx_license_keys):
            spdx.add(lic.key)
    return frozenset(spdx)


_spdx_keys = None

def is_spdx_license(lic_key, spdx_keys=_spdx_keys):
    """
    Return True if a license key is for some lesser known or unknown license.
    """
    global _spdx_keys
    if not spdx_keys:
        _spdx_keys = spdx_keys = get_spdx_keys()

    return lic_key in spdx_keys


def is_unknown_license(lic_key):
    """
    Return True if a license key is for some lesser known or unknown license.
    """
    return lic_key.startswith(('unknown', 'other-',)) or 'unknown' in lic_key


def has_unkown_licenses(resource):
    """
    Return True if some Resource licenses are unknown.
    """
    return not any(is_unknown_license(lic['key'])
                   for lic in getattr(resource, 'licenses', []) or [])


def is_using_only_spdx_licenses(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return True if all file-level detected licenses are SPDX licenses.
    """
    return all(has_spdx_licenses(res) for res in codebase.walk() if res.is_file)


def has_consistent_key_and_file_level_licenses(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return True if the file-level licenses are consistent with top level key
    files licenses.
    """
    key_files_licenses, other_files_licenses = get_unique_licenses(codebase, min_score)

    if (key_files_licenses
    and key_files_licenses == other_files_licenses
    and not any(is_unknown_license(l) for l in key_files_licenses)):
        return True
    else:
        return False


def get_unique_licenses(codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
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
        if not (resource.is_key_file or is_core_facet(resource)):
            # we only cover core code or top level, key filess
            continue

        if resource.is_key_file:
            license_keys = key_license_keys
        else:
            license_keys = other_license_keys

        for detected_license in getattr(resource, 'licenses', []) or []:
            if detected_license['score'] < min_score:
                license_keys.add('unknown')
            else:
                license_keys.add(detected_license['key'])

    return key_license_keys, other_license_keys


def get_detected_license_keys_with_full_text(codebase, min_score=MIN_GOOD_LICENSE_SCORE,
                                             key_files_only=False, **kwargs):
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

        if key_files_only and not resource.is_key_file:
            continue

        for detected_license in getattr(resource, 'licenses', []) or []:
            if detected_license['score'] < min_score:
                continue
            if not detected_license['matched_rule']['is_license_text']:
                continue
            license_keys.add(detected_license['key'])

    return license_keys


def has_full_text_in_key_files_for_all_licenses(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return True if the full text of all licenses is preset in the codebase key,
    top level files.
    """
    return _has_full_text(codebase, min_score, key_files_only=True, **kwargs)


def has_full_text_for_all_licenses(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return True if the full text of all licenses is preset in the codebase.
    """
    return _has_full_text(codebase, min_score, key_files_only=False, **kwargs)


def _has_full_text(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, key_files_only=False, **kwargs):
    """
    Return True if the full text of all licenses is preset in the codebase.
    Consider only key files if key_files_only is True.
    """

    key_files_license_keys, other_files_license_keys = get_unique_licenses(
        codebase, min_score, **kwargs)

    if TRACE:
        logger_debug(
            '_has_full_text: key_files_license_keys:', key_files_license_keys,
            'other_files_license_keys:', other_files_license_keys)

    all_keys = key_files_license_keys & other_files_license_keys
    keys_with_license_text = get_detected_license_keys_with_full_text(
        codebase, min_score, key_files_only, **kwargs)

    if TRACE:
        logger_debug(
            '_has_full_text: keys_with_license_text:', keys_with_license_text)

    return all_keys and (all_keys == keys_with_license_text)


def get_file_level_license_and_copyright_coverage(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a float between 0 and 1 that represent the proportions of files that
    have a license and a copyright vs. all files.
    """
    scoring_element = 0
    covered_files, files_count = get_other_licenses_and_copyrights_counts(codebase, min_score)

    if TRACE:
        logger_debug('compute_license_score:covered_files:',
                     covered_files, 'files_count:', files_count)

    if files_count:
        scoring_element = covered_files / files_count

        if TRACE:
            logger_debug('compute_license_score:scoring_element:', scoring_element)

    return scoring_element


def get_other_licenses_and_copyrights_counts(
        codebase, min_score=MIN_GOOD_LICENSE_SCORE, **kwargs):
    """
    Return a tuple of (count of files with a license/copyright, total count of
    files).

    Do files that can contain licensing and copyright information reliably carry
    such information? This is based on a percentage of files in the core facet
    of the project that have both:

    - A license text, notice or an SPDX-License-Identifier and,
    - A copyright statement in standard (e.g. recognized) format.

    Here "reliably" means that these are reliably detected by tool(s) with a
    high level of confidence This is a progressive element that is computed
    based on:

    - LICCOP:  the number of files with a license notice and copyright statement
    - TOT: the total number of files

    """
    total_files_count = 0
    files_with_good_license_and_copyright_count = 0
    files_with_a_license_count = 0
    files_with_a_good_license_count = 0
    files_with_a_copyright_count = 0

    for resource in codebase.walk():
        # consider non-key files
        if resource.is_key_file or not resource.is_file:
            continue

        # ... in the core facet
        if not is_core_facet(resource):
            continue

        total_files_count += 1

        licenses = getattr(resource, 'licenses', []) or []
        # ... with a license
        if licenses:
            files_with_a_license_count += 1

        is_public_domain = [l['key'] for l in licenses] == 'public-domain'

        copyrights = getattr(resource, 'copyrights', []) or []

        # ... with a copyright, unless public-domain
        if copyrights or (not copyrights and is_public_domain):
            files_with_a_copyright_count += 1

        # ... where the license is a "good one"
        if  has_good_licenses(resource, min_score):
            files_with_a_good_license_count += 1
            if copyrights:
                files_with_good_license_and_copyright_count += 1

    return files_with_good_license_and_copyright_count, total_files_count


@attr.s
class ScoringElement(object):
    is_binary = attr.ib()
    name = attr.ib()
    scorer = attr.ib()
    weight = attr.ib()


declared = ScoringElement(
    is_binary=True,
    name='has_declared_license_in_key_files',
    scorer=get_declared_license_keys,
    weight=30)

discovered = ScoringElement(
    is_binary=False,
    name='file_level_license_and_copyright_coverage',
    scorer=get_file_level_license_and_copyright_coverage,
    weight=25)

consistency = ScoringElement(
    is_binary=True,
    name='has_consistent_key_and_file_level_licenses',
    scorer=has_consistent_key_and_file_level_licenses,
    weight=15)

spdx_licenses = ScoringElement(
    is_binary=True,
    name='is_using_only_spdx_licenses',
    scorer=is_using_only_spdx_licenses,
    weight=15)

full_text = ScoringElement(
    is_binary=True,
    name='has_full_text_for_all_licenses',
    scorer=has_full_text_for_all_licenses,
    weight=15)

# not used for now
unkown = ScoringElement(
    is_binary=True,
    name='has_unkown_licenses',
    scorer=has_unkown_licenses,
    weight=15)

# not used for now
full_text_in_key_files = ScoringElement(
    is_binary=True,
    name='has_full_text_in_key_files_for_all_licenses',
    scorer=has_full_text_in_key_files_for_all_licenses,
    weight=15)


SCORING_ELEMENTS = [
    declared,
    discovered,
    consistency,
    spdx_licenses,
    full_text
]
