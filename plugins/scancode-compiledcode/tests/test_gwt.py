#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import json
import os

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from commoncode.testcase import FileBasedTesting


class TestScanPluginGWTScan(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    def test_gwt_scan(self):
        test_dir = self.get_test_loc('gwt')
        result_file = self.get_temp_file('json')
        args = ['--gwt', test_dir, '--json', result_file]
        run_scan_click(args)
        test_loc = self.get_test_loc('gwt/expected.json')
        check_json_scan(test_loc, result_file, regen=False)

