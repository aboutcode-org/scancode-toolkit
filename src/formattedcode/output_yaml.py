#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

import saneyaml
from six import string_types

from commoncode.system import py2
from commoncode.system import py3
from formattedcode import output_json
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP

"""
Output plugin to write scan results as YAML.
"""

if py2:
    mode = 'wb'
    eol = b'\n'

if py3:
    mode = 'w'
    eol = u'\n'


@output_impl
class YamlOutput(OutputPlugin):

    options = [
        CommandLineOption(('--yaml', 'output_yaml',),
            type=FileOptionType(mode=mode, lazy=True),
            metavar='FILE',
            help='Write scan output as YAML to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=20),
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
    close_of = False
    try:
        if isinstance(output_file, string_types):
            output_file = open(output_file, mode)
            close_of = True
        output_file.write(saneyaml.dump(results, indent=4))
        output_file.write(eol)
    finally:
        if close_of:
            output_file.close()
