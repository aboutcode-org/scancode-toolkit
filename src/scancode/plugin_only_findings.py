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

from plugincode.post_scan import post_scan_impl


@post_scan_impl
def process_only_findings(scanners, results):
    """
    Only return files or directories with findings for the requested scans. Files without findings are omitted.
    """
    files_count = 0
    # Find all scans that are both enabled and have a valid function
    # reference. This deliberately filters out the "info" scan
    # (which always has a "None" function reference) as there is no
    # dedicated "infos" key in the results that "has_findings()"
    # could check.
    # FIXME: we should not use positional tings tuples for v[0], v[1] that are mysterious values for now
    active_scans = [k for k, v in scanners.items() if v[0] and v[1]]

    # FIXME: this is forcing all the scan results to be loaded in memory
    # and defeats lazy loading from cache
    # FIXME: we should instead use a generator of use a filter
    # function that pass to the scan results loader iterator
    for file_data in results:
        if has_findings(active_scans, file_data):
            files_count += 1
            yield file_data

def has_findings(active_scans, file_data):
    """
    Return True if the file_data has findings for any of the `active_scans` names list.
    """
    return any(file_data.get(scan_name) for scan_name in active_scans)
