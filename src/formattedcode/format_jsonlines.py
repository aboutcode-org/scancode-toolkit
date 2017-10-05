#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from plugincode.output import scan_output_writer


"""
Output plugins to write scan results as JSON Lines.
"""


@scan_output_writer
def write_jsonlines(files_count, version, notice, scanned_files, options, output_file, *args, **kwargs):
    """
    Write scan output formatted as JSON Lines.
    """
    header = dict(header=OrderedDict([
        ('scancode_notice', notice),
        ('scancode_version', version),
        ('scancode_options', options),
        ('files_count', files_count)
    ]))

    kwargs = dict(iterable_as_array=True, encoding='utf-8', separators=(',', ':',))

    output_file.write(simplejson.dumps(header, **kwargs))
    output_file.write('\n')

    for scanned_file in scanned_files:
        scanned_file_line = {'files': [scanned_file]}
        output_file.write(simplejson.dumps(scanned_file_line, **kwargs))
        output_file.write('\n')
