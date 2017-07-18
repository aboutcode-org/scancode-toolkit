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

from plugincode.scan_output_hooks import scan_output


class Json(object):

    def __init__(self, notice, version, options, files_count, scanned_files):
        self.meta = OrderedDict()
        self.meta['scancode_notice'] = notice
        self.meta['scancode_version'] = version
        self.meta['scancode_options'] = options
        self.meta['files_count'] = files_count
        self.meta['files'] = scanned_files

    @classmethod
    @scan_output
    def write_output(cls, files_count, version, notice, scanned_files, options, input, output_file, _echo):
        meta = cls(notice, version, options, files_count, scanned_files).meta
        output_file.write(unicode(json.dumps(meta, separators=(',', ':'), iterable_as_array=True, encoding='utf-8')))
        output_file.write('\n')


class Json_pp(Json):

    def __init__(self, notice, version, options, files_count, scanned_files):
        super(Json_pp, self).__init__(notice, version, options, files_count, scanned_files)

    @classmethod
    @scan_output
    def write_output(cls, files_count, version, notice, scanned_files, options, input, output_file, _echo):
        meta = cls(notice, version, options, files_count, scanned_files).meta
        output_file.write(unicode(json.dumps(meta, indent=2 * ' ', iterable_as_array=True, encoding='utf-8')))
        output_file.write('\n')
