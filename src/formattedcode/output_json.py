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

"""
Output plugins to write scan results as JSON.
"""


@output_impl
class JsonCompactOutput(OutputPlugin):

    options = [
        CommandLineOption(('--json', 'output_json',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as compact JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order= 10),
    ]

    def is_enabled(self):
        return self.is_command_option_enabled('output_json')

    def save_results(self, codebase, results, files_count, version, notice, options):
        output_file = self.get_command_option('output_json').value
        self.create_parent_directory(output_file)
        write_json(results, output_file, files_count, version, notice, options, pretty=False)


@output_impl
class JsonPrettyOutput(OutputPlugin):

    options = [
        CommandLineOption(('--json-pp', 'output_json_pp',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as pretty-printed JSON to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order= 10),
    ]

    def is_enabled(self):
        return self.is_command_option_enabled('output_json_pp')

    def save_results(self, codebase, results, files_count, version, notice, options):
        output_file = self.get_command_option('output_json_pp').value
        self.create_parent_directory(output_file)
        write_json(results, output_file, files_count, version, notice, options, pretty=True)


def write_json(results, output_file, files_count, version, notice, options, pretty=False):
    scan = OrderedDict([
        ('scancode_notice', notice),
        ('scancode_version', version),
        ('scancode_options', options),
        ('files_count', files_count),
        ('files', results),
    ])

    kwargs = dict(iterable_as_array=True, encoding='utf-8')
    if pretty:
        kwargs['indent'] = 2 * b' '
    else:
        kwargs['separators'] = (b',', b':',)

    # FIXME: Why do we wrap the output in unicode? Test output when we do not wrap the output in unicode
    output_file.write(simplejson.dumps(scan, **kwargs))
    output_file.write(b'\n')
