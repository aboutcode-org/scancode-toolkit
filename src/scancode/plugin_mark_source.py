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

from commoncode.filetype import is_dir
from commoncode.fileutils import file_iter
from plugincode.post_scan import post_scan_impl
from scancode.api import get_file_infos


@post_scan_impl
def process_mark_source(scanners, results, options):
    """
    Set `is_source` to true for all packages with (~90%) of source files
    """
    if not options['--info']:
        return
    for scanned_file in results:
        if is_dir(scanned_file['path']):
            source_files_count = files_count = 0
            for file in file_iter(scanned_file['path']):
                files_count += 1
                if get_file_infos(file)['is_source']:
                    source_files_count += 1
            if files_count == 0:
                continue
            # Check if directory has >=90% of source files
            if source_files_count / files_count >= 0.9:
                scanned_file['is_source'] = True
        yield scanned_file
