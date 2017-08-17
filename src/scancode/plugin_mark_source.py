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
    Set the "is_source" flag to true for directories that contain
    over 90% of source files as direct children.
    Has no effect unless the --info scan is requested.
    """

    # FIXME: this is forcing all the scan results to be loaded in memory
    # and defeats lazy loading from cache
    results = list(results)

    # FIXME: we should test for active scans instead, but "info" may not
    # be present for now. check if the first item has a file info.
    has_file_info = 'type' in results[0]

    if not has_file_info:
        # just yield results untouched
        for scanned_file in results:
            yield scanned_file
        return

    # FIXME: this is an nested loop, looping twice on results
    # TODO: this may not recusrively roll up the is_source flag, as we
    # may not iterate bottom up.
    for scanned_file in results:
        if scanned_file['type'] == 'directory' and scanned_file['files_count'] > 0:
            source_files_count = 0
            for scanned_file2 in results:
                if path.dirname(scanned_file2['path']) == scanned_file['path']:
                    if scanned_file2['is_source']:
                        source_files_count += 1
            mark_source(source_files_count, scanned_file)
        yield scanned_file


def mark_source(source_files_count, scanned_file):
    """
    Set `is_source` to True for a `scanned_file` directory if
    `source_files_count` is >=90% of files_count for this directory.
    """
    if source_files_count / scanned_file['files_count'] >= 0.9:
        scanned_file['is_source'] = True
