#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import logging

from collections import defaultdict
from os.path import exists
from os.path import isdir

import attr
import click
import saneyaml

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from commoncode.filetype import is_file
from commoncode.filetype import is_readable
from licensedcode.detection import get_license_keys_from_detections
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl

TRACE = os.environ.get('SCANCODE_DEBUG_LICENSE_POLICY', False)


def logger_debug(*args):
    pass


if TRACE:

    logger = logging.getLogger(__name__)

    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def validate_policy_path(ctx, param, value):
    """
    Validate the ``value`` of the policy file path
    """
    policy = value
    if policy:
        if not is_file(location=value, follow_symlinks=True):
            raise click.BadParameter(f"policy file is not a regular file: {value!r}")

        if not is_readable(location=value):
            raise click.BadParameter(f"policy file is not readable: {value!r}")
        policy = load_license_policy(value)
    return policy


@post_scan_impl
class LicensePolicy(PostScanPlugin):
    """
    Add the "license_policy" attribute to a resouce if it contains a
    detected license key that is found in the license_policy.yml file
    """

    resource_attributes = dict(license_policy=attr.ib(default=attr.Factory(list)))

    run_order = 9
    sort_order = 9

    options = [
        PluggableCommandLineOption(('--license-policy',),
            multiple=False,
            callback=validate_policy_path,
            metavar='FILE',
            help='Load a License Policy file and apply it to the scan at the '
                 'Resource level.',
            help_group=POST_SCAN_GROUP,
        )
    ]

    def is_enabled(self, license_policy, **kwargs):
        return license_policy

    def process_codebase(self, codebase, license_policy, **kwargs):
        """
        Populate a license_policy mapping with four attributes: license_key, label,
        icon, and color_code at the File Resource level.
        """
        if not self.is_enabled(license_policy):
            return

        # license_policy has been validated through a callback and contains data
        # loaded from YAML
        policies = license_policy.get('license_policies', [])
        if not policies:
            codebase.errors.append(f'ERROR: License Policy file is empty')
            return

        # get a list of unique license policies from the license_policy file
        dupes = get_duplicate_policies(policies)
        if dupes:
            dupes = '\n'.join(repr(d) for d in dupes.items())
            codebase.errors.append(f'ERROR: License Policy file contains duplicate entries:\n{dupes}')
            return

        # apply policy to Resources if they contain an offending license
        for resource in codebase.walk(topdown=True):
            if not resource.is_file:
                continue

            try:
                resource_license_keys = get_license_keys_from_detections(resource.license_detections)

            except AttributeError:
                # add license_policy regardless if there is license info or not
                resource.license_policy = []
                codebase.save_resource(resource)
                continue

            license_policies = []
            for key in resource_license_keys:
                for policy in policies:
                    if key == policy.get('license_key'):
                        # Apply the policy to the Resource
                        license_policies.append(policy)

            resource.license_policy = sorted(license_policies, key=lambda d: d['license_key'])
            codebase.save_resource(resource)


def get_duplicate_policies(policies):
    """
    Return a list of duplicated policy mappings based on the license key.
    Return an empty list if there are no duplicates.
    """
    if not policies:
        return []

    policies_by_license = defaultdict(list)
    for policy in policies:
        license_key = policy.get('license_key')
        policies_by_license[license_key].append(policy)
    return {key: pols for key, pols in policies_by_license.items() if len(pols) > 1}


def load_license_policy(license_policy_location):
    """
    Return a license policy mapping loaded from a license policy file.
    """
    if not license_policy_location:
        return {}

    if not exists(license_policy_location):
        raise click.BadParameter(f"policy file does not exists: {license_policy_location!r} ")

    if isdir(license_policy_location):
        raise click.BadParameter(f"policy file is a directory: {license_policy_location!r} ")

    try:
        with open(license_policy_location, 'r') as conf:
            conf_content = conf.read()
        policy = saneyaml.load(conf_content)
        if not policy:
            raise click.BadParameter(f"policy file is empty: {license_policy_location!r}")
        if "license_policies" not in policy:
            raise click.BadParameter(f"policy file is missing a 'license_policies' attribute: {license_policy_location!r} ")
    except Exception as e:
        if isinstance(e, click.BadParameter):
            raise e
        else:
            raise click.BadParameter(f"policy file is not a well formed or readable YAML file: {license_policy_location!r} {e!r}") from e
    return policy

