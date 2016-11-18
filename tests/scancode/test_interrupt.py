#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from scancode import interrupt


class TestInterrupt(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_megabytes(self):
        assert '12MB' == interrupt.megabytes(12 * 1024 * 1024)
        assert '1MB' == interrupt.megabytes(1 * 1024 * 1024)
        assert '0MB' == interrupt.megabytes(1024)
        assert '11MB' == interrupt.megabytes(11.6 * 1024 * 1024)

    def test_memory_guard(self):
        assert interrupt.MEMORY_EXCEEDED == interrupt.time_and_memory_guard(max_memory=1, timeout=4, interval=2)
        # should fail after 2 seconds
        assert interrupt.RUNTIME_EXCEEDED == interrupt.time_and_memory_guard(max_memory=1024 * 1024 * 1024 * 1024, timeout=2, interval=1)

    def test_interruptible_can_run_function(self):
        from time import sleep

        def some_long_function(exec_time):
            sleep(exec_time)
            return 'OK'

        result = interrupt.interruptible(some_long_function, 0.01, timeout=10, max_memory=1024)
        assert (True, 'OK') == result

    def test_interruptible_stops_execution_on_timeout(self):
        from time import sleep

        def some_long_function(exec_time):
            sleep(exec_time)
            return 'OK'

        result = interrupt.interruptible(some_long_function, 0.5, timeout=0.01)
        assert (False, 'Processing interrupted: timeout after 0 seconds.') == result

    def test_interruptible_stops_execution_on_memory(self):
        from time import sleep

        def some_hungry_function(exec_time):
            sleep(exec_time)
            # consume some memory
            _ram = range(1000000)
            return 'OK'

        success, result = interrupt.interruptible(some_hungry_function, 0.1, timeout=5, max_memory=1)
        assert success == False
        assert 'Processing interrupted: excessive memory usage of more than' in result
