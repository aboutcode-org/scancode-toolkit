#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP

@post_scan_impl
class PackageSummary(PostScanPlugin):
    """
    Summary at the Package Level.
    """

    options = [
        PluggableCommandLineOption(('--package-summary',),
        is_flag=True, default=False,
        help='Generate Package Level summary',
        help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, package_summary, **kwargs):
        return package_summary

    def process_codebase(self, codebase, package_summary, **kwargs):
        """
        Process the codebase.
        """
        if not self.is_enabled(package_summary):
            return