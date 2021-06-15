#
# Copyright (c) nexB Inc. and others. All rights reserved.
    # ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import saneyaml

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from formattedcode import FileOptionType
from formattedcode import output_json
from plugincode.output import output_impl
from plugincode.output import OutputPlugin

"""
Output plugin to write scan results as YAML.
"""


@output_impl
class YamlOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--yaml', 'output_yaml',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output as YAML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=20
        ),
    ]

    def is_enabled(self, output_yaml, **kwargs):
        return output_yaml

    def process_codebase(self, codebase, output_yaml, **kwargs):
        results = output_json.get_results(codebase, as_list=True, **kwargs)
        write_yaml(results, output_file=output_yaml, pretty=False)


def write_yaml(results, output_file, **kwargs):
    """
    Write `results` to the `output_file` opened file-like object.
    """
    output_file.write(saneyaml.dump(results, indent=4))
    output_file.write('\n')
