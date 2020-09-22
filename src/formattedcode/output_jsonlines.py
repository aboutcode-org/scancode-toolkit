#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict

import simplejson

from commoncode.system import py2
from commoncode.system import py3
from formattedcode import FileOptionType
from commoncode.cliutils import OUTPUT_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from plugincode.output import OutputPlugin
from plugincode.output import output_impl

"""
Output plugin to write scan results as JSON lines.
"""


if py2:
    mode = 'wb'
    space = b' '
    comma = b','
    colon = b':'
    eol = b'\n'
    file_key = b'files'

if py3:
    mode = 'w'
    space = u' '
    comma = u','
    colon = u':'
    eol = u'\n'
    file_key = u'files'


@output_impl
class JsonLinesOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--json-lines', 'output_json_lines',),
            type=FileOptionType(mode=mode, lazy=True),
            metavar='FILE',
            help='Write scan output as JSON Lines to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=15),
    ]

    def is_enabled(self, output_json_lines, **kwargs):
        return output_json_lines

    # TODO: reuse the json output code and merge that in a single plugin
    def process_codebase(self, codebase, output_json_lines, **kwargs):
        # NOTE: we write as binary, not text
        files = self.get_files(codebase, **kwargs)

        codebase.add_files_count_to_current_header()

        headers = OrderedDict(headers=codebase.get_headers())

        simplejson_kwargs = dict(
            iterable_as_array=True,
            encoding='utf-8',
            separators=(comma, colon,)
        )
        output_json_lines.write(
            simplejson.dumps(headers, **simplejson_kwargs))
        output_json_lines.write(eol)

        for name, value in codebase.attributes.to_dict().items():
            if value:
                smry = {name: value}
                output_json_lines.write(
                    simplejson.dumps(smry, **simplejson_kwargs))
                output_json_lines.write(eol)

        for scanned_file in files:
            scanned_file_line = {file_key: [scanned_file]}
            output_json_lines.write(
                simplejson.dumps(scanned_file_line, **simplejson_kwargs))
            output_json_lines.write(eol)
