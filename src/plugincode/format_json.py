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
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from collections import OrderedDict

import simplejson as json
from pluggy import HookimplMarker

hookimpl = HookimplMarker('scan_output')

@hookimpl
def add_format():
    return (('json', 'json-pp'), 'format_json')

@hookimpl
def write_output(format, files_count, version, notice, scanned_files, options, input, output_file, _echo):

    meta = OrderedDict()
    meta['scancode_notice'] = notice
    meta['scancode_version'] = version
    meta['scancode_options'] = options
    meta['files_count'] = files_count
    meta['files'] = scanned_files
    if format == 'json-pp':
        output_file.write(unicode(json.dumps(meta, indent=2 * ' ', iterable_as_array=True, encoding='utf-8')))
    else:
        output_file.write(unicode(json.dumps(meta, separators=(',', ':'), iterable_as_array=True, encoding='utf-8')))
    output_file.write('\n')
