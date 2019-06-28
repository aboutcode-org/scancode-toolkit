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

from commoncode.text import python_safe_name
from packagedcode import get_package_instance
from packagedcode.utils import combine_expressions
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


# Tracing flags
TRACE = True


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
class Summary(object):
    identifier = attr.ib()
    license_expression = attr.ib()
    holders = attr.ib()
    type=attr.ib()


@attr.s
class Fileset(object):
    type=attr.ib()
    identifier = attr.ib(default=-1) # maybe
    primary_resource = attr.ib(default=None) # in case of packages, will be package root
    resources = attr.ib(default=attr.Factory(list))
    package = attr.ib(default=None)
    declared_license_expression = attr.ib(default=None)
    declared_holders = attr.ib(default=None)
    discovered_license_expression = attr.ib(default=None)
    discovered_holders = attr.ib(default=None)


@post_scan_impl
class OriginSummary(PostScanPlugin):
    """
    Summarize copyright holders and license expressions to the directory level if a copyright holder
    or license expression is detected in 75% or more of total files in a directory
    """
    codebase_attributes = dict(
        summaries=attr.ib(default=attr.Factory(list))
    )

    resource_attributes = dict(
        origin_summary=attr.ib(default=attr.Factory(OrderedDict)),
        summarized_to=attr.ib(default=None, type=str)
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
        root = codebase.get_resource(0)

        # TODO: Should we activate or deactivate certain summarization options based on
        # the attributes that are present in the codebase?
        if not hasattr(root, 'copyrights') or not hasattr(root, 'licenses'):
            # TODO: Raise warning(?) if these fields are not there
            return

        filesets = []
        # Collecters should be independent and not depend on the result of another
        collecters = [get_package_filesets, get_license_exp_holder_fileset]
        for collecter in collecters:
            filesets.extend(collecter(codebase, origin_summary_threshold=origin_summary_threshold))

        process_filesets(filesets, codebase)


def get_package_filesets(codebase, **kwargs):
    """
    Yield filesets for each detected package in the codebase
    """
    for resource in codebase.walk(topdown=False):
        for package_data in resource.packages:
            package = get_package_instance(package_data)
            yield Fileset(
                type='package',
                resources=list(package.get_package_resources(resource, codebase)),
                # TODO: add package declared license and holders
                # TODO: may be better as primary license
                primary_resource=resource,
                package=package
            )


def get_license_exp_holder_fileset(codebase, origin_summary_threshold=None, **kwargs):
    def collect_fileset_resources(resource, codebase):
        license_expression = resource.origin_summary.get('license_expression')
        holders = resource.origin_summary.get('holders')
        if not license_expression and holders:
            return
        resources = []
        for c in resource.walk(codebase, topdown=False):
            if ((c.is_file and combine_expressions(c.license_expressions) == license_expression
                    and c.holders == holders)
                    or (c.is_dir and c.origin_summary.get('license_expression', '') == license_expression
                    and c.origin_summary.get('holders', '') == holders)):
                resources.append(c)
        return resources

    # Summarize origin clues to directory level and tag summarized Resources
    for resource in codebase.walk(topdown=False):
        # TODO: Consider facets for later

        if resource.is_file:
            continue

        children = resource.children(codebase)
        if not children:
            continue

        # Collect license expression and holders count for stat-based summarization
        origin_count = Counter()
        child_rids = []
        for child in children:
            if child.is_file:
                license_expression = combine_expressions(child.license_expressions)
                holders = tuple(h['value'] for h in child.holders)
                if not license_expression or not holders:
                    continue
                origin = holders, license_expression
                origin_count[origin] += 1
            else:
                # We are in a subdirectory
                child_origin_count = child.extra_data.get('origin_count', {})
                if not child_origin_count:
                    continue
                origin_count.update(child_origin_count)
            child_rids.append(child.rid)

        if origin_count:
            resource.extra_data['origin_count'] = origin_count
            resource.save(codebase)

            origin, top_count = origin_count.most_common(1)[0]
            # TODO: Check for contradictions when performing summarizations
            if is_majority(top_count, resource.files_count, origin_summary_threshold):
                holders, license_expression = origin
                resource.origin_summary['license_expression'] = license_expression
                resource.origin_summary['holders'] = holders
                resource.origin_summary['count'] = top_count
                codebase.save_resource(resource)

            # Check to see which one of the children are part of the majority and create filesets from that
            else:
                for child in resource.children(codebase):
                    child_license_expression = child.origin_summary.get('license_expression')
                    child_holders = child.origin_summary.get('holders')
                    if child_license_expression and child_holders:
                        yield Fileset(
                            type='license-holder',
                            resources=collect_fileset_resources(child, codebase),
                            primary_resource=child,
                            discovered_license_expression=child_license_expression,
                            discovered_holders=child_holders
                        )

    # Yield a Fileset for root if there is a majority
    root = codebase.get_resource(0)
    root_license_expression = root.origin_summary.get('license_expression')
    root_holders = root.origin_summary.get('holders')
    if root_license_expression and root_holders:
        yield Fileset(
            type='license-holder',
            resources=collect_fileset_resources(root, codebase),
            primary_resource=root,
            discovered_license_expression=root_license_expression,
            discovered_holders=root_holders
        )


def is_majority(count, files_count, threshold=None):
    """
    Return True if `count` divided by `files_count` is greater than or equal to `threshold`
    """
    # TODO: Increase this and test with real codebases
    threshold = threshold or 0.75
    return count / files_count >= threshold


def process_filesets(filesets, codebase, **kwargs):
    """
    Create summaries based on collected filesets
    """
    identifier = 0
    for fileset in filesets:
        summary_type = fileset.type
        if summary_type == 'package':
            license_expression = fileset.package.license_expression
            holders = None
        if summary_type == 'license-holder':
            license_expression = fileset.discovered_license_expression
            holders = fileset.discovered_holders
        codebase.attributes.summaries.append(
            Summary(
                identifier=identifier,
                license_expression=license_expression or None,
                holders=holders or None,
                type=summary_type,
            )
        )
        for res in fileset.resources:
            res.summarized_to = identifier
            res.save(codebase)
        identifier += 1


def tag_nr_files(codebase, **kwargs):
    # TODO: Load set of extensions to NR from somewhere
    nr_exts = []
    # Summarize origin clues to directory level and tag summarized Resources
    for resource in codebase.walk(topdown=False):
        if resource.extension in nr_exts:
            resource.extra_data['NR'] = True
            resource.save(codebase)
