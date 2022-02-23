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

# Set to True to enable debug tracing
TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:

    def logger_debug(*args):
        pass


@post_scan_impl
class LicensesReference(PostScanPlugin):
    """
    Add a reference list of all licenses data and text.
    """
    codebase_attributes = dict(licenses_reference=attr.ib(default=attr.Factory(list)))

    sort_order = 500

    options = [
        PluggableCommandLineOption(('--licenses-reference',),
            is_flag=True, default=False,
            help='Include a reference of all the licenses referenced in this '
                 'scan with the data details and full texts.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, licenses_reference, **kwargs):
        return licenses_reference

    def process_codebase(self, codebase, licenses_reference, **kwargs):
        from licensedcode.cache import get_licenses_db
        licensing = Licensing()

        license_keys = set()

        for resource in codebase.walk():
            licexps = getattr(resource, 'license_expressions', []) or []
            for expression in licexps:
                if expression:
                    license_keys.update(licensing.license_keys(expression))

        packages = getattr(codebase, 'packages', []) or []
        for package in packages:
            # FXIME: license_expression attribute name is changing soon
            expression = package.get('license_expression')
            if expression:
                license_keys.update(licensing.license_keys(expression))

                resource.save(codebase)

        db = get_licenses_db()
        for key in sorted(license_keys):
            license_details = db[key].to_dict(
                include_ignorables=False,
                include_text=True,
            )
            codebase.attributes.licenses_reference.append(license_details)
