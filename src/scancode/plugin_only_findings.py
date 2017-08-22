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
def process_only_findings(active_scans, results):
    """
    Only return files or directories with findings for the requested
    scans. Files and directories without findings are omitted (not
    considering basic file information as findings).
    """

    # FIXME: this is forcing all the scan results to be loaded in memory
    # and defeats lazy loading from cache. Only a different caching
    # (e.g. DB) could work here.
    # FIXME: We should instead use a generator or use a filter function
    # that pass to the scan results loader iterator
    for scanned_file in results:
        if has_findings(active_scans, scanned_file):
            yield scanned_file


def has_findings(active_scans, scanned_file):
    """
    Return True if the `scanned_file` has findings for any of the
    `active_scans` names list (excluding basic file information).
    """
    return any(scanned_file.get(scan_name) for scan_name in active_scans)
