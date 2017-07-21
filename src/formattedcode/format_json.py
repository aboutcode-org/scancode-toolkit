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
Output plugins to write scan results as JSON.
"""

@scan_output_writer
def write_json_compact(files_count, version, notice, scanned_files, options, output_file, *args, **kwargs):
    """
    Write scan output formatted as compact JSON.
    """
    _write_json(files_count, version, notice, scanned_files, options, output_file, pretty=False)


@scan_output_writer
def write_json_pretty_printed(files_count, version, notice, scanned_files, options, output_file, *args, **kwargs):
    """
    Write scan output formatted as pretty-printed JSON.
    """
    _write_json(files_count, version, notice, scanned_files, options, output_file, pretty=True)


def _write_json(files_count, version, notice, scanned_files, options, output_file, pretty=False):
    scan = OrderedDict([
        ('scancode_notice', notice),
        ('scancode_version', version),
        ('scancode_options', options),
        ('files_count', files_count),
        ('files', scanned_files),
    ])
    kwargs = dict(iterable_as_array=True, encoding='utf-8')
    if pretty:
        kwargs['indent'] = 2 * ' '
    else:
        kwargs['separators'] = (',', ':',)

    output_file.write(unicode(simplejson.dumps(scan, **kwargs)))
    output_file.write('\n')
