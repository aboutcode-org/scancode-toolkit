#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import json 

from json2xml import json2xml
from json2xml.utils import readfromstring
from formattedcode import FileOptionType
from formattedcode import output_json
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from plugincode.output import output_impl
from plugincode.output import OutputPlugin

"""
Output plugin to write scan results as XML.
"""

@output_impl
class XmlOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--xml', 'output_xml',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output as XML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=20
        ),
    ]

    def is_enabled(self, output_xml, **kwargs):
        return output_xml

    def process_codebase(self, codebase, output_xml, **kwargs):
        results = output_json.get_results(codebase, as_list=True, **kwargs)
        results = json.dumps(results)
        write_xml(results, output_file=output_xml, pretty=True)

def write_xml(results, output_file, **kwargs):
    """
    Write `results` to the `output_file` opened file-like object.
    """
    data = readfromstring(results)
    output_file.write(json2xml.Json2xml(data).to_xml())
    output_file.write('\n')


    