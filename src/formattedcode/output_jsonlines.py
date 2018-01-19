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

from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP


@output_impl
class JsonLinesOutput(OutputPlugin):

    options = [
        CommandLineOption(('--json-lines','output_json_lines',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as JSON Lines to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order= 15),
    ]

    def is_enabled(self):
        return self.is_command_option_enabled('output_json_lines')

    def save_results(self, codebase, results, files_count, version, notice, options):
        output_file = self.get_command_option('output_json_lines').value
        self.create_parent_directory(output_file)
        header = dict(header=OrderedDict([
            ('scancode_notice', notice),
            ('scancode_version', version),
            ('scancode_options', options),
            ('files_count', files_count)
        ]))

        kwargs = dict(
            iterable_as_array=True, encoding='utf-8', separators=(',', ':',))
        output_file.write(simplejson.dumps(header, **kwargs))
        output_file.write('\n')

        for scanned_file in results:
            scanned_file_line = {'files': [scanned_file]}
            output_file.write(simplejson.dumps(scanned_file_line, **kwargs))
            output_file.write('\n')
