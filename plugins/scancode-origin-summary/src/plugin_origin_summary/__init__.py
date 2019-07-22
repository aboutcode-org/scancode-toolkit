#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from collections import Counter
from collections import defaultdict
from collections import OrderedDict

import attr

from cluecode.copyrights import CopyrightDetector
from commoncode.text import python_safe_name
from license_expression import Licensing
from packagedcode import get_package_instance
from packagedcode.utils import combine_expressions
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, unicode) and a or repr(a) for a in args))


@attr.s
class Fileset(object):
    """
    A grouping of files that share the same origin
    """
    # TODO: have an attribute for key files (one that strongly determines origin)
    type=attr.ib()
    identifier = attr.ib(default=None)
    resources = attr.ib(default=attr.Factory(list))
    package = attr.ib(default=None)
    core_license_expression = attr.ib(default=None)
    core_holders = attr.ib(default=attr.Factory(list))
    context_license_expression = attr.ib(default=None)
    context_holders = attr.ib(default=attr.Factory(list))

    def to_dict(self, **kwargs):
        """
        Return an OrderedDict that contains the attributes (except for `resources`) and values for this Fileset
        """
        def dict_fields(attr, value):
            if attr.name in ('resources', ):
                return False
            return True
        return attr.asdict(self, filter=dict_fields, dict_factory=OrderedDict)


@post_scan_impl
class OriginSummary(PostScanPlugin):
    """
    A post-scan plugin that returns Filesets for summarized resources.

    This plugin summarizes resources by:
    - Packages
    - Copyright holders and license expression, i

    Summarize copyright holders and license expressions to the directory level if a copyright holder
    or license expression is detected in 75% or more of total files in a directory
    """
    codebase_attributes = dict(
        filesets=attr.ib(default=attr.Factory(list))
    )

    resource_attributes = dict(
        origin_summary=attr.ib(default=attr.Factory(OrderedDict)),
        summarized_to=attr.ib(default=attr.Factory(list))
    )

    sort_order = 8

    options = [
        CommandLineOption(('--origin-summary',),
            is_flag=True, default=False,
            help='Summarize copyright holders and license expressions to the directory level '
                 'if a copyright holder or license expression is detected in 75% or more of '
                 'total files in a directory.',
            help_group=POST_SCAN_GROUP
        ),
        CommandLineOption(('--origin-summary-threshold',),
            is_flag=False, type=float,
            help='Set a custom threshold for origin summarization.',
            required_options=['origin_summary'],
            help_group=POST_SCAN_GROUP
        )
    ]

    def is_enabled(self, origin_summary, **kwargs):
        return origin_summary

    def process_codebase(self, codebase, origin_summary_threshold=None, **kwargs):
        # Collect Filesets
        filesets = []
        root = codebase.get_resource(0)
        if hasattr(root, 'packages') and hasattr(root, 'copyrights') and hasattr(root, 'licenses'):
            filesets.extend(get_package_filesets(codebase))
        if hasattr(root, 'copyrights') and hasattr(root, 'licenses'):
            filesets.extend(get_license_exp_holders_filesets(codebase, origin_summary_threshold=origin_summary_threshold))

        if not filesets:
            return

        # Process Filesets (if needed)
        filesets = process_license_exp_holders_filesets(filesets)

        # Add Filesets to codebase
        for index, fileset in enumerate(filesets, start=1):
            if fileset.type == 'package':
                identifier = fileset.package.purl
            else:
                # TODO: Consider adding license expression to be part of identifier
                core_holders = '_'.join(fileset.core_holders)
                context_holders = '_'.join(fileset.context_holders)
                holders = core_holders or context_holders
                # We do not want the identifier to be too long
                holders = holders[:65]
                if holders:
                    identifier = python_safe_name('{}_{}'.format(holders, index))
                else:
                    identifier = index
            fileset.identifier = identifier
            for resource in fileset.resources:
                resource.summarized_to.append(identifier)
                resource.save(codebase)
            codebase.attributes.filesets.append(fileset.to_dict())

        # Dedupe and sort identifiers in summarized_to
        for resource in codebase.walk(topdown=True):
            resource.summarized_to = sorted(set(resource.summarized_to))
            resource.save(codebase)


def get_package_filesets(codebase):
    """
    Yield a Fileset for each detected package in the codebase
    """
    for resource in codebase.walk(topdown=False):
        for package_data in resource.packages:
            package = get_package_instance(package_data)
            package_resources = list(package.get_package_resources(resource, codebase))
            package_license_expression = package.license_expression
            package_copyright = package.copyright

            package_holders = []
            if package_copyright:
                numbered_lines = [(0, package_copyright)]
                for _, holder, _, _ in CopyrightDetector().detect(numbered_lines,
                        copyrights=False, holders=True, authors=False, include_years=False):
                    package_holders.append(holder)

            discovered_license_expressions = []
            discovered_holders = []
            for package_resource in package_resources:
                # If a resource is part of a package Fileset, then it cannot be part of any other type of Fileset
                package_resource.extra_data['in_package_fileset'] = True
                package_resource.save(codebase)

                package_resource_license_expression = combine_expressions(package_resource.license_expressions)
                package_resource_holders = package_resource.holders
                if not package_resource_license_expression and not package_resource_holders:
                    continue
                discovered_license_expressions.append(package_resource_license_expression)
                discovered_holders.extend(h.get('value') for h in package_resource_holders)

            # Remove top-level package license and NoneTypes from discovered licenses
            discovered_license_expressions = [lic for lic in discovered_license_expressions if lic]
            # Remove top-level holders and NoneTypes from discovered holders
            discovered_holders = [holder for holder in discovered_holders if holder]

            combined_discovered_license_expression = combine_expressions(discovered_license_expressions)
            if combined_discovered_license_expression:
                simplified_discovered_license_expression = str(Licensing().parse(combined_discovered_license_expression).simplify())
            else:
                simplified_discovered_license_expression = None

            yield Fileset(
                type='package',
                resources=package_resources,
                package=package,
                core_license_expression=package_license_expression,
                core_holders=sorted(package_holders),
                context_license_expression=simplified_discovered_license_expression,
                context_holders=set(sorted(discovered_holders))
            )


