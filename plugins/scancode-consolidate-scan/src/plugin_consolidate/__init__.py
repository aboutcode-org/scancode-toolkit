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
class Consolidation(object):
    """
    A grouping of files that share the same origin. Other clues found in the
    codebase are stored in `other_license_expression` and `other_holders`
    """
    # TODO: Add file counts for proper accounting
    identifier = attr.ib(default=None)
    core_license_expression = attr.ib(default=None)
    other_license_expression = attr.ib(default=None)
    consolidated_core_copyright = attr.ib(default=None)
    consolidated_other_copyright = attr.ib(default=None)
    core_holders = attr.ib(default=attr.Factory(list))
    other_holders = attr.ib(default=attr.Factory(list))
    resources = attr.ib(default=attr.Factory(list))

    def to_dict(self, **kwargs):
        def dict_fields(attr, value):
            if attr.name in ('resources', ):
                return False
            return True
        self.consolidated_core_copyright = self.consolidate_core_copyright()
        self.consolidated_other_copyright = self.consolidate_other_copyright()
        return attr.asdict(self, filter=dict_fields, dict_factory=OrderedDict)

    def consolidate_core_copyright(self):
        # TODO: Verify and test that we are generating detectable copyrights
        holders = list(self.core_holders) + list(self.other_holders)
        if holders:
            return 'Copyright (c) {}'.format(', '.join(holders))

    def consolidate_other_copyright(self):
        # TODO: Verify and test that we are generating detectable copyrights
        other_holders = list(self.other_holders)
        if other_holders:
            return 'Copyright (c) {}'.format(', '.join(other_holders))


@attr.s
class ConsolidatedComponent(object):
    # TODO: have an attribute for key files (one that strongly determines origin)
    type=attr.ib()
    consolidation = attr.ib()

    def to_dict(self, **kwargs):
        c = OrderedDict(type=self.type)
        c.update(self.consolidation.to_dict())
        return c


@attr.s
class ConsolidatedPackage(object):
    package = attr.ib()
    consolidation = attr.ib()

    def to_dict(self, **kwargs):
        package = self.package.to_dict()
        package.update(self.consolidation.to_dict())
        return package


@post_scan_impl
class Consolidator(PostScanPlugin):
    """
    A post-scan plugin that returns Components for consolidated resources.

    This plugin consolidates resources by:
    - Packages
    - Copyright holders and license expression
    """
    codebase_attributes = OrderedDict(
        consolidated_components=attr.ib(default=attr.Factory(list)),
        consolidated_packages=attr.ib(default=attr.Factory(list))
    )

    resource_attributes = dict(
        consolidated_to=attr.ib(default=attr.Factory(list))
    )

    sort_order = 8

    options = [
        CommandLineOption(('--consolidate',),
            is_flag=True, default=False,
            help='Return a list of consolidated packages and a list of consolidated components',
            help_group=POST_SCAN_GROUP
        )
    ]

    def is_enabled(self, consolidate, **kwargs):
        return consolidate

    def process_codebase(self, codebase, **kwargs):
        # Collect ConsolidatedPackages and ConsolidatedComponents
        # TODO: Have a "catch-all" Component for the things that we haven't grouped
        packages = []
        components = []
        root = codebase.root
        if hasattr(root, 'packages') and hasattr(root, 'copyrights') and hasattr(root, 'licenses'):
            packages.extend(get_consolidated_packages(codebase))
        if hasattr(root, 'copyrights') and hasattr(root, 'licenses'):
            components.extend(get_license_holders_consolidated_components(codebase))

        if not packages and not components:
            return

        # Process ConsolidatedPackages and ConsolidatedComponents (if needed)
        # components = combine_license_holders_consolidated_components(components)

        # Add ConsolidatedPackages and ConsolidatedComponents to top-level codebase attributes
        codebase.attributes.consolidated_packages = consolidated_packages = []
        for index, package in enumerate(packages, start=1):
            if not package.consolidation.resources:
                continue
            identifier = python_safe_name('{}_{}'.format(package.package.purl, index))
            package.consolidation.identifier = identifier
            for resource in package.consolidation.resources:
                resource.consolidated_to.append(identifier)
                resource.save(codebase)
            consolidated_packages.append(package.to_dict())

        codebase.attributes.consolidated_components = consolidated_components = []
        for index, component in enumerate(components, start=1):
            # Skip ConsolidatedComponents that do not have files in them
            if not component.consolidation.resources:
                continue
            # TODO: Consider adding license expression to be part of name
            holders = '_'.join(component.consolidation.core_holders)
            other_holders = '_'.join(component.consolidation.other_holders)
            holders = holders or other_holders
            # We do not want the name to be too long
            holders = holders[:65]
            if holders:
                identifier = python_safe_name('{}_{}'.format(holders, index))
            else:
                identifier = index
            component.consolidation.identifier = identifier
            for resource in component.consolidation.resources:
                resource.consolidated_to.append(identifier)
                resource.save(codebase)
            consolidated_components.append(component.to_dict())

        # Dedupe and sort names in consolidated_to
        for resource in codebase.walk(topdown=True):
            resource.consolidated_to = sorted(set(resource.consolidated_to))
            resource.save(codebase)


