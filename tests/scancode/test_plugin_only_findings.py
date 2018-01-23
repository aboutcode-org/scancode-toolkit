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

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode.plugin_only_findings import has_findings
from scancode.resource import Resource


class TestHasFindings(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_has_findings(self):
        resource = Resource('name', 1, 2, 3, use_cache=False)
        resource.put_scans({'licenses': ['MIT']})
        assert has_findings(resource)

    def test_has_findings_with_children(self):
        resource = Resource('name', 1, 2, 3, use_cache=False)
        resource.children_rids.append(1)
        assert not has_findings(resource)

    def test_has_findings_includes_errors(self):
        resource = Resource('name', 1, 2, 3, use_cache=False)
        resource.errors = [
                'ERROR: Processing interrupted: timeout after 10 seconds.'
            ]
        assert has_findings(resource)

    def test_scan_only_findings(self):
        test_dir = self.extract_test_tar('plugin_only_findings/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/expected.json')

        result= run_scan_click(['-clip','--only-findings','--json', result_file,  test_dir])
        print(result.output)
        assert result.exit_code == 0
        
        check_json_scan(expected_file, result_file, strip_dates=True)
