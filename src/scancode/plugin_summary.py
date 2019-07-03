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
        if (not hasattr(root, 'copyrights')
                or not hasattr(root, 'licenses')
                or not hasattr(root, 'packages')):
            # TODO: Raise warning(?) if these fields are not there
            return

        filesets = []
        # Collecters should be independent and not depend on the result of another
        fileset_collecters = [get_package_filesets, get_license_exp_holders_filesets]
        for collecter in fileset_collecters:
            filesets.extend(collecter(codebase, origin_summary_threshold=origin_summary_threshold))

        processed_filesets = filesets
        fileset_processors = [process_license_exp_holders_filesets]
        for processor in fileset_processors:
            processed_filesets = list(processor(processed_filesets))

        codebase.attributes.summaries = create_summaries(processed_filesets, codebase)


def get_package_filesets(codebase, **kwargs):
    """
    Yield a Fileset for each detected package in the codebase
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


def get_license_exp_holders_filesets(codebase, origin_summary_threshold=None, **kwargs):
    """
    Yield a Fileset for each directory where 75% or more of the files have the same license
    expression and copyright holders ONLY IF its parent directory has no majority license expression
    and copyright holders. This means each yielded Fileset is a "local maximum" in terms of being
    able to summarize on license expression and copyright holders.

    We yield a fileset for the root Resource in `codebase` if there is a majority license expression
    and copyright holder, such that we can properly report every instance of summarization
    """
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
                majority_holders, majority_license_expression = origin
                resource.origin_summary['license_expression'] = majority_license_expression
                resource.origin_summary['holders'] = majority_holders
                resource.origin_summary['count'] = top_count
                resource.save(codebase)

        # If we have a summary for the directory we're in, we check to see if any of our children
        # have summaries and yield filesets for them
        # We do this to make sure we report each fileset that has a majority, so it doesn't get
        # lost when another license expression, holders combination is more dominant later on
        if resource.origin_summary:
            for child in children:
                if child.is_file:
                    continue
                # We only care about the children with different expressions and holders from ours
                if (child.origin_summary['license_expression'] == majority_license_expression
                        and child.origin_summary['holders'] == majority_holders):
                    continue
                fs = create_license_exp_holders_fileset(child, codebase)
                if fs:
                    yield fs

    # Yield a Fileset for root if there is a majority
    root = codebase.get_resource(0)
    fs = create_license_exp_holders_fileset(root, codebase)
    if fs:
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
                type='license-exp-holders',
                resources=fileset_resources,
                primary_resource=resource,
                discovered_license_expression=license_expression,
                discovered_holders=holders
            )


def get_fileset_resources(resource, codebase):
    """
    Return a list of resources to be used to create a Fileset from `resource`
    """
    license_expression = resource.origin_summary.get('license_expression')
    holders = resource.origin_summary.get('holders')
    if not license_expression and holders:
        return
    resources = [resource]
    for r in resource.walk(codebase, topdown=False):
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
    filesets_by_holders_lic_exp = defaultdict(list)
    for fileset in filesets:
        if not (fileset.type == 'license-exp-holders'):
            # We yield the other Filesets that we don't handle
            yield fileset
            continue
        origin = fileset.discovered_holders, fileset.discovered_license_expression
        filesets_by_holders_lic_exp[origin].append(fileset)

    for (fileset_holders, fileset_license_expression), filesets in filesets_by_holders_lic_exp.items():
        fileset_resources = []
        for fileset in filesets:
            fileset_resources.extend(fileset.resources)
        yield Fileset(
            type='license-exp-holders',
            resources=fileset_resources,
            discovered_license_expression=fileset_license_expression,
            discovered_holders=fileset_holders
        )


def create_summaries(filesets, codebase):
    """
    Return a list of summaries from `filesets`
    """
    # TODO: Introduce notion of precedence for package data
    # TODO: Process filesets further before creating summaries
    summaries = []
    identifier = 0
    for fileset in filesets:
        summary_type = fileset.type
        license_expression = None
        holders = None
        if summary_type == 'package':
            license_expression = fileset.package.license_expression
        if summary_type == 'license-exp-holders':
            license_expression = fileset.discovered_license_expression
            holders = fileset.discovered_holders
        for res in fileset.resources:
            res.summarized_to = identifier
            res.save(codebase)
        summaries.append(
            Summary(
                identifier=identifier,
                license_expression=license_expression,
                holders=holders,
                type=summary_type,
            )
        )
        identifier += 1
    return summaries


def get_nr_fileset(codebase, **kwargs):
    """
    Yield a Fileset for all Resources that are not to be reported
    """
    # TODO: Load set of extensions to NR from somewhere
    nr_exts = []
    resources = []
    for resource in codebase.walk(topdown=False):
        if resource.extension in nr_exts:
            resources.append(resource)
    yield Fileset(
        type='nr',
        resources=resources
    )
