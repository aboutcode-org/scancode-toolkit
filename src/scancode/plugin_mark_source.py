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
from __future__ import division
from __future__ import unicode_literals

from os import path

from plugincode.post_scan import post_scan_impl


@post_scan_impl
def process_mark_source(active_scans, results):
    """
    Set `is_source` to true for all packages with (>=90%) of source files. Has no effect unless --info is requested.
    """

    # FIXME: this is forcing all the scan results to be loaded in memory
    # and defeats lazy loading from cache
    loaded_results = list(results)

    has_file_info = 'type' in loaded_results[0]

    if not has_file_info:
        for scanned_file in loaded_results:
            yield scanned_file
        return

    for scanned_file in loaded_results:
        if scanned_file['type'] == 'directory' and scanned_file['files_count'] > 0:
            source_files_count = 0
            for file in loaded_results:
                if path.dirname(file['path']) == scanned_file['path']:
                    if file['is_source']:
                        source_files_count += 1
            mark_source(source_files_count, scanned_file)
        yield scanned_file

def mark_source(source_files_count, scanned_file):
    """
    Set `is_source` to true for `scanned_file` IFF `source_files_count` is >=90% of files_count.
    """
    if source_files_count / scanned_file['files_count'] >= 0.9:
        scanned_file['is_source'] = True