def get_license_exp_holders_filesets(codebase, origin_summary_threshold=None):
    """
    Yield a Fileset for each directory where 75% or more of the files have the same license
    expression and copyright holders
    """
    origin_translation_table = {}
    for resource in codebase.walk(topdown=False):
        # TODO: Consider facets for later

        if resource.is_file or resource.extra_data.get('in_package_fileset'):
            continue

        children = resource.children(codebase)
        if not children:
            continue

        # Collect license expression and holders count for stat-based summarization
        origin_count = Counter()
        for child in children:
            if child.extra_data.get('in_package_fileset'):
                continue
            if child.is_file:
                license_expression = combine_expressions(child.license_expressions)
                holders = tuple(h['value'] for h in child.holders)
                if not license_expression or not holders:
                    continue
                origin = holders, license_expression
                origin_key = ''.join(holders) + license_expression
                origin_translation_table[origin_key] = origin
                origin_count[origin_key] += 1
            else:
                # We are in a subdirectory
                child_origin_count = child.extra_data.get('origin_count', {})
                if not child_origin_count:
                    continue
                origin_count.update(child_origin_count)

        if origin_count:
            resource.extra_data['origin_count'] = origin_count
            resource.save(codebase)

            # TODO: When there is a tie, we need to be explicit and consistent about the tiebreaker
            # TODO: Consider creating two filesets instead of tiebreaking
            origin_key, top_count = origin_count.most_common(1)[0]
            if is_majority(top_count, resource.files_count, origin_summary_threshold):
                majority_holders, majority_license_expression = origin_translation_table[origin_key]
                resource.origin_summary['license_expression'] = majority_license_expression
                resource.origin_summary['holders'] = majority_holders
                resource.origin_summary['count'] = top_count
                resource.save(codebase)

                fs = create_license_exp_holders_fileset(resource, codebase)
                if fs:
                    yield fs

    # Yield a Fileset for root if there is a majority
    root = codebase.get_resource(0)
    fs = create_license_exp_holders_fileset(root, codebase)
    if fs and not root.extra_data.get('in_package_fileset'):
        yield fs


def is_majority(count, files_count, threshold=None):
    """
    Return True if `count` divided by `files_count` is greater than or equal to `threshold`
    """
    # TODO: Increase this and test with real codebases
    threshold = threshold or 0.75
    return count / files_count >= threshold


def create_license_exp_holders_fileset(resource, codebase):
    """
    Return a Fileset for `resource` if it can be summarized on license expression and holders
    """
    license_expression = resource.origin_summary.get('license_expression')
    holders = resource.origin_summary.get('holders')
    if license_expression and holders:
        fileset_resources = get_fileset_resources(resource, codebase)
        if fileset_resources:
            return Fileset(
                type='license-holders',
                resources=fileset_resources,
                core_license_expression=license_expression,
                core_holders=holders
            )


def get_fileset_resources(resource, codebase):
    """
    Return a list of resources to be used to create a Fileset from `resource`
    """
    license_expression = resource.origin_summary.get('license_expression')
    holders = resource.origin_summary.get('holders')
    if not license_expression and holders:
        return
    resources = [] if resource.extra_data.get('in_package_fileset') else [resource]
    for r in resource.walk(codebase, topdown=False):
        if r.extra_data.get('in_package_fileset'):
            continue
        if ((r.is_file
                and combine_expressions(r.license_expressions) == license_expression
                and r.holders == holders)
                or (r.is_dir
                and r.origin_summary.get('license_expression', '') == license_expression
                and r.origin_summary.get('holders', '') == holders)):
            resources.append(r)
    return resources


def process_license_exp_holders_filesets(filesets):
    """
    Combine Filesets with the same license expression and holders
    into a single Fileset
    """
    origin_translation_table = {}
    filesets_by_holders_license_expression = defaultdict(list)
    for fileset in filesets:
        if fileset.type != 'license-holders':
            # We yield the other Filesets that we don't handle
            yield fileset
            continue
        origin = fileset.core_holders, fileset.core_license_expression
        origin_key = ''.join(fileset.core_holders) + fileset.core_license_expression
        origin_translation_table[origin_key] = origin
        filesets_by_holders_license_expression[origin_key].append(fileset)

    for origin_key, filesets in filesets_by_holders_license_expression.items():
        fileset_resources = []
        for fileset in filesets:
            fileset_resources.extend(fileset.resources)
        fileset_holders, fileset_license_expression = origin_translation_table[origin_key]
        yield Fileset(
            type='license-holders',
            resources=fileset_resources,
            core_license_expression=fileset_license_expression,
            core_holders=fileset_holders
        )
