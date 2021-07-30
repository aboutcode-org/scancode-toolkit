# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from enum import Enum
from formattedcode import FileOptionType
from plugincode.output import output_impl
from plugincode.output import OutputPlugin


class CycloneDxFlavor(Enum):
    XML = 0
    JSON = 1


"""
Output plugin to write scan results in CycloneDX format.
For additional information on the format, 
please see https://cyclonedx.org/specification/overview/
"""


@output_impl
class CycloneDxOutput(OutputPlugin):
    options = [
        PluggableCommandLineOption(('--cyclonedx', 'output_cyclonedx',),
                                   type=FileOptionType(
                                       mode='w', encoding='utf-8', lazy=True),
                                   metavar='FILE',
                                   help='Write scan output in CycloneDX format to FILE.',
                                   help_group=OUTPUT_GROUP,
                                   sort_order=70),
    ]

    def is_enabled(self, output_cyclonedx, **kwargs):
        return output_cyclonedx

    def process_codebase(self, codebase, output_cyclonedx, **kwargs):
        return super().process_codebase(codebase, output_cyclonedx, **kwargs)


@output_impl
class CycloneDxJsonOutput(OutputPlugin):
    options = [
        PluggableCommandLineOption(('--cyclonedx-json', 'output_cyclonedx_json',),
                                   type=FileOptionType(
                                       mode='w', encoding='utf-8', lazy=True),
                                   metavar='FILE',
                                   help='Write scan output in CycloneDX JSON format to FILE.',
                                   help_group=OUTPUT_GROUP,
                                   sort_order=70),
    ]

    def is_enabled(self, output_cyclonedx_json, **kwargs):
        return output_cyclonedx_json

    def process_codebase(self, codebase, output_cyclonedx_json, **kwargs):
        write_results(codebase, output_file=output_cyclonedx_json,
                      cyclonedx_flavor=CycloneDxFlavor.JSON, **kwargs)
        print(codebase)


def write_results(codebase, output_file, cyclonedx_flavor: CycloneDxFlavor, **kwargs):
    pass
