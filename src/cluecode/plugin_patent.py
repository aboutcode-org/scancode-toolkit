# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from functools import partial
import attr

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OTHER_SCAN_GROUP
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl


@scan_impl
class PatentScanner(ScanPlugin):
    """
    Scan a Resource for patent references and patent numbers.
    """
    resource_attributes = dict(
        patent_detections=attr.ib(default=attr.Factory(list))
    )

    run_order = 8
    sort_order = 8

    options = [
        PluggableCommandLineOption(
            ('--patent',),
            is_flag=True,
            default=False,
            help='Scan <input> for patent references and patent numbers.',
            help_group=OTHER_SCAN_GROUP,
        ),
        PluggableCommandLineOption(
            ('--max-patent',),
            type=int,
            default=50,
            metavar='INT',
            show_default=True,
            required_options=['patent'],
            help='Report only up to INT patent references found in a file. Use 0 for no limit.',
            help_group=SCAN_OPTIONS_GROUP,
        ),
    ]

    def is_enabled(self, patent, **kwargs):
        return patent

    def get_scanner(self, max_patent=50, **kwargs):
        from scancode.api import get_patents
        return partial(
            get_patents,
            threshold=max_patent,
        )
