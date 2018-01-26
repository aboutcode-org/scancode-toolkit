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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from time import sleep
import threading

from commoncode.testcase import FileBasedTesting

from scancode import interrupt

"""
Note that these tests check the active threads count before and after each test to
verify there is no thread leak.
"""


class TestInterrupt(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_interruptible_can_run_function(self):
        before = threading.active_count()

        def some_long_function(exec_time):
            sleep(exec_time)
            return 'OK'

        results = interrupt.interruptible(some_long_function, args=(0.01,), timeout=10)
        expected = None, 'OK'
        assert expected == results

        after = threading.active_count()
        assert before == after

    def test_interruptible_stops_execution_on_timeout(self):
        before = threading.active_count()

        def some_long_function(exec_time):
            for i in range(exec_time):
                sleep(i)
            return 'OK'

        results = interrupt.interruptible(some_long_function, args=(20,), timeout=0.00001)
        expected = 'ERROR: Processing interrupted: timeout after 0 seconds.', None
        assert expected == results

        after = threading.active_count()
        assert before == after
