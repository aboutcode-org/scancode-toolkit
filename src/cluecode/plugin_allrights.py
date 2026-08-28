#
# This code is heavily inspired by original code from ScanCode Toolkit.
# The copyright header is therefore propagated. The content is primarily
# taken from following packages in the ScanCode Toolkit:
# - cluecode.plugin_copyright
# - scancode.api
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_GROUP


@scan_impl
class AllrightsCopyrightScanner(ScanPlugin):
    """Scan a Resource for copyrights with all rights reserved. This class is an adapted version of
    scancodes cluecode.plugin_copyright.
    """

    resource_attributes = dict(
        [
            ("copyrights", attr.ib(default=attr.Factory(list))),
            ("holders", attr.ib(default=attr.Factory(list))),
            ("authors", attr.ib(default=attr.Factory(list))),
        ]
    )

    run_order = 6
    sort_order = 6

    options = [
        PluggableCommandLineOption(
            (
                "-a",
                "--allrights",
            ),
            is_flag=True,
            default=False,
            help="Scan <input> for copyrights and all rights reserved.",
            help_group=SCAN_GROUP,
            sort_order=50,
        ),
    ]

    def is_enabled(self, allrights, **kwargs):  # NOQA
        return allrights

    def get_scanner(self, **kwargs):
        from scancode.api import allrights_scanner
        return allrights_scanner