def get_consolidated_packages(codebase):
    """
    Yield a ConsolidatedPackage for each detected package in the codebase
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
                # If a resource is part of a package Component, then it cannot be part of any other type of Component
                package_resource.extra_data['in_package_component'] = True
                package_resource.save(codebase)

                package_resource_license_expression = combine_expressions(package_resource.license_expressions)
                package_resource_holders = package_resource.holders
                if not package_resource_license_expression and not package_resource_holders:
                    continue
                discovered_license_expressions.append(package_resource_license_expression)
                discovered_holders.extend(h.get('value') for h in package_resource_holders)

            # Remove NoneTypes from discovered licenses
            discovered_license_expressions = [lic for lic in discovered_license_expressions if lic]
            # Remove NoneTypes from discovered holders
            discovered_holders = [holder for holder in discovered_holders if holder]

            combined_discovered_license_expression = combine_expressions(discovered_license_expressions)
            if combined_discovered_license_expression:
                simplified_discovered_license_expression = str(Licensing().parse(combined_discovered_license_expression).simplify())
            else:
                simplified_discovered_license_expression = None

            c = Consolidation(
                core_license_expression=package_license_expression,
                other_license_expression=simplified_discovered_license_expression,
                core_holders=sorted(set(package_holders)),
                other_holders=sorted(set(discovered_holders)),
                resources=package_resources,
            )
            yield ConsolidatedPackage(
                package=package,
                consolidation=c
            )


def get_license_holders_consolidated_components(codebase):
    """
    Yield a ConsolidatedComponent for each directory where 75% or more of the files have the
    same license expression and copyright holders
    """
    # TODO: Create Consolidated Components for the 25% or less of files that
    # aren't part of the majority
    # TODO: Take license score into account
    root = codebase.root
    if root.extra_data.get('in_package_component'):
        return

    origin_translation_table = {}
    for resource in codebase.walk(topdown=False):
        # TODO: Consider facets for later

        if resource.is_file or resource.extra_data.get('in_package_component'):
            continue

        children = resource.children(codebase)
        if not children:
            continue

        # Collect license expression and holders count for stat-based summarization
        origin_count = Counter()
        for child in children:
            if child.extra_data.get('in_package_component'):
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
            # TODO: Consider creating two components instead of tiebreaking
            origin_key, top_count = origin_count.most_common(1)[0]
            if is_majority(top_count, resource.files_count):
                majority_holders, majority_license_expression = origin_translation_table[origin_key]
                resource.extra_data['origin_summary_license_expression'] = majority_license_expression
                resource.extra_data['origin_summary_holders'] = majority_holders
                resource.extra_data['origin_summary_count'] = top_count
                resource.save(codebase)

                # Create consolidated components for a child that has a majority
                # that is different than the one we have now
                for child in children:
                    origin_summary_license_expression = child.extra_data.get('origin_summary_license_expression')
                    origin_summary_holders = child.extra_data.get('origin_summary_holders')
                    if (origin_summary_license_expression and origin_summary_holders
                            and origin_summary_license_expression != majority_license_expression
                            and origin_summary_holders != majority_holders):
                        c = create_license_holders_consolidated_component(child, codebase)
                        if c:
                            yield c
            else:
                # If there is no majority, we see if any of our child directories had majorities
                for child in children:
                    c = create_license_holders_consolidated_component(child, codebase)
                    if c:
                        yield c

    # Yield a Component for root if there is a majority
    c = create_license_holders_consolidated_component(root, codebase)
    if c:
        yield c


def is_majority(count, files_count):
    """
    Return True if `count` divided by `files_count` is greater than or equal to
    `threshold`
    """
    # TODO: Increase this and test with real codebases
    threshold = 0.75
    return count / files_count >= threshold


def create_license_holders_consolidated_component(resource, codebase):
    """
    Return a ConsolidatedComponent for `resource` if it can be summarized on license
    expression and holders
    """
    license_expression = resource.extra_data.get('origin_summary_license_expression')
    holders = resource.extra_data.get('origin_summary_holders')
    if license_expression and holders:
        component_resources = get_consolidated_component_resources(resource, codebase)
        if component_resources:
            c = Consolidation(
                core_license_expression=license_expression,
                core_holders=holders,
                resources=component_resources,
            )
            return ConsolidatedComponent(
                type='license-holders',
                consolidation=c
            )


def get_consolidated_component_resources(resource, codebase):
    """
    Return a list of resources to be used to create a ConsolidatedComponent from `resource`
    """
    license_expression = resource.extra_data.get('origin_summary_license_expression')
    holders = resource.extra_data.get('origin_summary_holders')
    if not license_expression and holders:
        return
    resources = [] if resource.extra_data.get('in_package_component') else [resource]
    for r in resource.walk(codebase, topdown=False):
        if r.extra_data.get('in_package_component'):
            continue
        resource_holders = tuple(h.get('value') for h in r.holders)
        if ((r.is_file
                and combine_expressions(r.license_expressions) == license_expression
                and resource_holders == holders)
                or (r.is_dir
                and r.extra_data.get('origin_summary_license_expression', '') == license_expression
                and r.extra_data.get('origin_summary_holders', tuple()) == holders)):
            resources.append(r)
    return resources


def combine_license_holders_consolidated_components(components):
    """
    Combine ConsolidatedComponents with the same license expression and holders into a
    single ConsolidatedComponent
    """
    origin_translation_table = {}
    components_by_holders_license_expression = defaultdict(list)
    for component in components:
        origin = component.consolidation.core_holders, component.consolidation.core_license_expression
        origin_key = ''.join(component.consolidation.core_holders) + component.consolidation.core_license_expression
        origin_translation_table[origin_key] = origin
        components_by_holders_license_expression[origin_key].append(component)

    for origin_key, components in components_by_holders_license_expression.items():
        component_resources = []
        for component in components:
            component_resources.extend(component.consolidation.resources)
        component_holders, component_license_expression = origin_translation_table[origin_key]
        c = Consolidation(
            core_license_expression=component_license_expression,
            core_holders=component_holders,
            resources=component_resources,
        )
        yield ConsolidatedComponent(
            type='license-holders',
            consolidation=c,
        )
