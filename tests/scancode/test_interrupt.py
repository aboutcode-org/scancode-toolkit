#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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

        results = interrupt.interruptible(some_long_function, args=(20,), timeout=0.1)
        expected = 'ERROR: Processing interrupted: timeout after 0 seconds.', None
        assert expected == results

        after = threading.active_count()
        assert before == after

    def test_interruptible_stops_execution_on_exception(self):
        before = threading.active_count()

        def some_crashing_function():
            raise Exception('I have to crash. Now!')

        results, _ = interrupt.interruptible(some_crashing_function, timeout=1.0)
        assert 'ERROR: Unknown error:' in results
        assert 'I have to crash. Now!' in results

        after = threading.active_count()
        assert before == after

    def test_fake_interruptible_stops_execution_on_exception(self):
        def some_crashing_function():
            raise Exception('I have to crash. Now!')

        results, _ = interrupt.fake_interruptible(some_crashing_function, timeout=1.0)
        assert 'ERROR: Unknown error:' in results
        assert 'I have to crash. Now!' in results
