#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import os

from commoncode.testcase import FileBasedTesting

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestMatchCache(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_cache(self):
        raise NotImplementedError()
    """
E             +  '======= MATCH ====================================',
E             +  LicenseMatch<'spl-1.0_6.RULE', u'spl-1.0', score=33.33, qlen=1, ilen=1, rlen=3, qreg=(0, 0), ireg=(1, 1), lines=(0, 0), 'multigram_chunk cached'>,
E             +  '',
E             +  '======= Matched Query Text for: file:///home/pombreda/w421/scancode-toolkit-ref/tests/licensedcode/data/licenses/sun-bcl-sdk-5.0_2.html ==================',
E             +  [],
E             +  '',
E             +  '======= Matched Rule Text for file:///home/pombreda/w421/scancode-toolkit-ref/src/licensedcode/data/rules/spl-1.0_6.RULE',
E             +  ' ============================',
E             +  [u'Public'],
E             +  '',
E             +  '======= MATCH ====================================',
E             +  LicenseMatch<'apache-2.0_1.RULE', u'apache-2.0', score=0.46, qlen=7, ilen=7, rlen=1538, qreg=(0, 20), ireg=(44, 50), lines=(0, 2), 'multigram_chunk cached'>,
E             +  '',
E             +  '======= Matched Query Text for: file:///home/pombreda/w421/scancode-toolkit-ref/tests/licensedcode/data/licenses/sun-bcl-sdk-5.0_2.html ==================',
E             +  [u'<no-match> <no-match> <no-match> <no-match> <no-match> <no-match> 01 <no-match> <no-match> <no-match> <no-match>',
E             +   u'<no-match> <no-match> head meta http <no-match> <no-match> <no-match> content'],
E             +  '',
E             +  '======= Matched Rule Text for file:///home/pombreda/w421/scancode-toolkit-ref/src/licensedcode/data/rules/apache-2.0_1.RULE',
E             +  ' ============================',
E             +  [u'0 license can be found at http']]

    """
